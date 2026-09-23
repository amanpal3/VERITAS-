# VERITAS — Product Requirements Document (PRD)

> **KAYA Hackathon 2026** // Master Project Analysis & Engineering Plan

---

## 1. Project Overview & Core Principle

**VERITAS** is an AI-powered criminal and intelligence network analysis platform designed to help investigators transform fragmented structured and unstructured records into an explainable relationship graph.

### Core Principle
VERITAS is built to **support investigation, not make determinations of guilt**. All analytical outputs are evidence-linked and phrased as objective analytical observations:
- *High-centrality entity*
- *Unusual activity flag*
- *Shared contact / intermediary*
- *Multi-hop connection*

---

## 2. Problem Analysis

Law-enforcement and intelligence records are scattered across FIRs/police complaints, Call Detail Records (CDRs), banking transactions, surveillance logs, criminal history records, and vehicle registries.

The 7 primary technical challenges VERITAS solves:
1. **Fragmentation** — Related clues exist in separate, disconnected files and databases.
2. **Unstructured Text** — Key suspects, locations, vehicles, and relationships are buried in narrative reports.
3. **Identity Ambiguity & Duplication** — The same entity appears under different spellings, aliases, or phone formats.
4. **Hidden Multi-Hop Relationships** — Critical connections require multiple intermediate hops across data sources.
5. **Network Scale** — Manual relationship mapping becomes infeasible as record counts grow.
6. **Explainability & Provenance** — Investigators need immediate access to the ground-truth evidence supporting any flagged link.
7. **Usability** — Graph intelligence must be intuitive, fast, and actionable through an interactive visual canvas.

---

## 3. Proposed Solution & End-to-End Pipeline

```text
Raw Sources (FIRs, CDRs, Financial Ledgers)
   ↓
Ingestion + Cleaning (`ai/ingestion/`)
   ↓
Entity / Relationship Extraction (`ai/extraction/`)
   ↓
Entity Resolution & Deduplication (`ai/resolution/`)
   ↓
Canonical Entities + Relationships (`data/output/`)
   ↓
NetworkX / Neo4j Knowledge Graph (`backend/app/graph/`)
   ↓
Centrality + Communities + Path Analysis + Anomaly Flags
   ↓
FastAPI REST API (`backend/app/api/`)
   ↓
React + Tailwind + Cytoscape.js Dashboard (`frontend/`)
   ↓
Evidence-Backed Investigator Insights & Dossiers
```

---

## 4. Key Personas & Core User Journey

### 4.1 Target Personas
- **Lead Investigator**: Needs macro-level network topology, community clusters, and top structural influencers.
- **Forensic Analyst**: Performs deep dives into CDR records, banking trails, and multi-hop paths between suspects.
- **Intelligence Officer**: Ingests new FIR complaints and field surveillance notes to extract new entities and links into the live graph.

### 4.2 Core User Journey
1. User opens the VERITAS dashboard.
2. User loads or selects a case dataset (e.g. *Operation Shadow Syndicate*).
3. System displays an ingestion processing summary (total records, extracted entities, resolved relationships).
4. Network graph renders automatically in the Cytoscape canvas with force-directed physics.
5. User searches or clicks on an entity to open the **Suspect Dossier** (attributes, connections, centrality scores, and source evidence).
6. User selects two suspects and runs **Find Connection**.
7. System highlights the shortest multi-hop path and presents all supporting relationships.
8. User inspects detected gang communities (Louvain modularity) and investigates flagged anomalous transactions or communication bursts.

---

## 5. Major Features & Priority Matrix

### P0 — Demo-Critical (Must-Have)
- Multi-source ingestion (CSV, JSON, plain text).
- Entity extraction: People, Phones, Locations, Vehicles, Organizations, Bank Accounts.
- Relationship extraction with source record citations.
- Entity normalization and alias deduplication.
- Interactive Cytoscape.js network graph canvas.
- Global entity search and multi-criteria filtering (entity type, relationship type).
- Node details and suspect dossiers.
- Edge evidence viewer with source document snippets.
- Centrality analysis (Degree, Betweenness, PageRank).
- Community detection (Louvain modularity clustering).
- Multi-hop pathfinder between selected entities.
- REST API integration via FastAPI.
- Cloud deployment on Render with health checks.

### P1 — Strong Enhancements
- Neo4j persistence with Cypher query repository and in-memory NetworkX fail-safe fallback.
- Graph metrics dashboard (density, diameter, cluster coefficients).
- Activity timeline charts and telecom communication logs.
- Cross-source evidence aggregation modal.
- Rule-based suspicious pattern indicators (burst calls, smurfing deposits).
- Pre-packaged demo dataset switcher.

### P2 — Time-Permitting (Bonus)
- scikit-learn anomaly detection (Isolation Forest).
- Graph-grounded LLM investigator assistant (RAG summaries restricted to retrieved subgraphs).
- Geographic map view with cell tower and safehouse coordinates.
- Neo4j Graph Data Science (GDS) algorithms.

---

## 6. Functional Requirements

| ID | Requirement Description |
| :--- | :--- |
| **FR-01** | Accept standardized entity and relationship JSON outputs from the AI pipeline. |
| **FR-02** | Construct a bidirectional multi-relational graph from canonical records. |
| **FR-03** | Expose graph nodes and edges via REST API formatted for Cytoscape.js. |
| **FR-04** | Return detailed entity dossiers and bounded $N$-hop ego-networks (`/entities/{id}`). |
| **FR-05** | Compute and return Degree, Betweenness, and PageRank centrality rankings. |
| **FR-06** | Partition graph into modular communities and return cluster assignments. |
| **FR-07** | Compute shortest multi-hop path between any two selected entities (`/paths/shortest`). |
| **FR-08** | Preserve evidentiary provenance for 100% of graph relationships. |
| **FR-09** | Support dynamic client-side filtering by entity type and edge confidence threshold. |
| **FR-10** | Provide `/api/v1/health` endpoint for continuous deployment monitoring. |

---

## 7. Non-Functional Requirements & Success Criteria

- **Graceful Error Handling**: All API routes return standardized `{ "error": { "code": "...", "message": "..." } }` JSON structures.
- **Fail-Safe Reliability**: Automatic fallback to in-memory NetworkX cache if Neo4j is offline.
- **Explainability**: No algorithmic score is presented as proof of guilt; every metric is displayed with clear definitions and source evidence.
- **Security**: No database credentials or API keys committed to version control; all configuration managed via environment variables.
- **Success Criteria**: An evaluation judge can witness the complete investigative flow in under 5 minutes:
  $$\text{Raw Data} \longrightarrow \text{Extraction} \longrightarrow \text{Knowledge Graph} \longrightarrow \text{Hidden Link Discovery} \longrightarrow \text{Evidence Audit}$$
