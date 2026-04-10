"""
AI DIAL Audit Logger Interceptor
=================================
A DIAL Core interceptor that logs every request and response to PostgreSQL.

DIAL Core calls interceptors as middleware before/after routing to the model.
The interceptor pattern here is a plain FastAPI ASGI app that:
  1. Receives the full request body from DIAL Core
  2. Forwards it upstream to the real model endpoint
  3. Collects the complete response (streamed or non-streamed)
  4. Persists both request + response to app.audit_log in PostgreSQL
  5. Returns the original response to the client unchanged

References:
  - https://github.com/epam/ai-dial-core/blob/main/docs/interceptors.md
  - The interceptor receives requests via POST /openai/deployments/{id}/chat/completions
  - x-upstream-endpoint header tells us where to forward the request
"""

import json
import os
import time
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import AsyncIterator

import httpx
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("audit-logger")

# ---------------------------------------------------------------------------
# Database — lazy connection pool
# ---------------------------------------------------------------------------
_pg_conn = None

def get_pg():
    global _pg_conn
    if _pg_conn is None or _pg_conn.closed:
        _pg_conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            dbname=os.getenv("POSTGRES_DB", "dial"),
            user=os.getenv("POSTGRES_USER", "dial"),
            password=os.getenv("POSTGRES_PASSWORD", "dial_password"),
        )
        _pg_conn.autocommit = True
        _ensure_audit_table(_pg_conn)
    return _pg_conn


def _ensure_audit_table(conn):
    """Create audit_log table if it doesn't exist yet."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app.audit_log (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                logged_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                deployment  TEXT,
                model       TEXT,
                user_sub    TEXT,
                request_id  TEXT,
                -- Request fields
                req_messages    JSONB,
                req_tools       JSONB,
                req_stream      BOOLEAN,
                req_temperature FLOAT,
                -- Response fields
                resp_status     INT,
                resp_choices    JSONB,
                resp_usage      JSONB,
                resp_model      TEXT,
                duration_ms     INT,
                -- Error tracking
                error_message   TEXT
            )
        """)
    log.info("audit_log table ready")


def _write_audit_row(row: dict):
    """Insert an audit row. Silently logs DB errors so they never break the proxy."""
    try:
        conn = get_pg()
        with conn.cursor() as cur:
            cols = ", ".join(row.keys())
            placeholders = ", ".join(["%s"] * len(row))
            cur.execute(
                f"INSERT INTO app.audit_log ({cols}) VALUES ({placeholders})",
                list(row.values()),
            )
    except Exception as e:
        log.error(f"Failed to write audit row: {e}")


# ---------------------------------------------------------------------------
# HTTP client — reuse connections
# ---------------------------------------------------------------------------
_http_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=120.0)
    return _http_client


# ---------------------------------------------------------------------------
# Response collation helpers
# ---------------------------------------------------------------------------

async def _collect_stream(
    response: httpx.Response,
) -> tuple[list[bytes], dict | None]:
    """
    Drains a streaming SSE response, returns:
      - raw_chunks: the original bytes to replay to the client
      - merged: best-effort merged JSON of the final chunk (for logging)
    """
    raw_chunks: list[bytes] = []
    last_data: dict | None = None

    async for line in response.aiter_lines():
        encoded = (line + "\n").encode()
        raw_chunks.append(encoded)
        if line.startswith("data: ") and line != "data: [DONE]":
            try:
                last_data = json.loads(line[6:])
            except Exception:
                pass

    return raw_chunks, last_data


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="DIAL Audit Logger", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "audit-logger"}


