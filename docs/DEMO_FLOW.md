# VERITAS — Demo Flow & Hackathon Presentation Script

> **Judge Walkthrough Script** // Recommended 5–7 minute continuous investigative storyline, presentation timeline, and technical risk mitigations.

---

## 1. Recommended 5–7 Minute Demo Storyline

### Act 1: The Investigative Problem (0:00 – 0:30)
- **Narrative**: Law enforcement captures thousands of records across siloed systems (police FIRs, telecom CDRs, Hawala ledgers, and surveillance).
- **Pain Point**: Human analysts looking at tabular spreadsheets miss multi-hop connections connecting street criminals to kingpins.
- **Hook**: *"VERITAS transforms fragmented intelligence into an explainable, interactive relationship graph in seconds."*

### Act 2: Multi-Source Ingestion & AI Pipeline (0:30 – 1:15)
- **Showcase**: Navigate to Ingestion summary.
- **Action**: Show how raw FIR text (e.g. *Singhu border truck seizure*), CDR records, and financial transactions are ingested, parsed by spaCy NER, and deduplicated via entity resolution.
- **Takeaway**: Show the transformation from raw text to structured entities (`Person`, `Phone`, `Vehicle`, `Organization`, `BankAccount`).

### Act 3: Interactive Network Exploration (1:15 – 2:15)
- **Showcase**: Open the **Cytoscape.js** interactive graph canvas.
- **Action**:
  - Demonstrate force-directed physics layout (`fcose`).
  - Demonstrate dynamic filtering by entity type (e.g., isolate phones and suspects).
  - Search for suspect **Arjun Verma (P006)** caught in FIR #104.
  - Expand Arjun's 1-hop neighborhood to see immediate associates and phone lines.

### Act 4: Multi-Hop Hidden Connection Discovery (2:15 – 3:45)
- **The Climax of the Presentation**:
  - The lead investigator wants to know: *"Does street courier Arjun Verma connect to our primary target, Vikramaditya Singhania?"*
  - Select **Source**: `Arjun Verma (P006)` and **Target**: `Vikramaditya Singhania (P001)`.
  - Click **Find Connection**.
- **Result**: VERITAS calculates and visually highlights the 5-hop path with a glowing stroke:
  $$\text{Arjun Verma [Runner]} \xrightarrow{\text{SUPERVISES}} \text{Rajesh Kumar} \xrightarrow{\text{COORDINATES}} \text{Kabir Mirza} \xrightarrow{\text{USES}} \text{Burner PH004} \xrightarrow{\text{CALLED}} \text{Secure Line PH001} \xrightarrow{\text{USES}} \mathbf{\text{Vikram Singhania}}$$

### Act 5: 100% Explainable Evidentiary Provenance (3:45 – 4:30)
- **Showcase**: Click on the edge connecting `Rajesh Kumar` and `Arjun Verma`.
- **Action**: Open the **Evidence Drawer Modal**.
- **Proof**: The system displays the exact quotation from *FIR #104/2026 Special Cell*:
  > *"Under interrogation, accused Arjun Verma stated consignment was received from warehouse in Okhla managed by Rajesh Kumar..."*
- **Key Message**: *"Every link in VERITAS is backed by evidentiary provenance—no black-box hallucinations."*

### Act 6: Graph Analytics & Community Clusters (4:30 – 5:30)
- **Showcase**: Open the **Analytics Tab**.
- **Action**:
  - **Betweenness Centrality Leaderboard**: Explain why Hawala broker **Tariq Sheikh (P002)** scores the highest ($0.62$), acting as the vital financial bridge between street smuggling and corporate accounts.
  - **Community Detection**: Show the 3 colored Louvain clusters: *Logistics & Smuggling Cell*, *Hawala Laundering Cell*, and *Tactical Security Cell*.

### Act 7: Summary & Closing (5:30 – 6:00)
- **Closing**: VERITAS delivers transparent, evidence-backed decision support for investigators, moving from fragmented data to actionable criminal network intelligence in real time.

---

## 2. Key Technical Risks & Mitigations

| Risk | Impact | Mitigation Strategy Implemented |
| :--- | :--- | :--- |
| **AI output changes shape** | Integration breaks | Schemas frozen in `DATA_SCHEMA.md` with strict Pydantic validation. |
| **Duplicate entities** | Fragmented graph | Fuzzy entity resolution + normalized canonical IDs. |
| **Dense unreadable graph** | Cluttered visual UI | Interactive filters, ego-network bounded depth ($1-2$ hops), and physics layout. |
| **Metric misunderstood** | Misleading presentation | UI displays clear analytical definitions and source citations alongside scores. |
| **Cloud database latency** | Demo failure / freeze | Automatic in-memory NetworkX failover (`USE_IN_MEMORY_FALLBACK=true`). |
| **Render cloud cold start** | Slow response | Pre-flight ping script to keep backend container warm before judging. |
| **Slow live NLP extraction** | Presentation delay | Demo scenario uses pre-computed `data/demo/graph.json` for instantaneous 150ms responses. |
| **Frontend/Backend mismatch** | Broken API calls | Frozen `API_CONTRACT.md` with automated pytest integration verification. |
