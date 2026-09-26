"""
VERITAS - Text and Field Preprocessing & Deterministic Normalization
Provides standard sanitization and canonical normalization for phone numbers,
vehicle registration numbers, timestamps, person names, organizations, and accounts.
Strictly adheres to project conventions established in docs/DATA_SCHEMA.md.
"""
import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple


# Indian timezone definition: IST is UTC+05:30
IST = timezone(timedelta(hours=5, minutes=30))

TZ_MAPPING = {
    "IST": IST,
    "UTC": timezone.utc,
    "GMT": timezone.utc,
    "Z": timezone.utc,
}


def clean_text(text: str) -> str:
    """
    Sanitizes raw text: strips non-printable control characters,
    normalizes Unicode whitespace, and trims leading/trailing spaces.
    """
    if not text:
        return ""
    # Normalize carriage returns and tabs
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace non-breaking spaces and redundant horizontal whitespace
    text = re.sub(r"[^\S\n]+", " ", text)
    return text.strip()


def normalize_phone_number(phone: str, default_country_code: str = "+91") -> Optional[str]:
    """
    Normalizes phone numbers to standard E.164 format (+919811010001).
    Handles national formats, leading zeros, separators (spaces, hyphens, parentheses),
    and country code variants (91, 0, +91).
    Preserves valid international numbers.
    Returns None if input cannot be resolved to a valid phone format.
    """
    if not phone or not isinstance(phone, str):
        return None

    cleaned = phone.strip()
    if not cleaned:
        return None

    has_plus = cleaned.startswith("+")

    # Extract digits only
    digits = re.sub(r"\D", "", cleaned)
    if not digits:
        return None

    # Case 1: Indian Mobile Number (10 digits starting with 6, 7, 8, 9)
    if len(digits) == 10 and digits[0] in "6789":
        return f"{default_country_code}{digits}"

    # Case 2: Indian number with leading 0 (11 digits: 0 + 10 digits)
    if len(digits) == 11 and digits.startswith("0") and digits[1] in "6789":
        return f"{default_country_code}{digits[1:]}"

    # Case 3: Indian number with 91 prefix (12 digits starting with 91)
    if len(digits) == 12 and digits.startswith("91") and digits[2] in "6789":
        return f"+{digits}"

    # Case 4: International number with explicit '+' in original string
    if has_plus and 7 <= len(digits) <= 15:
        return f"+{digits}"

    # Case 5: 10-15 digit string without '+'
    if 10 <= len(digits) <= 15:
        if has_plus:
            return f"+{digits}"
        # If it looks like Indian 10-digit but maybe didn't match leading digit strictly
        if len(digits) == 10:
            return f"{default_country_code}{digits}"
        return f"+{digits}"

    return None


def normalize_vehicle_plate(plate: str) -> Optional[str]:
    """
    Normalizes Indian vehicle registration plates into canonical hyphenated format (e.g. DL-1M-4412).
    Standardizes casing, strips surrounding model descriptions, and standardizes spacing/hyphens.
    """
    if not plate or not isinstance(plate, str):
        return None

    cleaned = plate.strip().upper()
    if not cleaned:
        return None

    # If format includes descriptive model suffix like "DL-1C-0001 (BMW 7-Series)",
    # extract the registration plate part before the parenthesis
    match_with_desc = re.match(r"^([A-Za-z0-9\s\-]+?)(?:\s*\((.*?)\))?$", plate.strip())
    desc = ""
    if match_with_desc:
        plate_part = match_with_desc.group(1).strip().upper()
        desc = match_with_desc.group(2).strip() if match_with_desc.group(2) else ""
    else:
        plate_part = plate.strip().upper()

    # Match standard Indian registration: e.g. DL-1M-4412, DL 1C 0001, DL-01-M-4412, HR-26-DK-8392
    # State (2 chars), District/series (1-3 alphanumeric), Number (1-4 digits)
    pattern = re.compile(
        r"^([A-Z]{2})[\s\-]*([0-9]{1,2})?[\s\-]*([A-Z]{1,3})?[\s\-]*([0-9]{1,4})$"
    )
    match = pattern.match(plate_part)

    if match:
        state = match.group(1)
        rto_num = match.group(2) or ""
        series = match.group(3) or ""
        num = match.group(4) or ""

        # Format number with leading zero if standard 4 digits
        if len(num) < 4 and len(num) > 0 and (rto_num or series):
            num_padded = num.zfill(4)
        else:
            num_padded = num

        mid_parts = [p for p in [rto_num, series] if p]
        mid = "".join(mid_parts)
        if mid and num_padded:
            canonical_plate = f"{state}-{mid}-{num_padded}"
        elif mid:
            canonical_plate = f"{state}-{mid}"
        else:
            canonical_plate = f"{state}-{num_padded}"

        if desc:
            return f"{canonical_plate} ({desc.strip()})"
        return canonical_plate

    # Fallback: clean multiple spaces/dashes into single hyphens
    normalized = re.sub(r"[\s_]+", "-", plate_part)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    if desc:
        return f"{normalized} ({desc.strip()})"
    return normalized