@app.post("/openai/deployments/{deployment_id:path}/chat/completions")
async def intercept_chat_completion(deployment_id: str, request: Request):
    start_ms = int(time.monotonic() * 1000)
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))

    # ------------------------------------------------------------------
    # 1. Parse and log the incoming request
    # ------------------------------------------------------------------
    raw_body = await request.body()
    try:
        req_json = json.loads(raw_body)
    except Exception:
        req_json = {}

    audit_row = {
        "deployment": deployment_id,
        "request_id": request_id,
        "user_sub": request.headers.get("x-user-sub"),
        "req_messages": json.dumps(req_json.get("messages", [])),
        "req_tools": json.dumps(req_json.get("tools")) if req_json.get("tools") else None,
        "req_stream": req_json.get("stream", False),
        "req_temperature": req_json.get("temperature"),
    }

    # ------------------------------------------------------------------
    # 2. Forward to upstream model
    #    DIAL Core sets x-upstream-endpoint so interceptors know where to proxy.
    # ------------------------------------------------------------------
    upstream_url = request.headers.get("x-upstream-endpoint")
    if not upstream_url:
        # Fallback: proxy to DIAL Core itself (it will route to the model)
        dial_core_url = os.getenv("DIAL_CORE_URL", "http://core:8080")
        upstream_url = f"{dial_core_url}/openai/deployments/{deployment_id}/chat/completions"

    forward_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length", "transfer-encoding")
    }

    client = get_http_client()
    error_message: str | None = None

    try:
        upstream_resp = await client.post(
            upstream_url,
            content=raw_body,
            headers=forward_headers,
        )

        resp_status = upstream_resp.status_code
        is_stream = "text/event-stream" in upstream_resp.headers.get("content-type", "")

        if is_stream:
            # Collect stream, then replay it
            raw_chunks, last_chunk = await _collect_stream(upstream_resp)
            duration_ms = int(time.monotonic() * 1000) - start_ms

            choices = last_chunk.get("choices") if last_chunk else None
            usage = last_chunk.get("usage") if last_chunk else None
            resp_model = last_chunk.get("model") if last_chunk else None

            audit_row.update({
                "resp_status": resp_status,
                "resp_choices": json.dumps(choices) if choices else None,
                "resp_usage": json.dumps(usage) if usage else None,
                "resp_model": resp_model,
                "duration_ms": duration_ms,
            })
            _write_audit_row(audit_row)

            async def replay() -> AsyncIterator[bytes]:
                for chunk in raw_chunks:
                    yield chunk

            return StreamingResponse(
                replay(),
                status_code=resp_status,
                media_type="text/event-stream",
                headers={
                    k: v for k, v in upstream_resp.headers.items()
                    if k.lower() not in ("transfer-encoding",)
                },
            )

        else:
            # Non-streaming: read full body
            resp_body = upstream_resp.content
            duration_ms = int(time.monotonic() * 1000) - start_ms

            try:
                resp_json = json.loads(resp_body)
            except Exception:
                resp_json = {}

            audit_row.update({
                "resp_status": resp_status,
                "resp_choices": json.dumps(resp_json.get("choices")) if resp_json.get("choices") else None,
                "resp_usage": json.dumps(resp_json.get("usage")) if resp_json.get("usage") else None,
                "resp_model": resp_json.get("model"),
                "duration_ms": duration_ms,
            })
            _write_audit_row(audit_row)

            return Response(
                content=resp_body,
                status_code=resp_status,
                media_type=upstream_resp.headers.get("content-type", "application/json"),
                headers={
                    k: v for k, v in upstream_resp.headers.items()
                    if k.lower() not in ("transfer-encoding",)
                },
            )

    except Exception as exc:
        error_message = str(exc)
        log.error(f"Upstream proxy error: {exc}")
        duration_ms = int(time.monotonic() * 1000) - start_ms
        audit_row.update({
            "resp_status": 502,
            "duration_ms": duration_ms,
            "error_message": error_message,
        })
        _write_audit_row(audit_row)

        return Response(
            content=json.dumps({"error": {"message": f"Interceptor proxy error: error_message", "type": "proxy_error"}}),
            status_code=502,
            media_type="application/json",
        )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8085"))
    log.info(f"Starting audit-logger on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
