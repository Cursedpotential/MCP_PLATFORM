"""
AI DIAL Python MCP Server — Semantica, LanceDB & Neo4j Tools

Exposes atomic NLP, vector search, and knowledge graph operations as MCP tools.
Ported from legacy memory_service.py (FastAPI) → FastMCP atomic tools.

Architecture:
  - Semantica: NER extraction, relation building, temporal facts, conflict detection,
               embedding generation, W3C PROV-O provenance tracking
  - LanceDB:   Vector similarity search and upsert
  - Neo4j:     Cypher queries and entity timeline traversal
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DB = os.getenv("NEO4J_DATABASE", "neo4j")

LANCEDB_PATH = os.getenv("LANCEDB_PATH", "/data/lancedb")

SEMANTICA_NER_MODEL = os.getenv("SEMANTICA_NER_MODEL", "en_core_web_sm")
SEMANTICA_EMBEDDING_MODEL = os.getenv("SEMANTICA_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dial-py-mcp")

# ---------------------------------------------------------------------------
# FastMCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "dial-py-core",
    description="AI DIAL Semantica Knowledge Graph & Vector Tools",
)

# ---------------------------------------------------------------------------
# Lazy Service Singletons
# ---------------------------------------------------------------------------
# We use lazy initialization so the server can start even if dependencies
# aren't available yet — tools will report clear errors when invoked.

_neo4j_driver = None
_lancedb_conn = None
_ner_extractor = None
_graph_builder = None
_temporal_query = None
_conflict_detector = None
_embedding_generator = None
_provenance_tracker = None


def _get_neo4j():
    global _neo4j_driver
    if _neo4j_driver is None:
        from neo4j import GraphDatabase

        _neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        logger.info(f"[Neo4j] Connected to {NEO4J_URI}")
    return _neo4j_driver


def _get_lancedb():
    global _lancedb_conn
    if _lancedb_conn is None:
        import lancedb

        _lancedb_conn = lancedb.connect(LANCEDB_PATH)
        logger.info(f"[LanceDB] Connected to {LANCEDB_PATH}")
    return _lancedb_conn


def _get_ner():
    global _ner_extractor
    if _ner_extractor is None:
        from semantica.semantic_extract import NERExtractor

        _ner_extractor = NERExtractor(model_name=SEMANTICA_NER_MODEL)
        logger.info(f"[Semantica] NER loaded ({SEMANTICA_NER_MODEL})")
    return _ner_extractor


def _get_graph_builder():
    global _graph_builder
    if _graph_builder is None:
        from semantica.kg import GraphBuilder

        _graph_builder = GraphBuilder()
        logger.info("[Semantica] GraphBuilder initialized")
    return _graph_builder


def _get_temporal_query():
    global _temporal_query
    if _temporal_query is None:
        from semantica.temporal import TemporalGraphQuery

        _temporal_query = TemporalGraphQuery()
        logger.info("[Semantica] TemporalGraphQuery initialized")
    return _temporal_query


def _get_conflict_detector():
    global _conflict_detector
    if _conflict_detector is None:
        from semantica.conflicts import ConflictDetector

        _conflict_detector = ConflictDetector()
        logger.info("[Semantica] ConflictDetector initialized")
    return _conflict_detector


def _get_embedding_generator():
    global _embedding_generator
    if _embedding_generator is None:
        from semantica.embeddings import EmbeddingGenerator

        _embedding_generator = EmbeddingGenerator(model_name=SEMANTICA_EMBEDDING_MODEL)
        logger.info(
            f"[Semantica] EmbeddingGenerator loaded ({SEMANTICA_EMBEDDING_MODEL})"
        )
    return _embedding_generator


def _get_provenance_tracker():
    global _provenance_tracker
    if _provenance_tracker is None:
        from semantica.provenance import ProvenanceTracker

        _provenance_tracker = ProvenanceTracker()
        logger.info("[Semantica] ProvenanceTracker initialized")
    return _provenance_tracker


# ===========================================================================
# Tool: Ping / Health
# ===========================================================================


@mcp.tool()
def ping() -> str:
    """Ping the Python MCP server to verify it is running within DIAL."""
    checks = {
        "server": True,
        "neo4j": False,
        "lancedb": False,
        "semantica": False,
    }
    try:
        driver = _get_neo4j()
        with driver.session(database=NEO4J_DB) as session:
            session.run("RETURN 1").single()
        checks["neo4j"] = True
    except Exception as e:
        checks["neo4j_error"] = str(e)

    try:
        _get_lancedb()
        checks["lancedb"] = True
    except Exception as e:
        checks["lancedb_error"] = str(e)

    try:
        _get_ner()
        checks["semantica"] = True
    except Exception as e:
        checks["semantica_error"] = str(e)

    return json.dumps(checks, indent=2)


# ===========================================================================
# Tools: Semantica NLP Pipeline
# ===========================================================================


@mcp.tool()
def semantica_extract_entities(text: str) -> str:
    """
    Extract named entities from text using Semantica NER.

    Args:
        text: The text to extract entities from.

    Returns:
        JSON array of entities with text, type, and confidence.
    """
    extractor = _get_ner()
    entities = extractor.extract(text)
    return json.dumps(entities, indent=2, default=str)


@mcp.tool()
def semantica_build_graph(
    text: str, entities_json: str, metadata_json: Optional[str] = None
) -> str:
    """
    Build relation graph from text and pre-extracted entities.

    Args:
        text: Original text.
        entities_json: JSON array of entities (from semantica_extract_entities).
        metadata_json: Optional JSON object of additional metadata.

    Returns:
        JSON array of relations with subject, predicate, object, confidence.
    """
    builder = _get_graph_builder()
    entities = json.loads(entities_json)
    metadata = json.loads(metadata_json) if metadata_json else {}
    relations = builder.extract_relations(text, entities, metadata=metadata)
    return json.dumps(relations, indent=2, default=str)


@mcp.tool()
def semantica_extract_temporal_facts(
    entities_json: str,
    relations_json: str,
    timestamp: str,
) -> str:
    """
    Extract temporal facts from entities and relations at a given timestamp.

    Args:
        entities_json: JSON array of entities.
        relations_json: JSON array of relations.
        timestamp: ISO 8601 timestamp for the evidence.

    Returns:
        JSON array of temporal facts with entity, attribute, value, valid_from.
    """
    tq = _get_temporal_query()
    entities = json.loads(entities_json)
    relations = json.loads(relations_json)
    facts = tq.build_facts(entities, relations, timestamp=timestamp)
    return json.dumps(facts, indent=2, default=str)


@mcp.tool()
async def semantica_detect_conflicts(entities_json: str, text: str) -> str:
    """
    Detect contradictions between new entities/text and existing graph knowledge.

    Args:
        entities_json: JSON array of entities from the new evidence.
        text: The new text being evaluated.

    Returns:
        JSON array of conflicts with entity, attribute, old_value, new_value.
    """
    detector = _get_conflict_detector()
    entities = json.loads(entities_json)
    driver = _get_neo4j()
    conflicts = await detector.detect(entities, text, neo4j_driver=driver)
    return json.dumps(conflicts, indent=2, default=str)


@mcp.tool()
def semantica_generate_embeddings(text: str) -> str:
    """
    Generate a 768-dimensional vector embedding for the given text.

    Args:
        text: Text to embed.

    Returns:
        JSON object with the embedding vector and dimension count.
    """
    gen = _get_embedding_generator()
    embedding = gen.generate(text)
    return json.dumps(
        {
            "embedding": embedding
            if isinstance(embedding, list)
            else embedding.tolist(),
            "dimensions": len(embedding),
        }
    )


@mcp.tool()
def semantica_track_provenance(
    source_hash: str,
    timestamp: str,
    platform: str,
    sender: Optional[str] = None,
    recipient: Optional[str] = None,
) -> str:
    """
    Create a W3C PROV-O provenance record for a piece of evidence.

    Args:
        source_hash: SHA-256 hash from DuckDB forensic vault.
        timestamp: ISO 8601 timestamp of the evidence.
        platform: Platform origin (sms, imessage, facebook, whatsapp, email).
        sender: Optional sender identifier.
        recipient: Optional recipient identifier.

    Returns:
        JSON provenance record.
    """
    tracker = _get_provenance_tracker()
    provenance = tracker.create_provenance(
        source_hash=source_hash,
        timestamp=timestamp,
        platform=platform,
        sender=sender,
        recipient=recipient,
    )
    return json.dumps(provenance, indent=2, default=str)


# ===========================================================================
# Tools: LanceDB Vector Search
# ===========================================================================


@mcp.tool()
def lancedb_vector_search(
    collection: str,
    query_text: str,
    top_k: int = 10,
) -> str:
    """
    Perform semantic vector search in a LanceDB collection.

    Args:
        collection: Name of the LanceDB collection/table.
        query_text: Text query — will be embedded and searched by similarity.
        top_k: Number of results to return (default: 10).

    Returns:
        JSON array of the top-k most similar records with distance scores.
    """
    db = _get_lancedb()
    gen = _get_embedding_generator()

    try:
        table = db.open_table(collection)
    except Exception:
        return json.dumps({"error": f"Collection '{collection}' not found."})

    query_embedding = gen.generate(query_text)
    if not isinstance(query_embedding, list):
        query_embedding = query_embedding.tolist()

    results = table.search(query_embedding).limit(top_k).to_pandas()
    return results.to_json(orient="records", indent=2, default_handler=str)


@mcp.tool()
def lancedb_upsert(
    collection: str,
    records_json: str,
) -> str:
    """
    Upsert records with pre-computed vectors into a LanceDB collection.

    Args:
        collection: Name of the LanceDB collection/table.
        records_json: JSON array of records. Each record MUST have a 'vector' field.

    Returns:
        Confirmation with row count.
    """
    import pyarrow as pa

    db = _get_lancedb()
    records = json.loads(records_json)

    try:
        table = db.open_table(collection)
        table.add(records)
    except Exception:
        # Table doesn't exist; create it
        table = db.create_table(collection, records)

    return json.dumps(
        {
            "success": True,
            "collection": collection,
            "rows_written": len(records),
        }
    )


@mcp.tool()
def lancedb_list_collections() -> str:
    """List all LanceDB collections/tables available."""
    db = _get_lancedb()
    tables = db.table_names()
    return json.dumps({"collections": list(tables)})


# ===========================================================================
# Tools: Neo4j Knowledge Graph
# ===========================================================================


@mcp.tool()
def neo4j_cypher_query(cypher: str, params_json: Optional[str] = None) -> str:
    """
    Execute an arbitrary Cypher query against the Neo4j knowledge graph.

    Args:
        cypher: Cypher query string.
        params_json: Optional JSON object of query parameters.

    Returns:
        JSON array of result records.
    """
    driver = _get_neo4j()
    params = json.loads(params_json) if params_json else {}

    with driver.session(database=NEO4J_DB) as session:
        result = session.run(cypher, **params)
        records = [dict(record) for record in result]

    return json.dumps(records, indent=2, default=str)


@mcp.tool()
def neo4j_get_entity_timeline(entity_text: str, limit: int = 100) -> str:
    """
    Get a chronological timeline of events involving a specific entity.

    Args:
        entity_text: The entity name/text to search for.
        limit: Maximum number of timeline events (default: 100).

    Returns:
        JSON array of timeline events with timestamp, platform, content, source_hash.
    """
    driver = _get_neo4j()

    with driver.session(database=NEO4J_DB) as session:
        result = session.run(
            """
            MATCH (e:Entity {text: $text})
            MATCH (m:Message)-[:MENTIONS]->(e)
            RETURN m.timestamp as timestamp,
                   m.platform as platform,
                   e.text as entity,
                   m.content as content,
                   m.source_hash as source_hash
            ORDER BY m.timestamp DESC
            LIMIT $limit
            """,
            text=entity_text,
            limit=limit,
        )
        events = [dict(record) for record in result]

    return json.dumps(events, indent=2, default=str)


# ===========================================================================
# Tools: DPK Pre-Processing (Identification & Analysis)
# ===========================================================================
# IBM Data Prep Kit transforms wrapped as MCP tools.
# These run FIRST on raw text, before custom detection.

from tools.dpk_tools import (
    dpk_hap_score as _dpk_hap_score,
    dpk_pii_redact as _dpk_pii_redact,
    dpk_lang_id as _dpk_lang_id,
    dpk_doc_quality as _dpk_doc_quality,
    dpk_readability as _dpk_readability,
)
from tools.voice_tools import fingerprint_voice as _fingerprint_voice
from tools.user_detection import (
    user_behavioral_detection as _user_behavioral_detection,
    user_darvo_detection as _user_darvo_detection,
    user_coercive_control as _user_coercive_control,
)
from tools.workflow_tools import (
    workflow_list as _workflow_list,
    workflow_run as _workflow_run,
    workflow_update_config as _workflow_update_config,
    workflow_add_module as _workflow_add_module,
    workflow_remove_module as _workflow_remove_module,
    register_tool,
)


@mcp.tool()
def dpk_hap_score(text: str, mode: str = "pass1") -> str:
    """Score text for Hate, Abuse, and Profanity (HAP) using IBM Granite 38M model."""
    return _dpk_hap_score(text, mode)


@mcp.tool()
def dpk_pii_redact(
    text: str,
    entities: Optional[str] = None,
    operator: str = "replace",
    score_threshold: float = 0.6,
) -> str:
    """Detect and redact PII using Microsoft Presidio + spaCy."""
    entity_list = json.loads(entities) if entities else None
    return _dpk_pii_redact(text, entity_list, operator, score_threshold)


@mcp.tool()
def dpk_lang_id(text: str) -> str:
    """Identify language of text using fasttext."""
    return _dpk_lang_id(text)


@mcp.tool()
def dpk_doc_quality(text: str) -> str:
    """Score document quality based on structure, length, readability."""
    return _dpk_doc_quality(text)


@mcp.tool()
def dpk_readability(text: str) -> str:
    """Calculate readability metrics (Flesch Reading Ease, Flesch-Kincaid Grade)."""
    return _dpk_readability(text)


@mcp.tool()
def fingerprint_voice(text: str, reference_texts: Optional[str] = None) -> str:
    """Voice fingerprinting using Burrows' Delta (faststylometry)."""
    refs = json.loads(reference_texts) if reference_texts else None
    return _fingerprint_voice(text, refs)


