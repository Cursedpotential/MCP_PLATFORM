"""
Hash Verification Tool for Evidence Pipeline

Provides hash computation and verification for evidence integrity.
Uses SHA-256 by default, supports multiple algorithms.

Part of the Critical Pipeline Additions (Task 1).

Created: 2026-03-16
Author: execution@opencode
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HashAlgorithm(str, Enum):
    """Supported hash algorithms."""

    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"
    MD5 = "md5"  # Legacy support, not recommended for new evidence


class VerificationStatus(str, Enum):
    """Status of hash verification."""

    VERIFIED = "verified"
    FAILED = "failed"
    ERROR = "error"
    PENDING = "pending"


class HashVerificationResult(BaseModel):
    """Result of hash verification."""

    evidence_id: str = Field(..., description="UUID of the evidence being verified")
    verified: bool = Field(..., description="Whether verification passed")
    stored_hash: str = Field(..., description="Hash stored in database")
    computed_hash: str = Field(..., description="Hash computed from content")
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    algorithm: HashAlgorithm = Field(default=HashAlgorithm.SHA256)
    status: VerificationStatus = Field(..., description="Verification status")
    error_message: Optional[str] = Field(
        None, description="Error message if verification failed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class HashComputationResult(BaseModel):
    """Result of hash computation."""

    content_hash: str = Field(..., description="Computed hash value")
    algorithm: HashAlgorithm = Field(..., description="Algorithm used")
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_size_bytes: int = Field(..., description="Size of content in bytes")
    computation_time_ms: float = Field(
        ..., description="Time to compute in milliseconds"
    )


class BatchVerificationResult(BaseModel):
    """Result of batch hash verification."""

    total_items: int = Field(..., description="Total items in batch")
    verified_count: int = Field(..., description="Number of verified items")
    failed_count: int = Field(..., description="Number of failed items")
    error_count: int = Field(..., description="Number of errors")
    results: List[HashVerificationResult] = Field(default_factory=list)
    batch_completed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


def compute_hash(
    content: bytes, algorithm: HashAlgorithm = HashAlgorithm.SHA256, **kwargs
) -> HashComputationResult:
    """
    Compute hash of content using specified algorithm.

    Args:
        content: Raw bytes to hash
        algorithm: Hash algorithm to use (default: SHA-256)

    Returns:
        HashComputationResult with computed hash and metadata

    Example:
        >>> result = compute_hash(b"evidence content")
        >>> print(result.content_hash)
        'a1b2c3...'
    """
    import time

    start_time = time.perf_counter()

    h = hashlib.new(algorithm.value)
    h.update(content)
    content_hash = h.hexdigest()

    computation_time = (time.perf_counter() - start_time) * 1000

    return HashComputationResult(
        content_hash=content_hash,
        algorithm=algorithm,
        content_size_bytes=len(content),
        computation_time_ms=computation_time,
    )


def verify_evidence_hash(
    evidence_id: str,
    content: bytes,
    stored_hash: str,
    algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    metadata: Optional[Dict[str, Any]] = None,
) -> HashVerificationResult:
    """
    Verify evidence hash matches stored hash.

    This is the primary verification function used at retrieval time.
    It computes the hash of the content and compares it to the stored hash.

    Args:
        evidence_id: UUID of the evidence
        content: Raw bytes of the evidence content
        stored_hash: Hash stored in the database
        algorithm: Hash algorithm used (must match stored hash algorithm)
        metadata: Additional metadata to include in result

    Returns:
        HashVerificationResult with verification status

    Example:
        >>> result = verify_evidence_hash(
        ...     evidence_id="550e8400-e29b-41d4-a716-446655440000",
        ...     content=file_bytes,
        ...     stored_hash="a1b2c3..."
        ... )
        >>> print(result.verified)
        True
    """
    try:
        # Compute hash
        computed = compute_hash(content, algorithm)

        # Compare (case-insensitive)
        verified = stored_hash.lower() == computed.content_hash.lower()

        status = VerificationStatus.VERIFIED if verified else VerificationStatus.FAILED

        return HashVerificationResult(
            evidence_id=evidence_id,
            verified=verified,
            stored_hash=stored_hash,
            computed_hash=computed.content_hash,
            algorithm=algorithm,
            status=status,
            metadata=metadata or {},
        )

    except Exception as e:
        logger.error(f"Hash verification error for {evidence_id}: {e}")
        return HashVerificationResult(
            evidence_id=evidence_id,
            verified=False,
            stored_hash=stored_hash,
            computed_hash="",
            algorithm=algorithm,
            status=VerificationStatus.ERROR,
            error_message=str(e),
            metadata=metadata or {},
        )


def verify_hash_from_file(
    evidence_id: str,
    file_path: str,
    stored_hash: str,
    algorithm: HashAlgorithm = HashAlgorithm.SHA256,
) -> HashVerificationResult:
    """
    Verify hash from a file path.

    Reads the file and computes hash for verification.

    Args:
        evidence_id: UUID of the evidence
        file_path: Path to the evidence file
        stored_hash: Hash stored in the database
        algorithm: Hash algorithm used

    Returns:
        HashVerificationResult with verification status
    """
    from pathlib import Path

    try:
        path = Path(file_path)
        if not path.exists():
            return HashVerificationResult(
                evidence_id=evidence_id,
                verified=False,
                stored_hash=stored_hash,
                computed_hash="",
                algorithm=algorithm,
                status=VerificationStatus.ERROR,
                error_message=f"File not found: {file_path}",
                metadata={"file_path": file_path},
            )

        content = path.read_bytes()
        return verify_evidence_hash(
            evidence_id=evidence_id,
            content=content,
            stored_hash=stored_hash,
            algorithm=algorithm,
            metadata={"file_path": str(path.absolute())},
        )

    except Exception as e:
        logger.error(f"File hash verification error for {evidence_id}: {e}")
        return HashVerificationResult(
            evidence_id=evidence_id,
            verified=False,
            stored_hash=stored_hash,
            computed_hash="",
            algorithm=algorithm,
            status=VerificationStatus.ERROR,
            error_message=str(e),
            metadata={"file_path": file_path},
        )


def batch_verify_hashes(
    items: List[Dict[str, Any]], algorithm: HashAlgorithm = HashAlgorithm.SHA256
) -> BatchVerificationResult:
    """
    Verify multiple evidence items in batch.

    Args:
        items: List of dicts with 'evidence_id', 'content' (bytes), 'stored_hash'
        algorithm: Hash algorithm to use

    Returns:
        BatchVerificationResult with summary and individual results

    Example:
        >>> items = [
        ...     {"evidence_id": "id1", "content": b"data1", "stored_hash": "abc..."},
        ...     {"evidence_id": "id2", "content": b"data2", "stored_hash": "def..."}
        ... ]
        >>> result = batch_verify_hashes(items)
        >>> print(f"Verified: {result.verified_count}/{result.total_items}")
    """
    results = []
    verified_count = 0
    failed_count = 0
    error_count = 0

    for item in items:
        result = verify_evidence_hash(
            evidence_id=item.get("evidence_id", "unknown"),
            content=item.get("content", b""),
            stored_hash=item.get("stored_hash", ""),
            algorithm=algorithm,
            metadata=item.get("metadata", {}),
        )
        results.append(result)

        if result.status == VerificationStatus.VERIFIED:
            verified_count += 1
        elif result.status == VerificationStatus.FAILED:
            failed_count += 1
        else:
            error_count += 1

    return BatchVerificationResult(
        total_items=len(items),
        verified_count=verified_count,
        failed_count=failed_count,
        error_count=error_count,
        results=results,
    )


def compute_multihash(
    content: bytes, algorithms: List[HashAlgorithm] = None
) -> Dict[HashAlgorithm, str]:
    """
    Compute multiple hashes for the same content.

    Useful for evidence that needs multiple hash representations
    (e.g., for compatibility with different systems).

    Args:
        content: Raw bytes to hash
        algorithms: List of algorithms to use (default: SHA-256, SHA-512)

    Returns:
        Dict mapping algorithm to hash value

    Example:
        >>> hashes = compute_multihash(b"evidence")
        >>> print(hashes[HashAlgorithm.SHA256])
        'a1b2c3...'
        >>> print(hashes[HashAlgorithm.SHA512])
        'd4e5f6...'
    """
    if algorithms is None:
        algorithms = [HashAlgorithm.SHA256, HashAlgorithm.SHA512]

    result = {}
    for algo in algorithms:
        computed = compute_hash(content, algo)
        result[algo] = computed.content_hash

    return result


# MCP Tool Functions


def mcp_compute_hash(content_b64: str, algorithm: str = "sha256") -> Dict[str, Any]:
    """
    MCP Tool: Compute hash of base64-encoded content.

    Args:
        content_b64: Base64-encoded content
        algorithm: Hash algorithm (sha256, sha384, sha512, blake2b)

    Returns:
        Dict with hash value and metadata
    """
    import base64

    try:
        content = base64.b64decode(content_b64)
        algo = HashAlgorithm(algorithm.lower())
        result = compute_hash(content, algo)

        return {
            "success": True,
            "content_hash": result.content_hash,
            "algorithm": result.algorithm.value,
            "content_size_bytes": result.content_size_bytes,
            "computation_time_ms": result.computation_time_ms,
            "computed_at": result.computed_at.isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def mcp_verify_evidence_hash(
    evidence_id: str, content_b64: str, stored_hash: str, algorithm: str = "sha256"
) -> Dict[str, Any]:
    """
    MCP Tool: Verify evidence hash.

    Args:
        evidence_id: UUID of the evidence
        content_b64: Base64-encoded content
        stored_hash: Hash stored in database
        algorithm: Hash algorithm used

    Returns:
        Dict with verification result
    """
    import base64

    try:
        content = base64.b64decode(content_b64)
        algo = HashAlgorithm(algorithm.lower())
        result = verify_evidence_hash(evidence_id, content, stored_hash, algo)

        return {
            "success": True,
            "verified": result.verified,
            "evidence_id": result.evidence_id,
            "stored_hash": result.stored_hash,
            "computed_hash": result.computed_hash,
            "status": result.status.value,
            "verified_at": result.verified_at.isoformat(),
            "algorithm": result.algorithm.value,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "verified": False}


def mcp_verify_file_hash(
    evidence_id: str, file_path: str, stored_hash: str, algorithm: str = "sha256"
) -> Dict[str, Any]:
    """
    MCP Tool: Verify hash from file path.

    Args:
        evidence_id: UUID of the evidence
        file_path: Path to the evidence file
        stored_hash: Hash stored in database
        algorithm: Hash algorithm used

    Returns:
        Dict with verification result
    """
    try:
        algo = HashAlgorithm(algorithm.lower())
        result = verify_hash_from_file(evidence_id, file_path, stored_hash, algo)

        return {
            "success": True,
            "verified": result.verified,
            "evidence_id": result.evidence_id,
            "stored_hash": result.stored_hash,
            "computed_hash": result.computed_hash,
            "status": result.status.value,
            "verified_at": result.verified_at.isoformat(),
            "algorithm": result.algorithm.value,
            "error_message": result.error_message,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "verified": False}


# Export for MCP registration
__all__ = [
    # Enums
    "HashAlgorithm",
    "VerificationStatus",
    # Models
    "HashVerificationResult",
    "HashComputationResult",
    "BatchVerificationResult",
    # Functions
    "compute_hash",
    "verify_evidence_hash",
    "verify_hash_from_file",
    "batch_verify_hashes",
    "compute_multihash",
    # MCP Tools
    "mcp_compute_hash",
    "mcp_verify_evidence_hash",
    "mcp_verify_file_hash",
]
