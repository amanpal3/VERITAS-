# VERITAS — Data Schema & Extraction Contracts

> **Data Governance & Normalization Rules** // Heterogeneous multi-source ingestion formats and canonical entity/relationship JSON schemas.

---

## 1. Raw Data Sources

VERITAS ingests 4 heterogeneous operational formats:

### 1.1 FIR & Police Narrative Reports (`TXT` / `PDF`)
- **Format**: Free-form natural language reports.
- **Fields**: Station Name, Crime No., Incident Date, Sections (IPC/NDPS/PMLA), Interrogation narrative, Officer remarks.
- **Example**: `data/demo/firs/FIR_001_Smuggling_Bust.txt`

### 1.2 Call Detail Records (CDRs) (`CSV`)
- **Format**: Structured telecom switch dumps.
- **Fields**:
  - `call_id`: Unique record identifier (e.g. `CDR1001`).
  - `caller_msisdn`: Initiating phone number in normalized E.164 format (e.g. `+919811010001`).
  - `receiver_msisdn`: Terminating phone number in normalized E.164 format.
  - `timestamp`: ISO-8601 UTC timestamp.
  - `duration_sec`: Duration in seconds.
  - `call_type`: `VOICE`, `SMS`, or `DATA`.
  - `cell_tower_id`: Sector / cell tower identifier.

### 1.3 Financial & Banking Ledgers (`CSV`)
- **Format**: Financial Intelligence Unit (FIU) and banking exports.
- **Fields**:
  - `transaction_id`: Transaction reference (e.g. `TX1001`).
  - `sender_account`: Originating account number (e.g. `ACC-ASTRA-7701`).
  - `receiver_account`: Beneficiary account number (e.g. `ACC-SINGH-9901`).
  - `amount`: Numeric transaction value.
  - `currency`: Currency code (e.g. `INR`, `USD`).
  - `timestamp`: ISO-8601 UTC timestamp.
  - `payment_channel`: `RTGS`, `NEFT`, `IMPS`, `UPI`, `CASH_DEPOSIT`, `SWIFT`.
  - `reference_note`: Transaction memo or invoice descriptor.

### 1.4 Surveillance & Field Intel Logs (`TXT`)
- **Format**: Tactical observation summaries with vehicle plates, safehouse locations, and associate spottings.

---

## 2. Canonical JSON Schemas

The AI pipeline (`ai/pipeline.py`) converts raw inputs into standardized JSON records before database loading.

### 2.1 Entity Schema
```json
{
  "id": "P001",
  "type": "Person",
  "label": "Vikramaditya Singhania",
  "role": "Syndicate Mastermind",
  "risk_score": 96,
  "aliases": ["Vikram", "The Don"],
  "attributes": {
    "age": 52,
    "residence": "Vasant Vihar, New Delhi",
    "primary_line": "+919811010001"
  },
  "source_records": ["FIR-188/2026", "INT-DEL-2026-409", "FIN-EOW-2026-092"]
}
```

#### Entity Type Controlled Vocabulary
- `Person`: Suspects, couriers, coordinators, kingpins, company directors.
- `Phone`: SIM cards, burner devices, secure terminals, IMSI/IMEI anchors.
- `Vehicle`: Cars, trucks, delivery vans, motorcycles.
- `Location`: Warehouses, cash vaults, safehouses, transit hubs.
- `Organization`: Corporate shells, logistics firms, front businesses, syndicates.
- `BankAccount`: Corporate accounts, wealth accounts, Hawala ledgers.

---

### 2.2 Relationship Schema
```json
{
  "id": "R001",
  "source": "P001",
  "target": "PH001",
  "type": "USES_PHONE",
  "directed": true,
  "weight": 1.0,
  "timestamp": "2026-03-01T00:00:00Z",
  "provenance": {
    "source_id": "INT-DEL-2026-409",
    "source_type": "SURVEILLANCE",
    "snippet": "Phone registered to Vasant Vihar residence.",
    "confidence": 0.95
  }
}
```

---

## 3. Data Governance & Normalization Rules

1. **Deterministic Unique IDs**: Every entity must carry an immutable unique identifier (`P001`, `PH001`, `V001`, `ORG001`, `LOC001`, `BA001`).
2. **Phone Number Standardization**: All phone numbers are normalized to E.164 format (stripping spaces, dashes, and leading zeros) prior to deduplication.
3. **Display Label vs. Identifier**: The display label is kept separate from the internal ID to facilitate alias resolution without corrupting graph keys.
4. **Zero Provenance Loss**: During entity resolution, merging two records must combine their `source_records` arrays rather than overwriting them.
5. **Controlled Relationship Vocabulary**: Relationship types are restricted to approved verbs: `CALLED`, `TRANSACTED_WITH`, `ASSOCIATED_WITH`, `OWNS`, `OPERATES`, `CONTROLS`, `MEMBER_OF`, `SUPERVISES`, `COORDINATES_WITH`, `LOCATED_AT`.
6. **Consistent Null Representation**: Missing fields are rendered as `null` or empty arrays `[]` rather than omitted keys.