def normalize_timestamp(ts_str: str) -> Optional[str]:
    """
    Converts timestamps to standard ISO-8601 representation.
    Preserves timezone information where available (converting named zones like IST).
    Does NOT silently assume or guess UTC if timezone is missing (preserves naive ISO).
    """
    if not ts_str or not isinstance(ts_str, str):
        return None

    cleaned = ts_str.strip()
    if not cleaned:
        return None

    # Check for trailing named timezones like IST, UTC, GMT
    # e.g. "12-FEB-2026 23:45 IST", "24-FEB-2026 18:20 IST"
    named_tz_match = re.search(r"\b(IST|UTC|GMT)\b", cleaned, re.IGNORECASE)
    tz_info = None
    if named_tz_match:
        tz_name = named_tz_match.group(1).upper()
        tz_info = TZ_MAPPING.get(tz_name)
        cleaned = cleaned[: named_tz_match.start()] + cleaned[named_tz_match.end() :]
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Try ISO formats first: e.g. "2026-03-01T14:22:10Z", "2026-03-01T14:22:10+05:30"
    try:
        # If ending in Z, fromisoformat in Python 3.11+ handles it directly
        dt = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
        if tz_info and dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz_info)
        # If UTC, return with Z
        if dt.tzinfo == timezone.utc:
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        return dt.isoformat()
    except ValueError:
        pass

    # Try specific common formats
    known_formats = [
        ("%d-%b-%Y %H:%M:%S", False),
        ("%d-%b-%Y %H:%M", False),
        ("%d-%B-%Y %H:%M:%S", False),
        ("%d-%B-%Y %H:%M", False),
        ("%Y-%m-%d %H:%M:%S", False),
        ("%Y-%m-%d %H:%M", False),
        ("%Y/%m/%d %H:%M:%S", False),
        ("%d/%m/%Y %H:%M:%S", False),
        ("%d/%m/%Y %H:%M", False),
        ("%Y-%m-%d", False),
    ]

    for fmt, _ in known_formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            if tz_info:
                dt = dt.replace(tzinfo=tz_info)
                return dt.isoformat()
            # Naive timestamp - preserve without guessing timezone
            return dt.isoformat()
        except ValueError:
            continue

    # Return None if unparseable
    return None


def normalize_name(name: str) -> str:
    """
    Conservative person name normalization:
    - Strips surrounding quotes, whitespace, and honors title casing.
    - Preserves meaningful initials, titles, and lineage tokens (e.g. S/o, S/O).
    """
    if not name or not isinstance(name, str):
        return ""

    cleaned = name.strip()
    # Strip quotes
    cleaned = cleaned.strip("\"'“”‘’")
    # Normalize multiple whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # If ALL UPPERCASE or all lowercase, apply title casing thoughtfully
    if cleaned.isupper() or cleaned.islower():
        words = cleaned.split()
        capitalized = []
        for w in words:
            # Preserve S/o, D/o, W/o markers
            if w.upper() in {"S/O", "D/O", "W/O"}:
                capitalized.append("S/o")
            elif "/" in w:
                capitalized.append(w.upper())
            else:
                capitalized.append(w.capitalize())
        return " ".join(capitalized)

    return cleaned


def normalize_org_name(org_name: str) -> str:
    """
    Conservative organization name normalization:
    - Normalizes common corporate suffix punctuation (e.g. Ltd., LTD -> Ltd).
    - Preserves legal entities (LLP, Inc, Pvt, Ltd).
    """
    if not org_name or not isinstance(org_name, str):
        return ""

    cleaned = org_name.strip().strip("\"'“”‘’")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    words = cleaned.split()
    cap_words = []
    for w in words:
        w_upper = w.upper().rstrip(".")
        if w_upper in {"LTD", "LIMITED"}:
            cap_words.append("Ltd")
        elif w_upper in {"PVT", "PRIVATE"}:
            cap_words.append("Pvt")
        elif w_upper in {"INC", "INCORPORATED"}:
            cap_words.append("Inc")
        elif w_upper in {"LLP", "MCA", "CIN", "EOW", "FIU"}:
            cap_words.append(w_upper)
        elif w.isupper() or w.islower():
            cap_words.append(w.capitalize())
        else:
            cap_words.append(w)
    return " ".join(cap_words)


def normalize_account_id(account_id: str) -> str:
    """
    Normalizes bank account identifiers:
    - Converts to standard uppercase hyphenated format (e.g. ACC-ASTRA-7701).
    - Normalizes underscores or whitespace to hyphens.
    """
    if not account_id or not isinstance(account_id, str):
        return ""

    cleaned = account_id.strip().upper()
    cleaned = re.sub(r"[\s_]+", "-", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned
