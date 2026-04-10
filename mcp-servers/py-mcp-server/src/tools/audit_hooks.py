"""
Audit Hooks — Mandatory forensic auditing for all identification tools.

Every tool MUST use the @audit_tool decorator. This ensures:
1. SHA-256 hashing of inputs BEFORE processing
2. UUIDv7 generation for audit trail
3. Logging to app.audit_log table
4. W3C PROV-O provenance tracking via Semantica
5. SHA-256 hashing of outputs AFTER processing
6. Graceful but LOUD error handling (never crash, always report)

GRACEFUL BUT LOUD:
- Errors never crash the tool — always return structured error response
- Errors are ALWAYS logged to console (logger.error)
- Errors ALWAYS written to audit log
- Errors ALWAYS include: tool name, input hash, error message, timestamp
- Errors are returned in response JSON with "error" field — caller sees them
"""

import hashlib
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger("dial-py-mcp-audit")

# ---------------------------------------------------------------------------
# Database Connection (lazy)
# ---------------------------------------------------------------------------

_pg_pool = None


def _get_pg_connection():
    """Get PostgreSQL connection for audit logging."""
    global _pg_pool
    if _pg_pool is None:
        try:
            import psycopg2

            _pg_pool = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "postgres"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                dbname=os.getenv("POSTGRES_DB", "dial"),
                user=os.getenv("POSTGRES_USER", "dial"),
                password=os.getenv("POSTGRES_PASSWORD", "dial"),
            )
            logger.info("[Audit] PostgreSQL connection established for audit logging")
        except Exception as e:
            logger.error(
                f"[Audit] FAILED to connect to PostgreSQL for audit logging: {e}"
            )
            # LOUD but graceful — don't crash, just log
            _pg_pool = False  # Mark as failed so we don't retry every call
    return _pg_pool if _pg_pool and _pg_pool is not False else None


# ---------------------------------------------------------------------------
# Hash Functions
# ---------------------------------------------------------------------------


def hash_sha256(data: Any) -> str:
    """Generate SHA-256 hash of any data (string, dict, bytes)."""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def generate_uuidv7() -> str:
    """Generate UUIDv7 (timestamp-sortable)."""
    # UUIDv7: timestamp-based, sortable
    import time

    ts_ms = int(time.time() * 1000)
    # Use uuidv7 package if available, fallback to manual
    try:
        from uuid_extensions import uuid7

        return str(uuid7())
    except ImportError:
        # Manual UUIDv7 construction
        ts_bytes = ts_ms.to_bytes(6, "big")
        random_bytes = os.urandom(10)
        uuid_bytes = ts_bytes + random_bytes
        # Set version (7) and variant bits
        uuid_bytes = bytearray(uuid_bytes)
        uuid_bytes[6] = (uuid_bytes[6] & 0x0F) | 0x70  # version 7
        uuid_bytes[8] = (uuid_bytes[8] & 0x3F) | 0x80  # variant RFC 4122
        return str(uuid.UUID(bytes=bytes(uuid_bytes)))


# ---------------------------------------------------------------------------
# Audit Logging
# ---------------------------------------------------------------------------


def write_audit_log(
    tool_name: str,
    input_hash: str,
    output_hash: Optional[str],
    status: str,
    duration_ms: int,
    error_message: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Optional[str]:
    """
    Write audit record to app.audit_log table.

    Returns audit_id if successful, None if DB unavailable.
    NEVER raises — errors are logged loudly but don't crash.
    """
    audit_id = generate_uuidv7()

    conn = _get_pg_connection()
    if conn is None:
        # LOUD: Log to console even if DB unavailable
        logger.error(
            f"[AUDIT] DB UNAVAILABLE — audit record NOT persisted to database! "
            f"tool={tool_name} input_hash={input_hash} status={status} "
            f"audit_id={audit_id} error={error_message}"
        )
        return audit_id  # Return ID anyway so tool can continue

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO app.audit_log 
                (id, logged_at, deployment, model, user_sub, request_id,
                 req_messages, req_tools, resp_status, resp_model, duration_ms, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    audit_id,
                    datetime.now(timezone.utc),
                    "py-mcp-server",
                    tool_name,
                    "system",  # TODO: Get actual user from auth context
                    input_hash,
                    json.dumps({"input_hash": input_hash, "metadata": metadata or {}}),
                    json.dumps([tool_name]),
                    200 if status == "success" else 500,
                    tool_name,
                    duration_ms,
                    error_message,
                ),
            )
        conn.commit()
        logger.info(
            f"[AUDIT] Logged: {tool_name} → {audit_id} ({status}, {duration_ms}ms)"
        )
    except Exception as e:
        # LOUD: Log error but don't crash
        logger.error(
            f"[AUDIT] FAILED to write audit log: {e} "
            f"tool={tool_name} input_hash={input_hash} status={status}"
        )
        try:
            conn.rollback()
        except:
            pass

    return audit_id


