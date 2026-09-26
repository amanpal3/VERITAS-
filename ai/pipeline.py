"""
VERITAS - Master AI Processing Pipeline
Orchestrates ingestion, preprocessing, hybrid NER extraction, relationship extraction,
entity resolution, relationship rewriting, and explainable anomaly detection into a unified
canonical intelligence result.
Provides a clean programmatic interface for Member 2 / Backend and investigative consumers.
Conforms strictly to docs/DATA_SCHEMA.md, docs/GRAPH_SCHEMA.md, and docs/API_CONTRACT.md.
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field

from ai.anomaly.detector import AnomalyDetector, AnomalyResult
from ai.extraction.ner import EntityExtractor, EntityIDGenerator
from ai.extraction.relation_extractor import RelationshipExtractor, RelationshipIDGenerator
from ai.ingestion.csv_parser import (
    CDRParser,
    CDRRecord,
    TransactionParser,
    TransactionRecord,
    load_cdrs_csv,
    load_transactions_csv,
)
from ai.ingestion.document_parser import (
    DocumentParser,
    DocumentRecord,
    load_document,
    load_documents_dir,
)
from ai.resolution.entity_resolver import EntityResolver, ResolutionEvidence
from ai.schemas.entity import Entity
from ai.schemas.relationship import Relationship

logger = logging.getLogger(__name__)


class PipelineMetadata(BaseModel):
    """
    Diagnostic and operational audit metrics recorded during pipeline execution.
    """
    model_config = ConfigDict(extra="allow")

    records_processed: int = Field(0, description="Total raw or parsed input records ingested")
    entity_count_raw: int = Field(0, description="Total entities extracted before cross-record resolution")
    entity_count: int = Field(0, description="Total canonical entities after resolution and deduplication")
    relationship_count_raw: int = Field(0, description="Total relationships extracted before rewriting")
    relationship_count: int = Field(0, description="Total canonical relationships after endpoint rewriting")
    anomaly_count: int = Field(0, description="Total explainable behavioral anomalies flagged")
    resolution_merge_count: int = Field(0, description="Total entity pairs merged into canonical nodes")
    status: str = Field("SUCCESS", description="Overall pipeline execution status ('SUCCESS' or 'PARTIAL')")


class PipelineResult(BaseModel):
    """
    Canonical End-to-End Intelligence Pipeline Result.
    Encapsulates resolved entities, rewritten relationships, explainable anomalies,
    resolution audit evidence, and operational metadata.
    Serializes directly to standard JSON adhering to project contracts.
    """
    model_config = ConfigDict(extra="allow")

    entities: List[Entity] = Field(default_factory=list, description="Canonical resolved investigative entities")
    relationships: List[Relationship] = Field(default_factory=list, description="Multi-relational graph edges with rewritten endpoints")
    anomalies: List[AnomalyResult] = Field(default_factory=list, description="Explainable behavioral anomaly detections")
    resolution_evidence: List[ResolutionEvidence] = Field(default_factory=list, description="Audit trail of pairwise candidate comparisons")
    pipeline_metadata: PipelineMetadata = Field(default_factory=PipelineMetadata, description="Execution metrics and audit statistics")

    def to_dict(self) -> Dict[str, Any]:
        """Returns standard Python dictionary representation."""
        return self.model_dump()

    def to_json(self, indent: int = 2) -> str:
        """Serializes pipeline result to formatted JSON string."""
        return self.model_dump_json(indent=indent)


class IntelligencePipeline:
    """
    Master AI/NLP Orchestrator (Member 1).
    Executes the 8-stage deterministic end-to-end intelligence extraction pipeline:
      Stage 1: Ingest raw records (DocumentRecord, CDRRecord, TransactionRecord, or directory paths).
      Stage 2: Deterministic sanitization and normalization.
      Stage 3: Hybrid NER entity extraction.
      Stage 4: Semantic multi-relational edge extraction.
      Stage 5: Multi-signal entity resolution & clustering.
      Stage 6: Relationship endpoint rewriting with structured event preservation.
      Stage 7: Explainable statistical anomaly detection.
      Stage 8: Construction of canonical serializable PipelineResult.
    """

    def __init__(
        self,
        use_spacy: bool = True,
        entity_id_generator: Optional[EntityIDGenerator] = None,
        rel_id_generator: Optional[RelationshipIDGenerator] = None,
        entity_resolver: Optional[EntityResolver] = None,
        anomaly_detector: Optional[AnomalyDetector] = None,
    ):
        self.entity_id_generator = entity_id_generator or EntityIDGenerator()
        self.rel_id_generator = rel_id_generator or RelationshipIDGenerator()

        self.ner_extractor = EntityExtractor(use_spacy=use_spacy)
        self.ner_extractor.id_generator = self.entity_id_generator

        self.relation_extractor = RelationshipExtractor(id_generator=self.rel_id_generator)
        self.entity_resolver = entity_resolver or EntityResolver()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()

        self.document_parser = DocumentParser()
        self.cdr_parser = CDRParser()
        self.transaction_parser = TransactionParser()

    def run(
        self,
        records: Optional[List[Any]] = None,
        raw_data_path: Optional[Union[str, Path]] = None,
    ) -> PipelineResult:
        """
        Executes end-to-end extraction across provided records and/or filesystem paths.
        Handles empty, sparse, or heterogeneous inputs safely.
        """
        all_records: List[Any] = []
        if records:
            all_records.extend(records)

        # Ingest from path if provided
        if raw_data_path:
            loaded = self._load_from_path(raw_data_path)
            all_records.extend(loaded)

        if not all_records:
            return PipelineResult(
                entities=[],
                relationships=[],
                anomalies=[],
                resolution_evidence=[],
                pipeline_metadata=PipelineMetadata(
                    records_processed=0,
                    entity_count_raw=0,
                    entity_count=0,
                    relationship_count_raw=0,
                    relationship_count=0,
                    anomaly_count=0,
                    resolution_merge_count=0,
                    status="SUCCESS",
                ),
            )

        # Stage 1 & 2: Parse / Ingest and Normalize
        standardized_records, record_errors = self._standardize_inputs(all_records)

        # Stage 3: Entity Extraction
        raw_entities: List[Entity] = []
        for rec in standardized_records:
            try:
                ents = self.ner_extractor.extract_from_record(rec)
                raw_entities.extend(ents)
            except Exception as e:
                logger.warning(f"Error extracting entities from record {rec}: {e}")

        # Stage 4: Relationship Extraction
        raw_relationships: List[Relationship] = []
        for rec in standardized_records:
            try:
                rels = self.relation_extractor.extract_from_record(rec, entities=raw_entities)
                raw_relationships.extend(rels)
            except Exception as e:
                logger.warning(f"Error extracting relationships from record {rec}: {e}")

        # Stage 5 & 6: Entity Resolution & Relationship Rewriting
        resolved_entities, rewritten_relationships, resolution_evidence = (
            self.entity_resolver.resolve_with_relationships(
                entities=raw_entities,
                relationships=raw_relationships,
            )
        )

        # Stage 7: Anomaly Detection
        anomalies = self.anomaly_detector.detect(
            entities=resolved_entities,
            relationships=rewritten_relationships,
            records=standardized_records,
        )

        # Stage 8: Unified Canonical Result
        merge_count = len(raw_entities) - len(resolved_entities)
        status = "SUCCESS" if not record_errors else "PARTIAL"

        metadata = PipelineMetadata(
            records_processed=len(standardized_records),
            entity_count_raw=len(raw_entities),
            entity_count=len(resolved_entities),
            relationship_count_raw=len(raw_relationships),
            relationship_count=len(rewritten_relationships),
            anomaly_count=len(anomalies),
            resolution_merge_count=max(0, merge_count),
            status=status,
        )

        return PipelineResult(
            entities=resolved_entities,
            relationships=rewritten_relationships,
            anomalies=anomalies,
            resolution_evidence=resolution_evidence,
            pipeline_metadata=metadata,
        )

    # -----------------------------------------------------------------
    # Ingestion & Standardization Helpers
    # -----------------------------------------------------------------

    def _load_from_path(self, path: Union[str, Path]) -> List[Any]:
        """Loads records from a single file or directory structure."""
        p = Path(path)
        if not p.exists():
            logger.error(f"Path does not exist: {path}")
            return []

        loaded: List[Any] = []
        if p.is_file():
            loaded.extend(self._load_single_file(p))
        elif p.is_dir():
            # Check for subdirectories like firs/
            firs_dir = p / "firs"
            if firs_dir.exists() and firs_dir.is_dir():
                docs = load_documents_dir(firs_dir)
                loaded.extend(docs)

            # Check for cdrs.csv
            cdrs_file = p / "cdrs.csv"
            if cdrs_file.exists() and cdrs_file.is_file():
                cdrs = load_cdrs_csv(cdrs_file)
                loaded.extend(cdrs)

            # Check for transactions.csv
            tx_file = p / "transactions.csv"
            if tx_file.exists() and tx_file.is_file():
                txs = load_transactions_csv(tx_file)
                loaded.extend(txs)

            # If no standard sub-files found, scan all .txt and .csv in the directory
            if not loaded:
                for file_path in p.glob("*"):
                    if file_path.is_file():
                        loaded.extend(self._load_single_file(file_path))

        return loaded

    def _load_single_file(self, file_path: Path) -> List[Any]:
        suffix = file_path.suffix.lower()
        if suffix in {".txt", ".pdf"}:
            doc = load_document(file_path)
            return [doc] if doc else []
        elif suffix == ".csv":
            # Inspect header to determine CDR vs Transaction
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    first_line = f.readline().lower()
                if "call_id" in first_line or "msisdn" in first_line:
                    cdrs = load_cdrs_csv(file_path)
                    return cdrs
                elif "transaction_id" in first_line or "sender_account" in first_line:
                    txs = load_transactions_csv(file_path)
                    return txs
            except Exception as e:
                logger.error(f"Error reading CSV {file_path}: {e}")
        return []

    def _standardize_inputs(self, raw_items: List[Any]) -> Tuple[List[Any], int]:
        """
        Converts heterogeneous inputs (DocumentRecord, CDRRecord, TransactionRecord,
        raw strings, dicts) into validated typed ingestion records.
        """
        standardized: List[Any] = []
        errors = 0

        for idx, item in enumerate(raw_items):
            if isinstance(item, (DocumentRecord, CDRRecord, TransactionRecord)):
                standardized.append(item)
            elif isinstance(item, str):
                # Raw text treated as police narrative report
                try:
                    doc = self.document_parser.parse_text(
                        text=item,
                        file_path="inline_document",
                        file_name=f"report_{idx+1:03d}.txt",
                    )
                    standardized.append(doc)
                except Exception:
                    errors += 1
            elif isinstance(item, dict):
                # Try inferring record type from dictionary keys
                if "call_id" in item or "caller_msisdn" in item:
                    try:
                        record = self.cdr_parser._parse_row(item, row_index=idx + 1)
                        standardized.append(record)
                    except Exception:
                        errors += 1
                elif "transaction_id" in item or "sender_account" in item:
                    try:
                        # Provide defaults for missing optional fields in loose dicts
                        dict_copy = {k: str(v) for k, v in item.items()}
                        dict_copy.setdefault("payment_channel", "RTGS")
                        dict_copy.setdefault("currency", "INR")
                        dict_copy.setdefault("timestamp", "2026-03-01T00:00:00Z")
                        record = self.transaction_parser._parse_row(dict_copy, row_index=idx + 1)
                        standardized.append(record)
                    except Exception:
                        errors += 1
                elif "raw_text" in item or "content" in item or "text" in item:
                    text_content = item.get("raw_text") or item.get("content") or item.get("text", "")
                    try:
                        doc = self.document_parser.parse_text(
                            text=text_content,
                            file_path=item.get("file_path", "inline_document"),
                            file_name=item.get("file_name", f"doc_{idx+1:03d}.txt"),
                        )
                        standardized.append(doc)
                    except Exception:
                        errors += 1
                else:
                    errors += 1
            else:
                errors += 1

        return standardized, errors
