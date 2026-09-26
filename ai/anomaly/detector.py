"""
VERITAS - Explainable Anomaly Detection Layer
Detects unusual behavioral patterns across financial transactions, CDR telecom activity,
and knowledge graph structural topology using explainable statistical heuristics.
Adheres strictly to the principles of explainable, non-accusatory anomaly detection.
"""
from datetime import datetime
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field

from ai.ingestion.csv_parser import CDRRecord, TransactionRecord
from ai.schemas.entity import Entity, EntityType
from ai.schemas.relationship import Relationship


class AnomalySeverity(str, Enum):
    """
    Controlled severity classification reflecting statistical divergence strength,
    NOT criminal culpability.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AnomalyType(str, Enum):
    """
    Controlled vocabulary of explainable analytical anomaly indicators.
    """
    HIGH_TRANSACTION_AMOUNT = "HIGH_TRANSACTION_AMOUNT"
    HIGH_TRANSACTION_FREQUENCY = "HIGH_TRANSACTION_FREQUENCY"
    HIGH_CALL_FREQUENCY = "HIGH_CALL_FREQUENCY"
    BURST_ACTIVITY = "BURST_ACTIVITY"
    HIGH_CONNECTIVITY = "HIGH_CONNECTIVITY"
    CROSS_COMMUNITY_BRIDGE = "CROSS_COMMUNITY_BRIDGE"


class AnomalyResult(BaseModel):
    """
    Canonical Explainable Anomaly Result.
    Binds every flagged anomaly to its entity, quantitative score, severity level,
    observed feature metrics, and supporting record provenance.
    """
    model_config = ConfigDict(extra="allow")

    entity_id: str = Field(..., description="Target entity identifier flagged by anomaly rule")
    anomaly_type: AnomalyType = Field(..., description="Controlled category of behavioral anomaly")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized anomaly score in [0.0, 1.0] indicating relative statistical extremity"
    )
    severity: AnomalySeverity = Field(..., description="Categorical anomaly strength (LOW, MEDIUM, HIGH)")
    evidence: str = Field(..., description="Summary of quantitative evidence observed")
    explanation: str = Field(..., description="Human-readable plain language investigative explanation")
    supporting_record_ids: List[str] = Field(
        default_factory=list,
        description="IDs of underlying records (CDRs, Transactions, FIRs) providing ground-truth evidence"
    )
    feature_values: Dict[str, Any] = Field(
        default_factory=dict,
        description="Empirical feature metrics (e.g. amount, count, threshold, z_score)"
    )


class AnomalyDetector:
    """
    Explainable Anomaly Detection Engine.
    Evaluates:
    1. Financial records -> High amount outliers (IQR / Percentile), High transaction counts.
    2. Telecom CDRs -> High call frequency, Burst temporal activity concentration.
    3. Graph topology -> High node degree connectivity, Cross-community bridging.
    """

    def __init__(
        self,
        amount_percentile_threshold: float = 0.90,
        frequency_iqr_multiplier: float = 1.5,
        burst_window_seconds: int = 7200,  # 2 hours
        burst_min_events: int = 3,
        degree_percentile_threshold: float = 0.90,
    ):
        self.amount_percentile_threshold = amount_percentile_threshold
        self.frequency_iqr_multiplier = frequency_iqr_multiplier
        self.burst_window_seconds = burst_window_seconds
        self.burst_min_events = burst_min_events
        self.degree_percentile_threshold = degree_percentile_threshold

    def detect(
        self,
        entities: Optional[List[Entity]] = None,
        relationships: Optional[List[Relationship]] = None,
        records: Optional[List[Any]] = None,
    ) -> List[AnomalyResult]:
        """
        Executes all configured explainable anomaly detection passes.
        Handles empty or sparse inputs safely with zero unhandled exceptions.
        """
        entity_list = entities or []
        relationship_list = relationships or []
        record_list = records or []

        anomalies: List[AnomalyResult] = []

        # 1. Transaction-based anomalies
        anomalies.extend(self._detect_transaction_anomalies(entity_list, record_list, relationship_list))

        # 2. CDR-based anomalies (Call frequency & Burst activity)
        anomalies.extend(self._detect_cdr_anomalies(entity_list, record_list, relationship_list))

        # 3. Graph topology anomalies (High degree & Bridging)
        anomalies.extend(self._detect_graph_anomalies(entity_list, relationship_list))

        # Deterministic sorting: sort by (severity desc, score desc, entity_id, anomaly_type)
        severity_rank = {AnomalySeverity.HIGH: 3, AnomalySeverity.MEDIUM: 2, AnomalySeverity.LOW: 1}
        anomalies.sort(
            key=lambda a: (-severity_rank.get(a.severity, 0), -a.score, a.entity_id, a.anomaly_type.value)
        )

        return anomalies

    # -----------------------------------------------------------------
    # 1. Transaction Anomaly Detectors
    # -----------------------------------------------------------------

    def _detect_transaction_anomalies(
        self,
        entities: List[Entity],
        records: List[Any],
        relationships: List[Relationship],
    ) -> List[AnomalyResult]:
        anomalies: List[AnomalyResult] = []

        # Extract transaction items from records or relationship edges
        tx_items = self._extract_transactions(records, relationships)
        if not tx_items or len(tx_items) < 3:
            # Insufficient transactions for statistical baseline
            return anomalies

        amounts = [t["amount"] for t in tx_items]
        p90 = self._percentile(amounts, self.amount_percentile_threshold)
        p95 = self._percentile(amounts, 0.95)
        median_amount = self._percentile(amounts, 0.50)
        max_amount = max(amounts)

        # A. High Transaction Amount
        for tx in tx_items:
            amt = tx["amount"]
            if amt >= p90 and amt > 0:
                # Calculate normalized score [0.60, 1.00]
                if max_amount > p90:
                    normalized_score = 0.60 + 0.40 * ((amt - p90) / (max_amount - p90))
                else:
                    normalized_score = 0.85
                normalized_score = min(1.0, max(0.0, normalized_score))

                if amt >= p95:
                    severity = AnomalySeverity.HIGH
                elif amt >= p90:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW

                target_id = tx.get("sender_account") or tx.get("receiver_account") or tx["transaction_id"]
                explanation = (
                    f"Transaction amount of {tx.get('currency', 'INR')} {amt:,.2f} exceeds "
                    f"the {int(self.amount_percentile_threshold * 100)}th percentile ({tx.get('currency', 'INR')} {p90:,.2f}) "
                    f"of observed financial transactions (median: {tx.get('currency', 'INR')} {median_amount:,.2f})."
                )

                anomalies.append(
                    AnomalyResult(
                        entity_id=target_id,
                        anomaly_type=AnomalyType.HIGH_TRANSACTION_AMOUNT,
                        score=round(normalized_score, 3),
                        severity=severity,
                        evidence=f"Amount: {amt:,.2f} vs P90: {p90:,.2f}",
                        explanation=explanation,
                        supporting_record_ids=[tx["transaction_id"]],
                        feature_values={
                            "amount": amt,
                            "currency": tx.get("currency", "INR"),
                            "p90_threshold": round(p90, 2),
                            "p95_threshold": round(p95, 2),
                            "median_amount": round(median_amount, 2),
                            "sender_account": tx.get("sender_account"),
                            "receiver_account": tx.get("receiver_account"),
                        },
                    )
                )

        # B. High Transaction Frequency per Account
        account_tx_counts: Dict[str, int] = {}
        account_tx_ids: Dict[str, List[str]] = {}
        for tx in tx_items:
            for acc in [tx.get("sender_account"), tx.get("receiver_account")]:
                if acc:
                    account_tx_counts[acc] = account_tx_counts.get(acc, 0) + 1
                    account_tx_ids.setdefault(acc, []).append(tx["transaction_id"])

        if len(account_tx_counts) >= 3:
            counts = list(account_tx_counts.values())
            q25 = self._percentile(counts, 0.25)
            q75 = self._percentile(counts, 0.75)
            p90 = self._percentile(counts, 0.90)
            iqr = q75 - q25
            iqr_fence = q75 + (self.frequency_iqr_multiplier * iqr)
            # Use upper IQR fence, or P90 if skewed distribution inflates IQR
            freq_threshold = min(iqr_fence, p90) if p90 > q75 else iqr_fence
            max_count = max(counts)

            p95 = self._percentile(counts, 0.95)
            for acc, count in account_tx_counts.items():
                if count >= freq_threshold and count > q75:
                    if max_count > freq_threshold:
                        norm_score = 0.60 + 0.40 * ((count - freq_threshold) / (max_count - freq_threshold))
                    else:
                        norm_score = 0.85
                    norm_score = min(1.0, max(0.0, norm_score))

                    severity = AnomalySeverity.HIGH if (count >= p95 or count >= (freq_threshold + 0.5 * iqr) or count >= 1.5 * freq_threshold) else AnomalySeverity.MEDIUM
                    explanation = (
                        f"Account participated in {count} transactions, substantially exceeding "
                        f"the upper frequency anomaly threshold of {freq_threshold:.1f} transfers "
                        f"(Q75: {q75:.1f}, IQR: {iqr:.1f})."
                    )

                    anomalies.append(
                        AnomalyResult(
                            entity_id=acc,
                            anomaly_type=AnomalyType.HIGH_TRANSACTION_FREQUENCY,
                            score=round(norm_score, 3),
                            severity=severity,
                            evidence=f"Transaction count: {count} vs threshold: {freq_threshold:.1f}",
                            explanation=explanation,
                            supporting_record_ids=sorted(list(set(account_tx_ids[acc]))),
                            feature_values={
                                "transaction_count": count,
                                "q75": round(q75, 1),
                                "iqr": round(iqr, 1),
                                "iqr_threshold": round(freq_threshold, 1),
                            },
                        )
                    )

        return anomalies

    # -----------------------------------------------------------------
    # 2. CDR Telecom Anomaly Detectors
    # -----------------------------------------------------------------

    def _detect_cdr_anomalies(
        self,
        entities: List[Entity],
        records: List[Any],
        relationships: List[Relationship],
    ) -> List[AnomalyResult]:
        anomalies: List[AnomalyResult] = []

        cdrs = self._extract_cdrs(records, relationships)
        if not cdrs or len(cdrs) < 3:
            return anomalies

        # C. High Call Frequency per Phone Node
        phone_call_counts: Dict[str, int] = {}
        phone_call_ids: Dict[str, List[str]] = {}
        phone_timestamps: Dict[str, List[Tuple[datetime, str]]] = {}

        for c in cdrs:
            cid = c["call_id"]
            caller = c.get("caller_msisdn")
            receiver = c.get("receiver_msisdn")
            dt = self._parse_iso_timestamp(c.get("timestamp"))

            for p in [caller, receiver]:
                if p:
                    phone_call_counts[p] = phone_call_counts.get(p, 0) + 1
                    phone_call_ids.setdefault(p, []).append(cid)
                    if dt:
                        phone_timestamps.setdefault(p, []).append((dt, cid))

        if len(phone_call_counts) >= 3:
            counts = list(phone_call_counts.values())
            q25 = self._percentile(counts, 0.25)
            q75 = self._percentile(counts, 0.75)
            p90 = self._percentile(counts, 0.90)
            iqr = q75 - q25
            median_calls = self._percentile(counts, 0.50)
            iqr_fence = q75 + (self.frequency_iqr_multiplier * iqr)
            threshold = min(iqr_fence, p90) if p90 > q75 else iqr_fence
            max_calls = max(counts)

            p95 = self._percentile(counts, 0.95)
            for phone, count in phone_call_counts.items():
                if count >= threshold and count > q75:
                    if max_calls > threshold:
                        norm_score = 0.60 + 0.40 * ((count - threshold) / (max_calls - threshold))
                    else:
                        norm_score = 0.85
                    norm_score = min(1.0, max(0.0, norm_score))

                    severity = AnomalySeverity.HIGH if (count >= p95 or count >= (threshold + 0.5 * iqr) or count >= 1.5 * threshold) else AnomalySeverity.MEDIUM
                    explanation = (
                        f"Phone participated in {count} calls, substantially exceeding "
                        f"the upper frequency anomaly threshold of {threshold:.1f} calls "
                        f"(median: {median_calls:.1f}, Q75: {q75:.1f})."
                    )

                    anomalies.append(
                        AnomalyResult(
                            entity_id=phone,
                            anomaly_type=AnomalyType.HIGH_CALL_FREQUENCY,
                            score=round(norm_score, 3),
                            severity=severity,
                            evidence=f"Call count: {count} vs threshold: {threshold:.1f}",
                            explanation=explanation,
                            supporting_record_ids=sorted(list(set(phone_call_ids[phone]))),
                            feature_values={
                                "call_count": count,
                                "median": round(median_calls, 1),
                                "q75": round(q75, 1),
                                "threshold": round(threshold, 1),
                            },
                        )
                    )

        # D. Burst Activity Detection (Concentrated events within short time window)
        for phone, ts_list in phone_timestamps.items():
            if len(ts_list) < self.burst_min_events:
                continue

            ts_sorted = sorted(ts_list, key=lambda x: x[0])
            max_burst_count = 0
            burst_record_ids: List[str] = []

            n = len(ts_sorted)
            for i in range(n):
                window_start = ts_sorted[i][0]
                window_ids = [ts_sorted[i][1]]
                current_count = 1

                for j in range(i + 1, n):
                    delta = (ts_sorted[j][0] - window_start).total_seconds()
                    if delta <= self.burst_window_seconds:
                        current_count += 1
                        window_ids.append(ts_sorted[j][1])
                    else:
                        break

                if current_count > max_burst_count:
                    max_burst_count = current_count
                    burst_record_ids = window_ids

            if max_burst_count >= self.burst_min_events:
                # Score based on how compressed the events are
                burst_score = min(1.0, 0.65 + 0.10 * (max_burst_count - self.burst_min_events))
                severity = AnomalySeverity.HIGH if max_burst_count >= (self.burst_min_events + 2) else AnomalySeverity.MEDIUM
                window_hrs = self.burst_window_seconds / 3600.0
                explanation = (
                    f"Concentrated burst activity detected: phone engaged in {max_burst_count} communications "
                    f"within a span of {window_hrs:.1f} hours."
                )

                anomalies.append(
                    AnomalyResult(
                        entity_id=phone,
                        anomaly_type=AnomalyType.BURST_ACTIVITY,
                        score=round(burst_score, 3),
                        severity=severity,
                        evidence=f"{max_burst_count} calls within {window_hrs:.1f} hours",
                        explanation=explanation,
                        supporting_record_ids=sorted(list(set(burst_record_ids))),
                        feature_values={
                            "burst_events_count": max_burst_count,
                            "window_seconds": self.burst_window_seconds,
                            "window_hours": window_hrs,
                        },
                    )
                )

        return anomalies

    # -----------------------------------------------------------------
    # 3. Graph Topology Anomaly Detectors
    # -----------------------------------------------------------------

    def _detect_graph_anomalies(
        self,
        entities: List[Entity],
        relationships: List[Relationship],
    ) -> List[AnomalyResult]:
        anomalies: List[AnomalyResult] = []

        if not relationships:
            return anomalies

        # Build adjacency graph
        adj: Dict[str, Set[str]] = {}
        edge_supporting_ids: Dict[str, List[str]] = {}

        for r in relationships:
            src = r.source
            tgt = r.target
            adj.setdefault(src, set()).add(tgt)
            adj.setdefault(tgt, set()).add(src)

            src_rec = r.provenance.source_id if hasattr(r, "provenance") and r.provenance else r.id
            edge_supporting_ids.setdefault(src, []).append(src_rec)
            edge_supporting_ids.setdefault(tgt, []).append(src_rec)

        degrees = {node: len(neighbors) for node, neighbors in adj.items()}
        if len(degrees) < 4:
            return anomalies

        deg_vals = list(degrees.values())
        p90_deg = self._percentile(deg_vals, self.degree_percentile_threshold)
        median_deg = self._percentile(deg_vals, 0.50)
        max_deg = max(deg_vals)

        # E. High Degree Connectivity
        for node, deg in degrees.items():
            if deg >= p90_deg and deg > median_deg:
                if max_deg > p90_deg:
                    norm_score = 0.60 + 0.40 * ((deg - p90_deg) / (max_deg - p90_deg))
                else:
                    norm_score = 0.85
                norm_score = min(1.0, max(0.0, norm_score))

                severity = AnomalySeverity.HIGH if deg >= (p90_deg * 1.3) else AnomalySeverity.MEDIUM
                explanation = (
                    f"Node possesses unusually high degree centrality with {deg} connections, "
                    f"exceeding the {int(self.degree_percentile_threshold * 100)}th percentile ({p90_deg:.1f}) "
                    f"of graph nodes (median: {median_deg:.1f})."
                )

                anomalies.append(
                    AnomalyResult(
                        entity_id=node,
                        anomaly_type=AnomalyType.HIGH_CONNECTIVITY,
                        score=round(norm_score, 3),
                        severity=severity,
                        evidence=f"Degree: {deg} vs P90: {p90_deg:.1f}",
                        explanation=explanation,
                        supporting_record_ids=sorted(list(set(edge_supporting_ids.get(node, [])))),
                        feature_values={
                            "degree": deg,
                            "median_degree": round(median_deg, 1),
                            "p90_degree": round(p90_deg, 1),
                            "neighbor_count": len(adj[node]),
                        },
                    )
                )

        # F. Cross-Community / Bridge Behavior
        # Inspect community annotations if present on entities
        entity_community: Dict[str, Any] = {}
        for e in entities:
            comm = getattr(e, "community_id", None)
            if comm is None and isinstance(e.attributes, dict):
                comm = e.attributes.get("community_id")
            if comm is not None:
                entity_community[e.id] = comm

        if len(entity_community) >= 4:
            for node, neighbors in adj.items():
                node_comm = entity_community.get(node)
                neighbor_comms = {entity_community.get(nbr) for nbr in neighbors if entity_community.get(nbr) is not None}
                # Remove node's own community from external count
                external_comms = neighbor_comms - ({node_comm} if node_comm is not None else set())

                # If node connects 2 or more distinct external communities
                if len(external_comms) >= 2:
                    score = min(1.0, 0.70 + (len(external_comms) * 0.10))
                    severity = AnomalySeverity.HIGH if len(external_comms) >= 3 else AnomalySeverity.MEDIUM
                    explanation = (
                        f"Node acts as a topological bridge connecting {len(external_comms)} "
                        f"separate modular communities ({sorted(list(external_comms))})."
                    )

                    anomalies.append(
                        AnomalyResult(
                            entity_id=node,
                            anomaly_type=AnomalyType.CROSS_COMMUNITY_BRIDGE,
                            score=round(score, 3),
                            severity=severity,
                            evidence=f"Bridges {len(external_comms)} distinct communities: {sorted(list(external_comms))}",
                            explanation=explanation,
                            supporting_record_ids=sorted(list(set(edge_supporting_ids.get(node, [])))),
                            feature_values={
                                "external_communities_count": len(external_comms),
                                "connected_communities": sorted(list(external_comms)),
                                "node_community": node_comm,
                            },
                        )
                    )

        return anomalies

    # -----------------------------------------------------------------
    # Statistical & Extraction Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _percentile(data: List[Union[int, float]], p: float) -> float:
        """
        Computes the p-th percentile of a list using linear interpolation.
        p must be in range [0.0, 1.0].
        """
        if not data:
            return 0.0
        s = sorted(data)
        n = len(s)
        if n == 1:
            return float(s[0])
        idx = p * (n - 1)
        lower = int(math.floor(idx))
        upper = int(math.ceil(idx))
        if lower == upper:
            return float(s[lower])
        weight = idx - lower
        return float(s[lower] * (1.0 - weight) + s[upper] * weight)

    @staticmethod
    def _parse_iso_timestamp(ts_str: Optional[str]) -> Optional[datetime]:
        if not ts_str or not isinstance(ts_str, str):
            return None
        cleaned = ts_str.strip()
        try:
            return datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _extract_transactions(
        self,
        records: List[Any],
        relationships: List[Relationship],
    ) -> List[Dict[str, Any]]:
        items = []
        for r in records:
            if isinstance(r, TransactionRecord):
                items.append({
                    "transaction_id": r.transaction_id,
                    "sender_account": r.sender_account_normalized,
                    "receiver_account": r.receiver_account_normalized,
                    "amount": float(r.amount),
                    "currency": r.currency,
                    "timestamp": r.normalized_timestamp or r.timestamp_raw,
                })
            elif isinstance(r, dict) and "amount" in r and "transaction_id" in r:
                items.append({
                    "transaction_id": r["transaction_id"],
                    "sender_account": r.get("sender_account"),
                    "receiver_account": r.get("receiver_account"),
                    "amount": float(r["amount"]),
                    "currency": r.get("currency", "INR"),
                    "timestamp": r.get("timestamp"),
                })

        for rel in relationships:
            if getattr(rel, "type", None) == "TRANSACTED_WITH" or getattr(getattr(rel, "type", None), "value", None) == "TRANSACTED_WITH":
                tid = rel.provenance.source_id if hasattr(rel, "provenance") and rel.provenance else rel.id
                # Avoid duplicate insertion if already gathered from raw records
                if not any(it["transaction_id"] == tid for it in items):
                    items.append({
                        "transaction_id": tid,
                        "sender_account": rel.source,
                        "receiver_account": rel.target,
                        "amount": float(rel.weight),
                        "currency": "INR",
                        "timestamp": rel.timestamp,
                    })

        return items

    def _extract_cdrs(
        self,
        records: List[Any],
        relationships: List[Relationship],
    ) -> List[Dict[str, Any]]:
        items = []
        for r in records:
            if isinstance(r, CDRRecord):
                items.append({
                    "call_id": r.call_id,
                    "caller_msisdn": r.caller_normalized,
                    "receiver_msisdn": r.receiver_normalized,
                    "timestamp": r.normalized_timestamp or r.timestamp_raw,
                    "duration_sec": r.duration_sec,
                })
            elif isinstance(r, dict) and "call_id" in r:
                items.append({
                    "call_id": r["call_id"],
                    "caller_msisdn": r.get("caller_msisdn"),
                    "receiver_msisdn": r.get("receiver_msisdn"),
                    "timestamp": r.get("timestamp"),
                    "duration_sec": r.get("duration_sec", 0),
                })

        for rel in relationships:
            if getattr(rel, "type", None) == "CALLED" or getattr(getattr(rel, "type", None), "value", None) == "CALLED":
                cid = rel.provenance.source_id if hasattr(rel, "provenance") and rel.provenance else rel.id
                if not any(it["call_id"] == cid for it in items):
                    items.append({
                        "call_id": cid,
                        "caller_msisdn": rel.source,
                        "receiver_msisdn": rel.target,
                        "timestamp": rel.timestamp,
                        "duration_sec": int(rel.weight),
                    })

        return items
