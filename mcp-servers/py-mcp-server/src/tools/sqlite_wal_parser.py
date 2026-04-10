"""
SQLite WAL Parser for Deleted Message Recovery

Parses SQLite Write-Ahead Log (WAL) files to recover deleted messages.
Useful for forensic analysis of SMS databases and other SQLite stores.

Part of the Critical Pipeline Additions (Task 3).

Created: 2026-03-16
Author: execution@opencode
"""

import struct
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, BinaryIO
from pydantic import BaseModel, Field
from enum import Enum
import hashlib
import logging
import uuid

logger = logging.getLogger(__name__)


class WALMagicType(str, Enum):
    """WAL file magic number types."""

    BIG_ENDIAN = "377f0682"  # 0x377f0682
    LITTLE_ENDIAN = "377f0683"  # 0x377f0683


class RecoveryStatus(str, Enum):
    """Status of message recovery."""

    RECOVERED = "recovered"
    PARTIAL = "partial"
    FAILED = "failed"
    ENCRYPTED = "encrypted"


class WALHeader(BaseModel):
    """WAL file header (32 bytes)."""

    magic: int = Field(..., description="Magic number determining endianness")
    format_version: int = Field(..., description="WAL format version")
    page_size: int = Field(..., description="Database page size")
    checkpoint_seq: int = Field(..., description="Checkpoint sequence number")
    salt1: int = Field(..., description="Salt value 1")
    salt2: int = Field(..., description="Salt value 2")
    checksum1: int = Field(..., description="Checksum 1")
    checksum2: int = Field(..., description="Checksum 2")
    is_big_endian: bool = Field(..., description="Whether file uses big-endian")


class WALFrame(BaseModel):
    """WAL frame (24 bytes header + page data)."""

    page_number: int = Field(..., description="Database page number")
    commit_size: int = Field(..., description="Commit marker (0 if not commit frame)")
    salt1: int = Field(..., description="Salt value 1")
    salt2: int = Field(..., description="Salt value 2")
    checksum1: int = Field(..., description="Checksum 1")
    checksum2: int = Field(..., description="Checksum 2")
    page_data: bytes = Field(..., description="Raw page content")
    frame_offset: int = Field(..., description="Byte offset in WAL file")
    is_commit: bool = Field(default=False, description="Whether this is a commit frame")


