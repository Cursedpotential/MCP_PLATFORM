"""
Ed25519 Cryptographic Signing for Evidence Chain of Custody

Provides Ed25519 signatures for evidence integrity verification.
Ed25519 is fast, secure, and legally defensible.

Part of the Critical Pipeline Additions (Task 4).

Created: 2026-03-16
Author: execution@opencode
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import json
import hashlib
import logging
import os
import base64

logger = logging.getLogger(__name__)

# Try to import nacl, provide helpful error if not available
try:
    from nacl.signing import SigningKey, VerifyKey, SignedMessage
    from nacl.encoding import HexEncoder, RawEncoder
    from nacl.exceptions import BadSignatureError

    HAS_NACL = True
except ImportError:
    HAS_NACL = False
    SigningKey = None
    VerifyKey = None
    logger.warning("PyNaCl not installed. Ed25519 signing will be disabled.")


class SignatureAction(str, Enum):
    """Action types for chain of custody."""

    CREATED = "created"
    ACCESSED = "accessed"
    MODIFIED = "modified"
    TRANSFERRED = "transferred"
    VERIFIED = "verified"
    EXPORTED = "exported"
    ARCHIVED = "archived"


class SignatureStatus(str, Enum):
    """Status of signature verification."""

    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"
    PENDING = "pending"


class EvidenceSignature(BaseModel):
    """Cryptographic signature for evidence."""

    evidence_id: str = Field(..., description="UUID of the evidence")
    signature: str = Field(..., description="Hex-encoded Ed25519 signature")
    public_key: str = Field(..., description="Hex-encoded public key")
    signed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signed_hash: str = Field(..., description="Hash of the signed message")
    signer_id: str = Field(..., description="Identifier of the signer")
    action: SignatureAction = Field(
        default=SignatureAction.CREATED, description="Action being signed"
    )
    algorithm: str = Field(default="Ed25519", description="Signature algorithm")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChainOfCustodyEntry(BaseModel):
    """A single entry in the chain of custody."""

    sequence_number: int = Field(..., description="Order in chain")
    evidence_id: str = Field(..., description="UUID of the evidence")
    action: SignatureAction = Field(..., description="Action performed")
    actor_id: str = Field(..., description="Who performed the action")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signature: EvidenceSignature = Field(..., description="Cryptographic signature")
    previous_hash: Optional[str] = Field(None, description="Hash of previous entry")
    entry_hash: str = Field(..., description="Hash of this entry")
    notes: Optional[str] = Field(None, description="Optional notes")


class ChainOfCustody(BaseModel):
    """Complete chain of custody for evidence."""

    evidence_id: str = Field(..., description="UUID of the evidence")
    entries: List[ChainOfCustodyEntry] = Field(
        default_factory=list, description="Chain entries"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_valid: bool = Field(default=True, description="Whether chain is valid")
    verification_errors: List[str] = Field(default_factory=list)


class EvidenceSigner:
    """
    Ed25519 signer for evidence chain of custody.

    Ed25519 provides:
    - Fast signing and verification
    - Small signature size (64 bytes)
    - Small public key size (32 bytes)
    - Cryptographic security
    - Legal admissibility (NIST approved)

    Example:
        >>> signer = EvidenceSigner()
        >>> sig = signer.sign_evidence("evidence-uuid", "abc123hash", {"file": "test.pdf"}, "user1")
        >>> print(sig.signature)
        'a1b2c3...'
        >>> EvidenceSigner.verify_signature("evidence-uuid", "abc123hash", {"file": "test.pdf"}, sig)
        True
    """

    def __init__(self, seed: Optional[bytes] = None):
        """
        Initialize signer with optional seed for deterministic keys.

        Args:
            seed: Optional 32-byte seed for deterministic key generation.
                  Use None for random key generation.
        """
        if not HAS_NACL:
            raise ImportError(
                "PyNaCl is required for Ed25519 signing. Install with: pip install pynacl"
            )

        if seed is not None:
            if len(seed) != 32:
                raise ValueError("Seed must be exactly 32 bytes")
            self.signing_key = SigningKey(seed)
        else:
            self.signing_key = SigningKey.generate()

        self.verify_key = self.signing_key.verify_key

    @property
    def public_key_hex(self) -> str:
        """Get public key as hex string."""
        return self.verify_key.encode(encoder=HexEncoder).decode("utf-8")

    @property
    def private_key_hex(self) -> str:
        """Get private key as hex string (KEEP SECRET!)."""
        return self.signing_key.encode(encoder=HexEncoder).decode("utf-8")

    def sign_evidence(
        self,
        evidence_id: str,
        content_hash: str,
        metadata: Dict[str, Any],
        signer_id: str,
        action: SignatureAction = SignatureAction.CREATED,
    ) -> EvidenceSignature:
        """
        Sign an evidence record.

        Args:
            evidence_id: UUID of the evidence
            content_hash: Hash of the evidence content
            metadata: Additional metadata to include
            signer_id: Identifier of the signer
            action: Action being signed

        Returns:
            EvidenceSignature with signature
        """
        # Create canonical message to sign
        message = self._create_signable_message(
            evidence_id, content_hash, metadata, action
        )

        # Canonical JSON encoding
        message_bytes = json.dumps(message, sort_keys=True).encode("utf-8")
        message_hash = hashlib.sha256(message_bytes).hexdigest()

        # Sign
        signed = self.signing_key.sign(message_bytes)
        signature_hex = signed.signature.encode(encoder=HexEncoder).decode("utf-8")

        return EvidenceSignature(
            evidence_id=evidence_id,
            signature=signature_hex,
            public_key=self.public_key_hex,
            signed_hash=message_hash,
            signer_id=signer_id,
            action=action,
            metadata=metadata,
        )

    def _create_signable_message(
        self,
        evidence_id: str,
        content_hash: str,
        metadata: Dict[str, Any],
        action: SignatureAction,
    ) -> Dict[str, Any]:
        """Create a canonical message for signing."""
        return {
            "evidence_id": evidence_id,
            "content_hash": content_hash,
            "metadata": metadata,
            "action": action.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def verify_signature(
        evidence_id: str,
        content_hash: str,
        metadata: Dict[str, Any],
        signature: EvidenceSignature,
    ) -> bool:
        """
        Verify an evidence signature.

        Args:
            evidence_id: UUID of the evidence
            content_hash: Hash of the evidence content
            metadata: Metadata that was signed
            signature: The signature to verify

        Returns:
            True if signature is valid
        """
        if not HAS_NACL:
            logger.error("PyNaCl not available for signature verification")
            return False

        try:
            # Recreate message
            message = {
                "evidence_id": evidence_id,
                "content_hash": content_hash,
                "metadata": metadata,
                "action": signature.action.value,
                "timestamp": signature.signed_at.isoformat(),
            }
            message_bytes = json.dumps(message, sort_keys=True).encode("utf-8")

            # Verify
            verify_key = VerifyKey(signature.public_key, encoder=HexEncoder)
            signature_bytes = bytes.fromhex(signature.signature)

            verify_key.verify(message_bytes, signature_bytes)
            return True

        except BadSignatureError:
            logger.warning(f"Invalid signature for evidence {evidence_id}")
            return False
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False


class ChainOfCustodyManager:
    """
    Manages chain of custody for evidence.

    Creates and verifies a cryptographic chain of custody
    that can be used to prove evidence integrity in court.
    """

    def __init__(self, signer: EvidenceSigner):
        """
        Initialize chain of custody manager.

        Args:
            signer: EvidenceSigner instance for signing
        """
        self.signer = signer

    def create_chain(
        self,
        evidence_id: str,
        content_hash: str,
        actor_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChainOfCustody:
        """
        Create a new chain of custody for evidence.

        Args:
            evidence_id: UUID of the evidence
            content_hash: Hash of the evidence content
            actor_id: Who is creating the evidence
            metadata: Optional metadata

        Returns:
            ChainOfCustody with initial entry
        """
        chain = ChainOfCustody(evidence_id=evidence_id)

        # Create initial entry
        signature = self.signer.sign_evidence(
            evidence_id=evidence_id,
            content_hash=content_hash,
            metadata=metadata or {},
            signer_id=actor_id,
            action=SignatureAction.CREATED,
        )

        entry_hash = self._compute_entry_hash(
            sequence_number=1,
            evidence_id=evidence_id,
            action=SignatureAction.CREATED,
            timestamp=signature.signed_at,
            signature=signature,
            previous_hash=None,
        )

        entry = ChainOfCustodyEntry(
            sequence_number=1,
            evidence_id=evidence_id,
            action=SignatureAction.CREATED,
            actor_id=actor_id,
            timestamp=signature.signed_at,
            signature=signature,
            previous_hash=None,
            entry_hash=entry_hash,
        )

        chain.entries.append(entry)
        return chain

    def add_entry(
        self,
        chain: ChainOfCustody,
        action: SignatureAction,
        actor_id: str,
        content_hash: str,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChainOfCustodyEntry:
        """
        Add an entry to the chain of custody.

        Args:
            chain: Existing chain to add to
            action: Action being recorded
            actor_id: Who is performing the action
            content_hash: Hash of evidence content
            notes: Optional notes
            metadata: Optional metadata

        Returns:
            New ChainOfCustodyEntry
        """
        # Get previous entry hash
        previous_hash = chain.entries[-1].entry_hash if chain.entries else None

        # Sign
        signature = self.signer.sign_evidence(
            evidence_id=chain.evidence_id,
            content_hash=content_hash,
            metadata=metadata or {},
            signer_id=actor_id,
            action=action,
        )

        sequence_number = len(chain.entries) + 1

        entry_hash = self._compute_entry_hash(
            sequence_number=sequence_number,
            evidence_id=chain.evidence_id,
            action=action,
            timestamp=signature.signed_at,
            signature=signature,
            previous_hash=previous_hash,
        )

        entry = ChainOfCustodyEntry(
            sequence_number=sequence_number,
            evidence_id=chain.evidence_id,
            action=action,
            actor_id=actor_id,
            timestamp=signature.signed_at,
            signature=signature,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
            notes=notes,
        )

        chain.entries.append(entry)
        chain.last_updated = datetime.now(timezone.utc)

        return entry

    def _compute_entry_hash(
        self,
        sequence_number: int,
        evidence_id: str,
        action: SignatureAction,
        timestamp: datetime,
        signature: EvidenceSignature,
        previous_hash: Optional[str],
    ) -> str:
        """Compute hash for a chain entry."""
        data = {
            "sequence_number": sequence_number,
            "evidence_id": evidence_id,
            "action": action.value,
            "timestamp": timestamp.isoformat(),
            "signature": signature.signature,
            "previous_hash": previous_hash,
        }
        data_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data_bytes).hexdigest()

    def verify_chain(self, chain: ChainOfCustody) -> bool:
        """
        Verify entire chain of custody.

        Args:
            chain: Chain to verify

        Returns:
            True if chain is valid
        """
        chain.verification_errors = []

        for i, entry in enumerate(chain.entries):
            # Verify signature
            if not EvidenceSigner.verify_signature(
                entry.evidence_id,
                entry.signature.signed_hash,
                entry.signature.metadata,
                entry.signature,
            ):
                chain.verification_errors.append(f"Entry {i + 1}: Invalid signature")
                chain.is_valid = False
                return False

            # Verify entry hash
            computed_hash = self._compute_entry_hash(
                entry.sequence_number,
                entry.evidence_id,
                entry.action,
                entry.timestamp,
                entry.signature,
                entry.previous_hash,
            )

            if computed_hash != entry.entry_hash:
                chain.verification_errors.append(f"Entry {i + 1}: Hash mismatch")
                chain.is_valid = False
                return False

            # Verify chain linkage
            if i > 0:
                expected_previous = chain.entries[i - 1].entry_hash
                if entry.previous_hash != expected_previous:
                    chain.verification_errors.append(f"Entry {i + 1}: Chain broken")
                    chain.is_valid = False
                    return False

        chain.is_valid = True
        return True

    def export_chain(self, chain: ChainOfCustody) -> str:
        """Export chain as JSON string."""
        return chain.model_dump_json(indent=2)


def generate_keypair() -> Dict[str, str]:
    """
    Generate a new Ed25519 keypair.

    Returns:
        Dict with 'public_key' and 'private_key' (hex encoded)

    Note: Keep private_key secret!
    """
    if not HAS_NACL:
        raise ImportError("PyNaCl required. Install with: pip install pynacl")

    signer = EvidenceSigner()
    return {"public_key": signer.public_key_hex, "private_key": signer.private_key_hex}


def load_signer_from_private_key(private_key_hex: str) -> EvidenceSigner:
    """
    Load a signer from a hex-encoded private key.

    Args:
        private_key_hex: Hex-encoded private key

    Returns:
        EvidenceSigner instance
    """
    if not HAS_NACL:
        raise ImportError("PyNaCl required. Install with: pip install pynacl")

    private_key_bytes = bytes.fromhex(private_key_hex)
    return EvidenceSigner(seed=private_key_bytes)


# MCP Tool Functions


def mcp_generate_keypair() -> Dict[str, Any]:
    """
    MCP Tool: Generate a new Ed25519 keypair.

    Returns:
        Dict with public and private keys
    """
    try:
        keypair = generate_keypair()
        return {
            "success": True,
            "public_key": keypair["public_key"],
            "private_key": keypair["private_key"],
            "warning": "Keep private_key secret! Store securely.",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def mcp_sign_evidence(
    evidence_id: str,
    content_hash: str,
    private_key: str,
    signer_id: str,
    action: str = "created",
    metadata: str = "{}",
) -> Dict[str, Any]:
    """
    MCP Tool: Sign evidence with Ed25519.

    Args:
        evidence_id: UUID of the evidence
        content_hash: Hash of evidence content
        private_key: Hex-encoded private key
        signer_id: Identifier of signer
        action: Action type
        metadata: JSON string of metadata

    Returns:
        Dict with signature details
    """
    try:
        signer = load_signer_from_private_key(private_key)
        action_enum = SignatureAction(action.lower())
        metadata_dict = json.loads(metadata)

        signature = signer.sign_evidence(
            evidence_id=evidence_id,
            content_hash=content_hash,
            metadata=metadata_dict,
            signer_id=signer_id,
            action=action_enum,
        )

        return {
            "success": True,
            "evidence_id": signature.evidence_id,
            "signature": signature.signature,
            "public_key": signature.public_key,
            "signed_at": signature.signed_at.isoformat(),
            "action": signature.action.value,
            "signed_hash": signature.signed_hash,
            "algorithm": signature.algorithm,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def mcp_verify_signature(
    evidence_id: str,
    content_hash: str,
    signature_hex: str,
    public_key: str,
    signed_at: str,
    action: str,
    metadata: str = "{}",
) -> Dict[str, Any]:
    """
    MCP Tool: Verify an Ed25519 signature.

    Args:
        evidence_id: UUID of the evidence
        content_hash: Hash of evidence content
        signature_hex: Hex-encoded signature
        public_key: Hex-encoded public key
        signed_at: ISO timestamp when signed
        action: Action that was signed
        metadata: JSON string of metadata

    Returns:
        Dict with verification result
    """
    try:
        metadata_dict = json.loads(metadata)

        signature = EvidenceSignature(
            evidence_id=evidence_id,
            signature=signature_hex,
            public_key=public_key,
            signed_at=datetime.fromisoformat(signed_at),
            signed_hash="",  # Will be computed
            signer_id="",
            action=SignatureAction(action.lower()),
            metadata=metadata_dict,
        )

        valid = EvidenceSigner.verify_signature(
            evidence_id, content_hash, metadata_dict, signature
        )

        return {
            "success": True,
            "valid": valid,
            "evidence_id": evidence_id,
            "status": "valid" if valid else "invalid",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "valid": False}


# Export for MCP registration
__all__ = [
    # Enums
    "SignatureAction",
    "SignatureStatus",
    # Models
    "EvidenceSignature",
    "ChainOfCustodyEntry",
    "ChainOfCustody",
    # Classes
    "EvidenceSigner",
    "ChainOfCustodyManager",
    # Functions
    "generate_keypair",
    "load_signer_from_private_key",
    # MCP Tools
    "mcp_generate_keypair",
    "mcp_sign_evidence",
    "mcp_verify_signature",
]