@mcp.tool()
def user_behavioral_detection(
    text: str, context: Optional[str] = None, mode: str = "pass1"
) -> str:
    """User's custom behavioral pattern detection system."""
    return _user_behavioral_detection(text, context, mode)


@mcp.tool()
def user_darvo_detection(
    text: str, context: Optional[str] = None, mode: str = "pass1"
) -> str:
    """User's custom DARVO (Deny, Attack, Reverse Victim/Offender) detection."""
    return _user_darvo_detection(text, context, mode)


@mcp.tool()
def user_coercive_control(
    text: str, context: Optional[str] = None, mode: str = "pass1"
) -> str:
    """User's custom coercive control analysis."""
    return _user_coercive_control(text, context, mode)


@mcp.tool()
def workflow_list() -> str:
    """List all available workflows and their modules from config."""
    return _workflow_list()


@mcp.tool()
def workflow_run(
    text: str, workflow_name: str = "full_analysis", mode: str = "pass1"
) -> str:
    """Run a configured workflow on text. Modules defined in config/workflows.json."""
    return _workflow_run(text, workflow_name, mode)


@mcp.tool()
def workflow_update_config(config_json: str) -> str:
    """Update workflow configuration at runtime. Pass JSON with modules/workflows to update."""
    return _workflow_update_config(config_json)