class RecoveredMessage(BaseModel):
    """A recovered deleted message."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Recovery UUID"
    )
    wal_source: str = Field(..., description="Path to source WAL file")
    frame_offset: int = Field(..., description="Byte offset in WAL")
    page_number: int = Field(..., description="Database page number")
    recovery_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When message was recovered",
    )
    message_data: Dict[str, Any] = Field(
        default_factory=dict, description="Extracted message data"
    )
    recovery_hash: str = Field(..., description="Hash of recovered data")
    original_hash: Optional[str] = Field(
        None, description="Original hash if determinable"
    )
    status: RecoveryStatus = Field(
        default=RecoveryStatus.RECOVERED, description="Recovery status"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class WALParseResult(BaseModel):
    """Result of parsing a WAL file."""

    wal_path: str = Field(..., description="Path to WAL file")
    header: Optional[WALHeader] = Field(None, description="WAL header")
    frames: List[WALFrame] = Field(default_factory=list, description="Parsed frames")
    total_frames: int = Field(default=0, description="Total frames found")
    parse_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When parsing occurred",
    )
    errors: List[str] = Field(default_factory=list, description="Parse errors")
    success: bool = Field(default=True, description="Whether parsing succeeded")


class SQLiteWALParser:
    """
    Parser for SQLite Write-Ahead Log (WAL) files.

    WAL files contain uncommitted transactions that can include deleted
    records. This parser extracts frames and attempts to recover deleted
    messages from SMS/iMessage databases.

    Example:
        >>> parser = SQLiteWALParser(Path("/path/to/sms.db-wal"))
        >>> result = parser.parse()
        >>> messages = parser.recover_deleted_messages()
    """

    # WAL magic numbers
    WAL_MAGIC_BE = 0x377F0682  # Big-endian
    WAL_MAGIC_LE = 0x377F0683  # Little-endian

    # Header size
    WAL_HEADER_SIZE = 32

    # Frame header size
    FRAME_HEADER_SIZE = 24

    def __init__(self, wal_path: Path):
        """
        Initialize WAL parser.

        Args:
            wal_path: Path to the WAL file
        """
        self.wal_path = Path(wal_path)
        self.header: Optional[WALHeader] = None
        self.frames: List[WALFrame] = []
        self._is_big_endian: bool = True

    def parse(self) -> WALParseResult:
        """
        Parse the WAL file and extract all frames.

        Returns:
            WALParseResult with header and frames
        """
        result = WALParseResult(wal_path=str(self.wal_path))

        try:
            if not self.wal_path.exists():
                result.errors.append(f"WAL file not found: {self.wal_path}")
                result.success = False
                return result

            with open(self.wal_path, "rb") as f:
                # Parse header
                self.header = self._parse_header(f)
                if self.header is None:
                    result.errors.append("Failed to parse WAL header")
                    result.success = False
                    return result
                result.header = self.header

                # Parse frames
                self.frames = self._parse_frames(f)
                result.frames = self.frames
                result.total_frames = len(self.frames)

        except Exception as e:
            logger.error(f"WAL parse error: {e}")
            result.errors.append(str(e))
            result.success = False

        return result

    def _parse_header(self, f: BinaryIO) -> Optional[WALHeader]:
        """
        Parse the 32-byte WAL header.

        Args:
            f: Binary file handle positioned at start

        Returns:
            WALHeader or None if invalid
        """
        header_data = f.read(self.WAL_HEADER_SIZE)
        if len(header_data) < self.WAL_HEADER_SIZE:
            logger.error(f"Header too short: {len(header_data)} bytes")
            return None

        # Determine endianness from magic number
        magic_be = struct.unpack(">I", header_data[0:4])[0]
        magic_le = struct.unpack("<I", header_data[0:4])[0]

        if magic_be == self.WAL_MAGIC_BE:
            self._is_big_endian = True
            magic = magic_be
            fmt = ">"
        elif magic_le == self.WAL_MAGIC_LE:
            self._is_big_endian = False
            magic = magic_le
            fmt = "<"
        elif magic_be == self.WAL_MAGIC_LE:
            # Little-endian file, big-endian read
            self._is_big_endian = False
            magic = magic_be
            fmt = ">"
        else:
            logger.error(f"Invalid WAL magic: {hex(magic_be)}")
            return None

        # Parse remaining header fields
        header = WALHeader(
            magic=magic,
            format_version=struct.unpack(f"{fmt}I", header_data[4:8])[0],
            page_size=struct.unpack(f"{fmt}I", header_data[8:12])[0],
            checkpoint_seq=struct.unpack(f"{fmt}I", header_data[12:16])[0],
            salt1=struct.unpack(f"{fmt}I", header_data[16:20])[0],
            salt2=struct.unpack(f"{fmt}I", header_data[20:24])[0],
            checksum1=struct.unpack(f"{fmt}I", header_data[24:28])[0],
            checksum2=struct.unpack(f"{fmt}I", header_data[28:32])[0],
            is_big_endian=self._is_big_endian,
        )

        return header

    def _parse_frames(self, f: BinaryIO) -> List[WALFrame]:
        """
        Parse all WAL frames after the header.

        Args:
            f: Binary file handle positioned after header

        Returns:
            List of WALFrame objects
        """
        frames = []
        frame_offset = self.WAL_HEADER_SIZE

        if self.header is None:
            return frames

        fmt = ">" if self._is_big_endian else "<"
        page_size = self.header.page_size

        while True:
            # Read frame header
            frame_header = f.read(self.FRAME_HEADER_SIZE)
            if len(frame_header) < self.FRAME_HEADER_SIZE:
                break

            # Parse frame header
            page_number = struct.unpack(f"{fmt}I", frame_header[0:4])[0]
            commit_size = struct.unpack(f"{fmt}I", frame_header[4:8])[0]
            salt1 = struct.unpack(f"{fmt}I", frame_header[8:12])[0]
            salt2 = struct.unpack(f"{fmt}I", frame_header[12:16])[0]
            checksum1 = struct.unpack(f"{fmt}I", frame_header[16:20])[0]
            checksum2 = struct.unpack(f"{fmt}I", frame_header[20:24])[0]

            # Read page data
            page_data = f.read(page_size)
            if len(page_data) < page_size:
                break

            frame = WALFrame(
                page_number=page_number,
                commit_size=commit_size,
                salt1=salt1,
                salt2=salt2,
                checksum1=checksum1,
                checksum2=checksum2,
                page_data=page_data,
                frame_offset=frame_offset,
                is_commit=(commit_size != 0),
            )
            frames.append(frame)

            frame_offset += self.FRAME_HEADER_SIZE + page_size

        return frames

    def recover_deleted_messages(self) -> List[RecoveredMessage]:
        """
        Attempt to recover deleted messages from WAL frames.

        Returns:
            List of RecoveredMessage objects
        """
        recovered = []

        for frame in self.frames:
            # Try to extract messages from page data
            messages = self._extract_messages_from_page(frame.page_data)

            for msg_data in messages:
                recovery_hash = hashlib.sha256(frame.page_data).hexdigest()

                recovered_msg = RecoveredMessage(
                    wal_source=str(self.wal_path),
                    frame_offset=frame.frame_offset,
                    page_number=frame.page_number,
                    message_data=msg_data,
                    recovery_hash=recovery_hash,
                    status=RecoveryStatus.RECOVERED,
                )
                recovered.append(recovered_msg)

        return recovered

    def _extract_messages_from_page(self, page_data: bytes) -> List[Dict[str, Any]]:
        """
        Extract message records from a database page.

        This is a simplified extraction. Real implementation would need
        to parse SQLite B-tree structure and record format.

        Args:
            page_data: Raw page bytes

        Returns:
            List of message dictionaries
        """
        messages = []

        # SQLite page header (for table leaf pages)
        # Offset 0: Page type (0x0D for table leaf)
        # Offset 1-2: First freeblock offset
        # Offset 3-4: Number of cells
        # Offset 5-6: Cell content area start

        if len(page_data) < 8:
            return messages

        page_type = page_data[0]

        # Table leaf page (0x0D) contains actual row data
        if page_type == 0x0D:
            # Try to extract SMS/iMessage records
            messages.extend(self._extract_sms_records(page_data))

        return messages

    def _extract_sms_records(self, page_data: bytes) -> List[Dict[str, Any]]:
        """
        Extract SMS/iMessage records from a table leaf page.

        This is a heuristic extraction. Real forensic tools use
        proper SQLite B-tree parsing.

        Args:
            page_data: Raw page bytes

        Returns:
            List of extracted message dictionaries
        """
        messages = []

        # Look for common SMS patterns in the data
        # This is simplified - real implementation would parse the B-tree

        # Try to find text patterns that look like messages
        text = page_data.decode("utf-8", errors="ignore")

        # Look for phone number patterns
        import re

        phone_pattern = r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        phones = re.findall(phone_pattern, text)

        # Look for date patterns (iOS SMS format)
        date_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        dates = re.findall(date_pattern, text)

        # If we found potential message data, create a record
        if phones or dates:
            messages.append(
                {
                    "phones": phones,
                    "dates": dates,
                    "raw_text_preview": text[:200] if len(text) > 200 else text,
                    "extraction_method": "heuristic",
                }
            )

        return messages


class SMSDatabaseWALParser(SQLiteWALParser):
    """
    Specialized WAL parser for SMS/iMessage databases.

    Handles iOS sms.db and Android mmssms.db formats.
    """

    def _extract_sms_records(self, page_data: bytes) -> List[Dict[str, Any]]:
        """Extract SMS records with iOS/Android specific parsing."""
        messages = []

        # Try iOS sms.db format first
        messages.extend(self._extract_ios_sms(page_data))

        # Try Android mmssms.db format
        messages.extend(self._extract_android_sms(page_data))

        return messages

    def _extract_ios_sms(self, page_data: bytes) -> List[Dict[str, Any]]:
        """Extract iOS SMS records."""
        messages = []

        # iOS sms.db structure:
        # - message table has: ROWID, address, date, text, flags, etc.
        # - Dates are in Cocoa epoch (seconds since 2001-01-01)

        # Look for message text patterns
        try:
            text = page_data.decode("utf-8", errors="ignore")

            # Find potential message content between null bytes
            import re

            # Match printable text sequences
            content_chunks = re.findall(r"[\x20-\x7E]{10,}", text)

            for chunk in content_chunks:
                if len(chunk) > 10:  # Minimum message length
                    messages.append(
                        {
                            "text_preview": chunk[:100],
                            "platform": "ios",
                            "extraction_method": "heuristic",
                        }
                    )
        except Exception as e:
            logger.debug(f"iOS SMS extraction error: {e}")

        return messages

    def _extract_android_sms(self, page_data: bytes) -> List[Dict[str, Any]]:
        """Extract Android SMS records."""
        messages = []

        # Android mmssms.db structure:
        # - sms table has: _id, thread_id, address, date, date_sent, body, etc.
        # - Dates are in Unix epoch (milliseconds)

        try:
            text = page_data.decode("utf-8", errors="ignore")

            # Look for phone numbers and dates
            import re

            phones = re.findall(r"\+?\d{10,15}", text)

            if phones:
                messages.append(
                    {
                        "phones": phones,
                        "platform": "android",
                        "extraction_method": "heuristic",
                    }
                )
        except Exception as e:
            logger.debug(f"Android SMS extraction error: {e}")

        return messages


# MCP Tool Functions


def mcp_parse_wal_file(wal_path: str) -> Dict[str, Any]:
    """
    MCP Tool: Parse a SQLite WAL file.

    Args:
        wal_path: Path to the WAL file

    Returns:
        Dict with parse results
    """
    try:
        parser = SQLiteWALParser(Path(wal_path))
        result = parser.parse()

        return {
            "success": True,
            "wal_path": result.wal_path,
            "total_frames": result.total_frames,
            "header": result.header.model_dump() if result.header else None,
            "frames": [
                {
                    "page_number": f.page_number,
                    "frame_offset": f.frame_offset,
                    "is_commit": f.is_commit,
                }
                for f in result.frames[:100]  # Limit output
            ],
            "errors": result.errors,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def mcp_recover_deleted_messages(wal_path: str) -> Dict[str, Any]:
    """
    MCP Tool: Recover deleted messages from WAL file.

    Args:
        wal_path: Path to the WAL file

    Returns:
        Dict with recovered messages
    """
    try:
        parser = SQLiteWALParser(Path(wal_path))
        parse_result = parser.parse()

        if not parse_result.success:
            return {
                "success": False,
                "error": "WAL parsing failed",
                "details": parse_result.errors,
            }

        messages = parser.recover_deleted_messages()

        return {
            "success": True,
            "wal_path": wal_path,
            "total_frames": len(parser.frames),
            "recovered_count": len(messages),
            "messages": [
                {
                    "id": m.id,
                    "frame_offset": m.frame_offset,
                    "page_number": m.page_number,
                    "recovery_hash": m.recovery_hash,
                    "status": m.status.value,
                    "data": m.message_data,
                }
                for m in messages[:50]  # Limit output
            ],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Export for MCP registration
__all__ = [
    # Enums
    "WALMagicType",
    "RecoveryStatus",
    # Models
    "WALHeader",
    "WALFrame",
    "RecoveredMessage",
    "WALParseResult",
    # Classes
    "SQLiteWALParser",
    "SMSDatabaseWALParser",
    # MCP Tools
    "mcp_parse_wal_file",
    "mcp_recover_deleted_messages",
]