def write_provenance(
    source_hash: str,
    timestamp: str,
    tool_name: str,
    operation: str,
) -> Optional[dict]:
    """
    Write W3C PROV-O provenance record via Semantica.

    NEVER raises — errors are logged loudly but don't crash.
    """
    try:
        # Call semantica_track_provenance if available
        # This is a best-effort call — if it fails, we log loudly but continue
        from semantica.provenance import ProvenanceTracker

        tracker = ProvenanceTracker()
        provenance = tracker.create_provenance(
            source_hash=source_hash,
            timestamp=timestamp,
            platform=tool_name,
            sender=operation,
        )
        logger.info(f"[PROV] Recorded: {tool_name}/{operation} → {source_hash[:16]}...")
        return provenance
    except Exception as e:
        # LOUD: Log error but don't crash
        logger.error(
            f"[PROV] FAILED to write provenance: {e} "
            f"tool={tool_name} operation={operation} hash={source_hash[:16]}..."
        )
        return None


def write_tool_execution_log(
    tool_name: str,
    server: str,
    started_at: float,
    input_hash: str,
    input_summary: str,
    output_hash: Optional[str],
    output_summary: Optional[str],
    status: str,
    duration_ms: int,
    tables_read: Optional[list] = None,
    tables_written: Optional[list] = None,
    files_read: Optional[list] = None,
    files_written: Optional[list] = None,
    input_message_ids: Optional[list] = None,
    result_score: Optional[float] = None,
    result_category: Optional[str] = None,
    result_entities_found: int = 0,
    error_message: Optional[str] = None,
    error_traceback: Optional[str] = None,
    source_hash: Optional[str] = None,
    parent_execution_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Optional[str]:
    """
    Write to evidence.tool_execution_log — the single source of truth for all tool execution.

    Logs EVERYTHING:
    - What tool ran, when, how long
    - What it touched (tables read/written, files read/written)
    - What it produced (output hash, summary, scores, entities found)
    - What messages it operated on
    - Errors with full traceback

    NEVER raises — errors are logged loudly but don't crash.
    """
    execution_id = generate_uuidv7()

    conn = _get_pg_connection()
    if conn is None:
        logger.error(
            f"[EXEC-LOG] DB UNAVAILABLE — execution NOT logged! "
            f"tool={tool_name} input={input_hash[:16]}... status={status}"
        )
        return execution_id

    try:
        from datetime import datetime, timezone

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO evidence.tool_execution_log
                (id, tool_name, server, started_at, completed_at, duration_ms,
                 input_hash, input_summary, input_message_ids,
                 output_hash, output_summary,
                 tables_read, tables_written, files_read, files_written,
                 status, error_message, error_traceback,
                 result_score, result_category, result_entities_found,
                 source_hash, parent_execution_id, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    execution_id,
                    tool_name,
                    server,
                    datetime.fromtimestamp(started_at, tz=timezone.utc),
                    datetime.now(timezone.utc),
                    duration_ms,
                    input_hash,
                    input_summary[:500] if input_summary else None,
                    input_message_ids or [],
                    output_hash,
                    output_summary[:500] if output_summary else None,
                    tables_read or [],
                    tables_written or [],
                    files_read or [],
                    files_written or [],
                    status,
                    error_message,
                    error_traceback,
                    result_score,
                    result_category,
                    result_entities_found,
                    source_hash,
                    parent_execution_id,
                    json.dumps(metadata) if metadata else None,
                ),
            )
        conn.commit()

        # LOUD: Always log to console
        icon = "✅" if status == "success" else "❌"
        logger.info(
            f"{icon} [EXEC] {tool_name} | {status} | {duration_ms}ms | "
            f"tables_r={tables_read or []} tables_w={tables_written or []} | "
            f"entities={result_entities_found} | hash={input_hash[:16]}..."
        )

    except Exception as e:
        logger.error(
            f"[EXEC-LOG] FAILED to write execution log: {e} "
            f"tool={tool_name} input={input_hash[:16]}..."
        )
        try:
            conn.rollback()
        except:
            pass

    return execution_id


