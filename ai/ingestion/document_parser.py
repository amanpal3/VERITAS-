"""
VERITAS - Document and FIR Ingestion Parser
Reads and structures unstructured police complaints, FIRs, forensic audits,
and field surveillance reports. Preserves raw text, identifies structural sections,
and derives stable source citations without executing NER.
"""
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from ai.ingestion.preprocessing import clean_text, normalize_timestamp


class DocumentRecord(BaseModel):
    """
    Structured representation of an ingested document or police report.
    Guarantees raw text preservation and provenance attribution.
    """
    source_id: str = Field(..., description="Stable source identifier (e.g. FIR-104/2026, INT-DEL-2026-409)")
    file_path: str = Field(..., description="Absolute or relative file path on disk")
    file_name: str = Field(..., description="Original filename")
    document_type: str = Field(..., description="Category: POLICE_REPORT, SURVEILLANCE, AUDIT, INTEL_BRIEF")
    title: str = Field(default="", description="Header title or report heading")
    raw_text: str = Field(..., description="100% complete unmodified text content")
    cleaned_text: str = Field(default="", description="Sanitized text with normalized whitespace")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extracted header metadata (Station, Crime No, Sections, Date)")
    sections: Dict[str, str] = Field(default_factory=dict, description="Identified body sections (summary, narrative, signoff)")
    date_str: Optional[str] = Field(default=None, description="Raw date string found in document header")
    normalized_timestamp: Optional[str] = Field(default=None, description="Standardized ISO-8601 UTC or offset timestamp")


