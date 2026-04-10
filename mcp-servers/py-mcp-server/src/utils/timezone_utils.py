"""
Timezone Utilities for Evidence Pipeline

Provides Eastern Time conversion with DST handling.
All timestamps are stored in UTC and converted for display.

Part of the Critical Pipeline Additions (Task 2).

Created: 2026-03-16
Author: execution@opencode
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import logging

# Try to import pendulum, fall back to zoneinfo if not available
try:
    import pendulum

    HAS_PENDULUM = True
except ImportError:
    from zoneinfo import ZoneInfo

    HAS_PENDULUM = False
    pendulum = None

logger = logging.getLogger(__name__)


class TimezoneName(str, Enum):
    """Supported timezone names."""

    UTC = "UTC"
    EASTERN = "America/New_York"
    EASTERN_STANDARD = "EST"
    EASTERN_DAYLIGHT = "EDT"


class EasternTimestamp(BaseModel):
    """Timestamp with Eastern Time conversion."""

    utc: datetime = Field(..., description="Original UTC timestamp")
    eastern: datetime = Field(..., description="Eastern Time timestamp")
    eastern_str: str = Field(..., description="Formatted Eastern Time string")
    is_dst: bool = Field(..., description="Whether Daylight Saving Time is active")
    timezone_name: str = Field(..., description="Timezone abbreviation (EST or EDT)")
    offset_hours: int = Field(
        ..., description="UTC offset in hours (-5 for EST, -4 for EDT)"
    )
    iso8601_utc: str = Field(..., description="ISO 8601 format in UTC")
    iso8601_eastern: str = Field(..., description="ISO 8601 format in Eastern Time")


class TimestampRange(BaseModel):
    """A range of timestamps with Eastern Time conversion."""

    start_utc: datetime = Field(..., description="Start timestamp in UTC")
    end_utc: datetime = Field(..., description="End timestamp in UTC")
    start_eastern: EasternTimestamp = Field(..., description="Start in Eastern Time")
    end_eastern: EasternTimestamp = Field(..., description="End in Eastern Time")
    duration_seconds: float = Field(..., description="Duration in seconds")
    crosses_dst_boundary: bool = Field(
        ..., description="Whether range crosses DST boundary"
    )


def convert_to_eastern(utc_timestamp: datetime) -> EasternTimestamp:
    """
    Convert UTC timestamp to Eastern Time with DST info.

    Uses pendulum for accurate DST handling if available,
    otherwise falls back to Python's zoneinfo.

    Args:
        utc_timestamp: UTC datetime (will be converted to UTC if naive)

    Returns:
        EasternTimestamp with conversion details

    Example:
        >>> from datetime import datetime, timezone
        >>> utc = datetime(2024, 7, 15, 14, 30, tzinfo=timezone.utc)
        >>> et = convert_to_eastern(utc)
        >>> print(f"{et.eastern_str} {et.timezone_name}")
        '2024-07-15 10:30:00 EDT'
    """
    # Ensure UTC timezone
    if utc_timestamp.tzinfo is None:
        utc_timestamp = utc_timestamp.replace(tzinfo=timezone.utc)
    elif utc_timestamp.tzinfo != timezone.utc:
        utc_timestamp = utc_timestamp.astimezone(timezone.utc)

    if HAS_PENDULUM:
        # Use pendulum for better DST handling
        eastern = pendulum.instance(utc_timestamp).in_timezone("America/New_York")
        is_dst = eastern.is_dst()
        offset_hours = eastern.offset_hours
        eastern_naive = eastern.naive()
        eastern_str = eastern.format("YYYY-MM-DD HH:mm:ss")
        iso8601_eastern = eastern.isoformat()
    else:
        # Fallback to zoneinfo
        from zoneinfo import ZoneInfo

        et_tz = ZoneInfo("America/New_York")
        eastern_dt = utc_timestamp.astimezone(et_tz)

        # Determine DST
        # DST starts second Sunday in March at 2:00 AM
        # DST ends first Sunday in November at 2:00 AM
        is_dst = _is_dst(eastern_dt)
        offset_hours = -4 if is_dst else -5
        eastern_naive = eastern_dt.replace(tzinfo=None)
        eastern_str = eastern_naive.strftime("%Y-%m-%d %H:%M:%S")
        iso8601_eastern = eastern_dt.isoformat()

    timezone_name = "EDT" if is_dst else "EST"

    return EasternTimestamp(
        utc=utc_timestamp,
        eastern=eastern_naive,
        eastern_str=eastern_str,
        is_dst=is_dst,
        timezone_name=timezone_name,
        offset_hours=offset_hours,
        iso8601_utc=utc_timestamp.isoformat(),
        iso8601_eastern=iso8601_eastern,
    )


def _is_dst(dt: datetime) -> bool:
    """
    Determine if a datetime is in Daylight Saving Time.

    DST in US Eastern Time:
    - Starts: Second Sunday in March at 2:00 AM
    - Ends: First Sunday in November at 2:00 AM

    Args:
        dt: datetime in Eastern Time zone

    Returns:
        True if DST is active
    """
    # DST starts second Sunday in March
    # DST ends first Sunday in November
    year = dt.year

    # Find second Sunday in March
    march_first = datetime(year, 3, 1)
    days_until_sunday = (6 - march_first.weekday()) % 7
    first_sunday_march = march_first + timedelta(days=days_until_sunday)
    second_sunday_march = first_sunday_march + timedelta(days=7)
    dst_start = second_sunday_march.replace(hour=2, minute=0, second=0)

    # Find first Sunday in November
    november_first = datetime(year, 11, 1)
    days_until_sunday = (6 - november_first.weekday()) % 7
    first_sunday_november = november_first + timedelta(days=days_until_sunday)
    dst_end = first_sunday_november.replace(hour=2, minute=0, second=0)

    # Compare (use naive datetime for comparison)
    dt_naive = dt.replace(tzinfo=None) if dt.tzinfo else dt

    return dst_start <= dt_naive < dst_end


def format_evidence_timestamp(utc_timestamp: datetime) -> str:
    """
    Format evidence timestamp for display.

    Args:
        utc_timestamp: UTC datetime

    Returns:
        Formatted string like "2024-07-15 10:30:00 EDT (UTC-4)"

    Example:
        >>> from datetime import datetime, timezone
        >>> utc = datetime(2024, 7, 15, 14, 30, tzinfo=timezone.utc)
        >>> print(format_evidence_timestamp(utc))
        '2024-07-15 10:30:00 EDT (UTC-4)'
    """
    et = convert_to_eastern(utc_timestamp)
    sign = "+" if et.offset_hours > 0 else ""
    return f"{et.eastern_str} {et.timezone_name} (UTC{sign}{et.offset_hours})"


def format_evidence_timestamp_short(utc_timestamp: datetime) -> str:
    """
    Format evidence timestamp in short format.

    Args:
        utc_timestamp: UTC datetime

    Returns:
        Formatted string like "07/15/2024 10:30 AM EDT"
    """
    et = convert_to_eastern(utc_timestamp)
    hour = et.eastern.hour
    am_pm = "AM" if hour < 12 else "PM"
    hour_12 = hour if hour <= 12 else hour - 12
    hour_12 = 12 if hour_12 == 0 else hour_12
    return f"{et.eastern.month:02d}/{et.eastern.day:02d}/{et.eastern.year} {hour_12}:{et.eastern.minute:02d} {am_pm} {et.timezone_name}"


def get_dst_transition_dates(year: int) -> Dict[str, datetime]:
    """
    Get DST transition dates for a given year.

    Args:
        year: Year to get transition dates for

    Returns:
        Dict with 'dst_start' and 'dst_end' keys

    Example:
        >>> transitions = get_dst_transition_dates(2024)
        >>> print(transitions['dst_start'])
        datetime(2024, 3, 10, 2, 0)
    """
    # DST starts second Sunday in March at 2:00 AM
    march_first = datetime(year, 3, 1)
    days_until_sunday = (6 - march_first.weekday()) % 7
    first_sunday_march = march_first + timedelta(days=days_until_sunday)
    second_sunday_march = first_sunday_march + timedelta(days=7)
    dst_start = second_sunday_march.replace(hour=2, minute=0, second=0)

    # DST ends first Sunday in November at 2:00 AM
    november_first = datetime(year, 11, 1)
    days_until_sunday = (6 - november_first.weekday()) % 7
    first_sunday_november = november_first + timedelta(days=days_until_sunday)
    dst_end = first_sunday_november.replace(hour=2, minute=0, second=0)

    return {
        "dst_start": dst_start,
        "dst_end": dst_end,
        "dst_start_str": dst_start.strftime("%Y-%m-%d %H:%M:%S"),
        "dst_end_str": dst_end.strftime("%Y-%m-%d %H:%M:%S"),
    }


def create_timestamp_range(start_utc: datetime, end_utc: datetime) -> TimestampRange:
    """
    Create a timestamp range with Eastern Time conversions.

    Args:
        start_utc: Start timestamp in UTC
        end_utc: End timestamp in UTC

    Returns:
        TimestampRange with conversions and DST info
    """
    start_eastern = convert_to_eastern(start_utc)
    end_eastern = convert_to_eastern(end_utc)

    duration = (end_utc - start_utc).total_seconds()
    crosses_dst = start_eastern.is_dst != end_eastern.is_dst

    return TimestampRange(
        start_utc=start_utc,
        end_utc=end_utc,
        start_eastern=start_eastern,
        end_eastern=end_eastern,
        duration_seconds=duration,
        crosses_dst_boundary=crosses_dst,
    )


def batch_convert_to_eastern(utc_timestamps: List[datetime]) -> List[EasternTimestamp]:
    """
    Convert multiple timestamps to Eastern Time.

    Args:
        utc_timestamps: List of UTC datetimes

    Returns:
        List of EasternTimestamp objects
    """
    return [convert_to_eastern(ts) for ts in utc_timestamps]


def now_eastern() -> EasternTimestamp:
    """
    Get current time in Eastern Time.

    Returns:
        EasternTimestamp for current time
    """
    return convert_to_eastern(datetime.now(timezone.utc))


# MCP Tool Functions


def mcp_convert_to_eastern(utc_timestamp_iso: str) -> Dict[str, Any]:
    """
    MCP Tool: Convert UTC timestamp to Eastern Time.

    Args:
        utc_timestamp_iso: ISO 8601 UTC timestamp string

    Returns:
        Dict with conversion details
    """
    try:
        # Parse ISO 8601 timestamp
        if utc_timestamp_iso.endswith("Z"):
            utc_timestamp_iso = utc_timestamp_iso[:-1] + "+00:00"

        utc_timestamp = datetime.fromisoformat(utc_timestamp_iso)

        # Ensure UTC
        if utc_timestamp.tzinfo is None:
            utc_timestamp = utc_timestamp.replace(tzinfo=timezone.utc)

        et = convert_to_eastern(utc_timestamp)

        return {
            "success": True,
            "utc": et.iso8601_utc,
            "eastern": et.iso8601_eastern,
            "eastern_str": et.eastern_str,
            "timezone_name": et.timezone_name,
            "is_dst": et.is_dst,
            "offset_hours": et.offset_hours,
            "formatted": format_evidence_timestamp(utc_timestamp),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def mcp_get_dst_transitions(year: int) -> Dict[str, Any]:
    """
    MCP Tool: Get DST transition dates for a year.

    Args:
        year: Year to get transitions for

    Returns:
        Dict with transition dates
    """
    try:
        transitions = get_dst_transition_dates(year)

        return {
            "success": True,
            "year": year,
            "dst_start": transitions["dst_start_str"],
            "dst_end": transitions["dst_end_str"],
            "dst_start_utc": transitions["dst_start"].isoformat(),
            "dst_end_utc": transitions["dst_end"].isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def mcp_now_eastern() -> Dict[str, Any]:
    """
    MCP Tool: Get current time in Eastern Time.

    Returns:
        Dict with current time in both UTC and Eastern
    """
    try:
        et = now_eastern()

        return {
            "success": True,
            "utc": et.iso8601_utc,
            "eastern": et.iso8601_eastern,
            "eastern_str": et.eastern_str,
            "timezone_name": et.timezone_name,
            "is_dst": et.is_dst,
            "offset_hours": et.offset_hours,
            "formatted": format_evidence_timestamp(et.utc),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Export for MCP registration
__all__ = [
    # Enums
    "TimezoneName",
    # Models
    "EasternTimestamp",
    "TimestampRange",
    # Functions
    "convert_to_eastern",
    "format_evidence_timestamp",
    "format_evidence_timestamp_short",
    "get_dst_transition_dates",
    "create_timestamp_range",
    "batch_convert_to_eastern",
    "now_eastern",
    # MCP Tools
    "mcp_convert_to_eastern",
    "mcp_get_dst_transitions",
    "mcp_now_eastern",
]