def write_hash_audit(
    input_hash: str,
    output_hash: str,
    tool_name: str,
    status: str,
    details: Optional[dict] = None,
) -> None:
    """
    Write to evidence.hash_audit table.

    NEVER raises — errors are logged loudly but don't crash.
    """
    conn = _get_pg_connection()
    if conn is None:
        logger.error(
            f"[HASH-AUDIT] DB UNAVAILABLE — hash audit NOT persisted! "
            f"tool={tool_name} input={input_hash[:16]}... output={output_hash[:16]}..."
        )
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO evidence.hash_audit (message_count, status, details)
                VALUES (%s, %s, %s)
            """,
                (
                    1,
                    status,
                    json.dumps(
                        {
                            "tool": tool_name,
                            "input_hash": input_hash,
                            "output_hash": output_hash,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            **(details or {}),
                        }
                    ),
                ),
            )
        conn.commit()
    except Exception as e:
        logger.error(
            f"[HASH-AUDIT] FAILED to write hash audit: {e} "
            f"tool={tool_name} input={input_hash[:16]}..."
        )
        try:
            conn.rollback()
        except:
            pass


# ---------------------------------------------------------------------------
# Audit Decorator (MANDATORY for all tools)
# ---------------------------------------------------------------------------


def audit_tool(tool_name: str):
    """
    Decorator that adds mandatory forensic auditing to any tool.

    Usage:
        @audit_tool("dpk_hap_score")
        def dpk_hap_score(text: str, mode: str = "pass1") -> str:
            ...

    What it does:
    1. Hashes input (SHA-256) BEFORE calling the tool
    2. Calls the tool
    3. Hashes output (SHA-256) AFTER tool completes
    4. Writes to app.audit_log
    5. Writes to evidence.hash_audit
    6. Writes W3C PROV-O provenance (best-effort)
    7. On error: logs LOUDLY, returns structured error, never crashes
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            input_hash = None
            output_hash = None
            status = "success"
            error_message = None
            result = None

            try:
                # 1. Hash input
                input_data = {"args": str(args), "kwargs": str(kwargs)}
                input_hash = hash_sha256(input_data)

                # 2. Call the actual tool
                result = func(*args, **kwargs)

                # 3. Hash output
                output_hash = hash_sha256(result)

                # 4. Write hash audit
                write_hash_audit(input_hash, output_hash, tool_name, "success")

                # 5. Write provenance (best-effort)
                write_provenance(
                    source_hash=input_hash,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    tool_name=tool_name,
                    operation="analysis",
                )

            except Exception as e:
                # GRACEFUL BUT LOUD
                status = "error"
                error_message = f"{type(e).__name__}: {str(e)}"

                # LOUD: Log to console
                logger.error(
                    f"\n{'=' * 60}\n"
                    f"[TOOL ERROR] {tool_name} FAILED\n"
                    f"  Error: {error_message}\n"
                    f"  Input hash: {input_hash}\n"
                    f"  Timestamp: {datetime.now(timezone.utc).isoformat()}\n"
                    f"{'=' * 60}\n"
                )

                # Return structured error (graceful)
                result = json.dumps(
                    {
                        "error": error_message,
                        "tool": tool_name,
                        "input_hash": input_hash,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "error",
                    }
                )

                # Write error to hash audit
                if input_hash:
                    write_hash_audit(
                        input_hash,
                        hash_sha256(result),
                        tool_name,
                        "error",
                        {"error": error_message},
                    )

            finally:
                # 6. ALWAYS write audit log (success or error)
                duration_ms = int((time.time() - start) * 1000)
                write_audit_log(
                    tool_name=tool_name,
                    input_hash=input_hash or "unknown",
                    output_hash=output_hash,
                    status=status,
                    duration_ms=duration_ms,
                    error_message=error_message,
                )

                # 7. ALWAYS write tool execution log (the full record)
                # Extract result metadata if available
                result_score = None
                result_category = None
                result_entities_found = 0
                output_summary = None
                tables_read = []
                tables_written = []

                if result and status == "success":
                    try:
                        parsed = (
                            json.loads(result) if isinstance(result, str) else result
                        )
                        # Extract score if present
                        result_score = (
                            parsed.get("score")
                            or parsed.get("hap_score")
                            or parsed.get("darvo_score")
                        )
                        # Extract category if present
                        cats = parsed.get("categories", [])
                        result_category = (
                            cats[0]
                            if cats
                            else parsed.get("language")
                            or parsed.get("role_classification")
                        )
                        # Count entities/items found
                        if "detected_pii" in parsed:
                            result_entities_found = len(parsed["detected_pii"])
                        elif "sentence_scores" in parsed:
                            result_entities_found = len(parsed["sentence_scores"])
                        # Output summary
                        output_summary = json.dumps(parsed)[:500]
                    except:
                        output_summary = str(result)[:500]

                # Determine which tables this tool touches based on tool name
                if (
                    "hap" in tool_name
                    or "pii" in tool_name
                    or "lang" in tool_name
                    or "quality" in tool_name
                    or "readability" in tool_name
                ):
                    tables_written = ["evidence.message_analysis"]
                elif (
                    "behavioral" in tool_name
                    or "darvo" in tool_name
                    or "coercive" in tool_name
                ):
                    tables_read = ["app.behavioral_patterns", "app.mcl_factors"]
                    tables_written = [
                        "evidence.message_analysis",
                        "evidence.behavioral_findings",
                    ]
                elif "semantica" in tool_name:
                    tables_read = ["evidence.messages"]
                    tables_written = ["neo4j:evidence_graph", "lancedb:vectors"]
                elif "voice" in tool_name or "fingerprint" in tool_name:
                    tables_written = ["evidence.message_analysis"]

                write_tool_execution_log(
                    tool_name=tool_name,
                    server="py-mcp-server",
                    started_at=start,
                    input_hash=input_hash or "unknown",
                    input_summary=str(args)[:200] if args else str(kwargs)[:200],
                    output_hash=output_hash,
                    output_summary=output_summary,
                    status=status,
                    duration_ms=duration_ms,
                    tables_read=tables_read,
                    tables_written=tables_written,
                    result_score=result_score,
                    result_category=result_category,
                    result_entities_found=result_entities_found,
                    error_message=error_message,
                    error_traceback=None,  # TODO: capture traceback on error
                )

            return result

        return wrapper

    return decorator