class DocumentParser:
    """
    Parses unstructured .txt and narrative reports into typed DocumentRecord instances.
    """

    @classmethod
    def parse_file(cls, file_path: Union[str, Path]) -> DocumentRecord:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file does not exist: {file_path}")
        if not path.is_file():
            raise ValueError(f"Path is not a regular file: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {e}")

        if not content.strip():
            raise ValueError(f"Document is empty: {file_path}")

        return cls.parse_text(content, file_path=str(path), file_name=path.name)

    @classmethod
    def parse_text(
        cls,
        text: str,
        file_path: str = "inline_document",
        file_name: str = "inline.txt"
    ) -> DocumentRecord:
        if not text or not text.strip():
            raise ValueError("Cannot parse empty text.")

        raw = text
        cleaned = clean_text(raw)
        lines = [line.strip() for line in raw.split("\n") if line.strip()]

        # 1. Determine Title and Header lines
        title = lines[0] if lines else "UNTITLED REPORT"

        # 2. Derive stable source_id and document_type
        source_id, doc_type = cls._extract_source_identity(raw, file_name)

        # 3. Extract header metadata
        metadata = cls._extract_metadata(raw)

        # 4. Identify structural sections
        sections = cls._segment_sections(raw)

        # 5. Extract timestamp
        date_str = metadata.get("date") or metadata.get("date_and_time") or metadata.get("date_of_audit")
        normalized_ts = normalize_timestamp(date_str) if date_str else None

        return DocumentRecord(
            source_id=source_id,
            file_path=file_path,
            file_name=file_name,
            document_type=doc_type,
            title=title,
            raw_text=raw,
            cleaned_text=cleaned,
            metadata=metadata,
            sections=sections,
            date_str=date_str,
            normalized_timestamp=normalized_ts,
        )

    @classmethod
    def parse_directory(cls, dir_path: Union[str, Path]) -> List[DocumentRecord]:
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        records = []
        # Case-insensitively collect unique .txt files
        seen_paths = set()
        files = []
        for f in path.iterdir():
            if f.is_file() and f.suffix.lower() == ".txt":
                resolved = f.resolve()
                if resolved not in seen_paths:
                    seen_paths.add(resolved)
                    files.append(f)
        files.sort(key=lambda p: p.name)
        for f in files:
            records.append(cls.parse_file(f))
        return records

    @staticmethod
    def _extract_source_identity(raw_text: str, file_name: str) -> tuple[str, str]:
        """
        Derives stable source ID and document category from header patterns.
        """
        # FIR Pattern: CRIME NO: 104/2026 -> FIR-104/2026
        fir_match = re.search(r"CRIME\s+NO[:\s]+([0-9]+/[0-9]{4})", raw_text, re.IGNORECASE)
        if fir_match:
            return f"FIR-{fir_match.group(1)}", "POLICE_REPORT"

        # Intelligence Report Pattern: INT-DEL-2026-409
        int_match = re.search(r"(?:REPORT|BRIEF)[:\s]+([A-Z0-9\-]+(?:DEL|INT|SURV|EOW)[A-Z0-9\-]*)", raw_text, re.IGNORECASE)
        if int_match:
            return int_match.group(1).strip(), "SURVEILLANCE"

        # General Document ID Pattern: SURV-2026-031, FIN-EOW-2026-092
        code_match = re.search(r"\b([A-Z]{3,5}-[A-Z0-9\-]+)\b", raw_text)
        if code_match:
            code = code_match.group(1)
            doc_type = "AUDIT" if "FIN" in code or "EOW" in code else "SURVEILLANCE"
            return code, doc_type

        # Fallback to filename stem
        stem = Path(file_name).stem
        if "FIR" in stem.upper():
            return stem, "POLICE_REPORT"
        if "SURV" in stem.upper():
            return stem, "SURVEILLANCE"
        if "AUDIT" in stem.upper() or "FIN" in stem.upper():
            return stem, "AUDIT"
        return stem, "DOCUMENT"

    @staticmethod
    def _extract_metadata(raw_text: str) -> Dict[str, Any]:
        """
        Extracts key-value header pairs commonly present in FIRs and intelligence briefs.
        """
        metadata: Dict[str, Any] = {}
        # Explicit pattern check for CRIME NO
        crime_match = re.search(r"CRIME\s+NO[:\s]+([0-9]+/[0-9]{4})", raw_text, re.IGNORECASE)
        if crime_match:
            metadata["crime_no"] = crime_match.group(1).strip()

        for line in raw_text.split("\n"):
            line_str = line.strip()
            if ":" in line_str:
                parts = line_str.split(":", 1)
                key = parts[0].strip().lower().replace(" ", "_").replace("&", "and")
                val = parts[1].strip()
                if key in {
                    "police_station",
                    "crime_no",
                    "date_and_time_of_report",
                    "date",
                    "date_of_audit",
                    "sections_applied",
                    "agency",
                    "subject",
                    "location",
                    "dates",
                }:
                    metadata[key] = val
        return metadata

    @staticmethod
    def _segment_sections(raw_text: str) -> Dict[str, str]:
        """
        Partitions narrative document into identified body headings.
        """
        sections: Dict[str, str] = {}
        current_heading = "header"
        current_lines: List[str] = []

        known_headings = {
            "INCIDENT SUMMARY",
            "OPERATIONAL SUMMARY",
            "OBSERVATION CHRONOLOGY",
            "EXECUTIVE FINDINGS",
            "INVESTIGATING OFFICER",
            "AUTHOR",
            "CONCLUSION",
            "BANKING FOOTPRINT",
            "KEY SHAREHOLDERS",
        }

        for line in raw_text.split("\n"):
            stripped = line.strip().rstrip(":")
            if stripped.upper() in known_headings:
                if current_lines:
                    sections[current_heading] = "\n".join(current_lines).strip()
                current_heading = stripped.lower().replace(" ", "_")
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            sections[current_heading] = "\n".join(current_lines).strip()

        return sections


# Convenience module function
def load_document(file_path: Union[str, Path]) -> DocumentRecord:
    return DocumentParser.parse_file(file_path)


def load_documents_dir(dir_path: Union[str, Path]) -> List[DocumentRecord]:
    return DocumentParser.parse_directory(dir_path)