@mcp.tool()
def workflow_add_module(
    workflow_name: str, module_id: str, position: Optional[int] = None
) -> str:
    """Add a module to a workflow at runtime."""
    return _workflow_add_module(workflow_name, module_id, position)


@mcp.tool()
def workflow_remove_module(workflow_name: str, module_id: str) -> str:
    """Remove a module from a workflow at runtime."""
    return _workflow_remove_module(workflow_name, module_id)


# ---------------------------------------------------------------------------
# Register tools with workflow engine (so workflows can call them)
# ---------------------------------------------------------------------------
register_tool("dpk_hap_score", _dpk_hap_score)
register_tool("dpk_pii_redact", _dpk_pii_redact)
register_tool("dpk_lang_id", _dpk_lang_id)
register_tool("dpk_doc_quality", _dpk_doc_quality)
register_tool("dpk_readability", _dpk_readability)
register_tool("fingerprint_voice", _fingerprint_voice)
register_tool("user_behavioral_detection", _user_behavioral_detection)
register_tool("user_darvo_detection", _user_darvo_detection)
register_tool("user_coercive_control", _user_coercive_control)
# Semantica tools already registered above
register_tool(
    "semantica_extract_entities",
    _get_ner().extract if hasattr(_get_ner(), "extract") else None,
)


# ===========================================================================
# Document Intelligence Tools
# ===========================================================================

try:
    from document_intelligence.mcp_tools import register_document_intelligence_tools
    register_document_intelligence_tools(mcp)
    logger.info("[dial-py-core] Document intelligence tools registered.")
except Exception as _di_err:
    logger.warning(f"[dial-py-core] Document intelligence tools not loaded: {_di_err}")


# ===========================================================================
# Entry Point
# ===========================================================================

if __name__ == "__main__":
    logger.info("[dial-py-core] Starting Python MCP Server...")
    mcp.run()
