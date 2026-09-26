# VERITAS — AI Explainable Anomaly Detection Specification

> **Module Documentation** // Member 1 (AI/NLP + Data)  
> Architectural design, statistical methods, explainability guarantees, non-accusatory semantics, and anomaly signal catalogs across financial, telecom, and graph domains.

---

## 1. Overview & Core Philosophy

In intelligence and forensic investigations, automated systems must never conflate **statistical anomaly** with **criminal guilt**. An anomaly simply means:

$$\text{"This behavior is statistically unusual according to the configured analytical rule."}$$

The Anomaly Detection Layer ([`ai/anomaly/detector.py`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/anomaly/detector.py)) produces explainable, mathematically grounded anomaly signals that guide human investigators toward unusual clusters of activity without asserting legal culpability or criminal intent.

### Non-Accusatory Investigative Guardrails
* **No Presumption of Guilt**: Entities are never flagged as "criminal", "guilty", or "perpetrator". Analytical language is strictly adhered to (e.g. "unusual transaction pattern", "elevated call volume", "high connectivity hub").
* **100% Explainable Ground Truth**: Every [`AnomalyResult`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/anomaly/detector.py#L38-L62) binds directly to its supporting records (`supporting_record_ids`), feature values (`feature_values`), quantitative threshold comparisons, and plain-language explanation.
* **No Label Leakage**: Anomaly indicators are derived purely from observable data (amounts, frequencies, timestamps, topological degrees) without relying on manually assigned demo risk scores or pre-seeded ground-truth targets.

---

## 2. Supported Anomaly Signals & Statistical Methods

| Anomaly Type | Domain | Statistical Method | Trigger Threshold | Primary Entity |
| :--- | :--- | :--- | :--- | :---: |
| `HIGH_TRANSACTION_AMOUNT` | Financial Ledgers | Percentile Distribution ($P_{90}$, $P_{95}$) | Transaction amount $\ge P_{90}$ of observed transfers. | `BankAccount` |
| `HIGH_TRANSACTION_FREQUENCY` | Financial Ledgers | Upper IQR Fence ($Q_3 + 1.5 \times \text{IQR}$) or $P_{90}$ | Total transaction count per account $\ge \min(\text{IQR Fence}, P_{90})$. | `BankAccount` |
| `HIGH_CALL_FREQUENCY` | Telecom CDRs | Upper IQR Fence ($Q_3 + 1.5 \times \text{IQR}$) or $P_{90}$ | Call count per MSISDN $\ge \min(\text{IQR Fence}, P_{90})$. | `Phone` |
| `BURST_ACTIVITY` | Telecom CDRs | Sliding Temporal Window | $\ge 3$ calls within a 2-hour window ($7200\text{s}$). | `Phone` |
| `HIGH_CONNECTIVITY` | Graph Topology | Degree Percentile ($P_{90}$) | Node degree $\ge P_{90}$ and $>$ median degree. | Any Node (`Person`, `Phone`, etc.) |
| `CROSS_COMMUNITY_BRIDGE` | Graph Topology | Modularity Partitioning | Node connects to $\ge 2$ distinct external modular communities. | Any Node |

---

## 3. Data Structures & Output Schema

Flagged anomalies conform to the canonical [`AnomalyResult`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/anomaly/detector.py#L38-L62) schema:

```python
class AnomalyResult(BaseModel):
    entity_id: str                      # e.g. "ACC-ASTRA-7701" or "+919811010003"
    anomaly_type: AnomalyType           # Controlled vocabulary
    score: float                        # [0.0, 1.0] normalized statistical extremity
    severity: AnomalySeverity           # LOW, MEDIUM, HIGH
    evidence: str                       # Quantitative snippet (e.g. "Amount: 3,500,000.00 vs P90: 940,000.00")
    explanation: str                    # Human-readable investigative justification
    supporting_record_ids: List[str]    # Underlying CDR/Transaction/FIR IDs
    feature_values: Dict[str, Any]      # Empirical metrics (amount, count, threshold, etc.)
```

### 3.1 Scoring Semantics
Anomaly scores are bounded within $[0.0, 1.0]$:
$$\text{Score} = 0.60 + 0.40 \times \left( \frac{\text{Value} - \text{Threshold}}{\text{Max Value} - \text{Threshold}} \right)$$
* **$0.60$**: Exactly at the outlier threshold boundary.
* **$1.00$**: Maximum outlier magnitude observed within the dataset.
* Scores reflect **statistical divergence**, not probabilities of guilt.

### 3.2 Severity Semantics
* **`HIGH`**: Value $\ge P_{95}$, value $\ge (\text{Threshold} + 0.5 \times \text{IQR})$, or value $\ge 1.5 \times \text{Threshold}$. Indicates extreme statistical deviation requiring immediate analytical inspection.
* **`MEDIUM`**: Value falls between threshold and high-severity boundary. Indicates moderately elevated activity.
* **`LOW`**: Borderline or exploratory anomalies.

---

## 4. Investigative Explanation Strategy

Every anomaly generates transparent, verifiable text for analyst review:

* **High Transaction Amount**:  
  *"Transaction amount of INR 3,500,000.00 exceeds the 90th percentile (INR 940,000.00) of observed financial transactions (median: INR 256,750.00)."*
* **High Call Frequency**:  
  *"Phone participated in 23 calls, substantially exceeding the upper frequency anomaly threshold of 20.7 calls (median: 12.0, Q75: 16.5)."*
* **Burst Activity**:  
  *"Concentrated burst activity detected: phone engaged in 5 communications within a span of 2.0 hours."*
* **High Degree Connectivity**:  
  *"Node possesses unusually high degree centrality with 8 connections, exceeding the 90th percentile (4.0) of graph nodes (median: 2.5)."*
* **Cross-Community Bridge**:  
  *"Node acts as a topological bridge connecting 2 separate modular communities ([2, 3])."*

---

## 5. Usage Example

```python
from ai.anomaly.detector import AnomalyDetector
from ai.ingestion.csv_parser import load_cdrs_csv, load_transactions_csv

detector = AnomalyDetector()

# Ingest records and detect anomalies
cdrs = load_cdrs_csv("data/demo/cdrs.csv")
transactions = load_transactions_csv("data/demo/transactions.csv")

anomalies = detector.detect(
    entities=entities,
    relationships=relationships,
    records=cdrs + transactions
)

for a in anomalies:
    print(f"[{a.severity.value}] {a.entity_id} ({a.anomaly_type.value}): {a.explanation}")
```

---

## 6. Limitations & False-Positive Considerations

1. **Volume Dependency**: Small datasets ($N < 4$) lack sufficient statistical density; the detector safely returns empty lists rather than reporting false positives.
2. **Operational Benign High Volume**: Legitimate high-throughput hubs (e.g. corporate payroll disbursement accounts, telecom customer care lines) will naturally trigger frequency thresholds and must be interpreted by human analysts with domain context.
3. **Temporal Skew**: Periodic batch accounting transfers (such as month-end settlements) may exhibit burst-like properties.
