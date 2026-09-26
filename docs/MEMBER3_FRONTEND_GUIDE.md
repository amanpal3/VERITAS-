# VERITAS — Member 3 Frontend & UI/UX Guide

> **Author**: Member 3 (UI/UX Design, React, Cytoscape.js, Tailwind CSS)  
> **Status**: Production-Ready & Verified  
> **Theme**: Light-first Warm Canvas (`#F5F5F1`) with Dedicated Night Mode (`#101522`) and Detective Micro-Grid Texture

---

## 1. Product & Design Philosophy

**VERITAS** is an AI-powered criminal network intelligence system for law enforcement investigators.
The interface is designed as a calm, editorial, technical workspace:
* **Explainable Analysis**: Algorithmic metrics (PageRank, Betweenness, Centrality) are presented as descriptive signals, never automated guilt determinations.
* **Strict Provenance**: Every graph link connects directly to underlying source evidence (verbatim police FIR sentence, CDR record, or bank ledger transfer).
* **Restrained Visual Tone**: No hacker matrix neon, no glowing sci-fi borders, no red for guilt.
* **Institutional Detective Authority**: Polished heraldic forensic insignias, division seals, and evidentiary stamps.

---

## 2. Key Pages & Layout Hierarchy

| Route | View | Description |
| :--- | :--- | :--- |
| `/` | **Bureau Landing Home** | Institutional front page featuring investigative divisions, active operation metrics (Operation Cerberus), algorithmic architecture pillars, and mission brief. |
| `/dashboard` | **Overview Dashboard** | Header metrics, 4 minimal KPI cards, interactive Hero Cytoscape network preview, and prioritized review signals. |
| `/network` | **Network Explorer** | Core 72%/28% workspace with interactive Cytoscape canvas, multi-hop path finder, filter popover, entity dossiers, and evidence inspector. |
| `/entities` | **Entities Directory** | Forensic table of all discovered suspects and entities with search, class filtering, risk ranking, and CSV export. |
| `/analytics` | **Network Analytics** | Structural metrics (density, components, average degree), centrality horizontal bar charts, and Louvain modularity cell breakdowns. |

---

## 3. Component Architecture

```
frontend/src/
├── api/                   # Axios API clients for Backend endpoints (/graph, /entities, /analytics, /paths)
├── charts/
│   ├── CentralityChart    # Recharts horizontal ranking bar chart
│   └── CommunityChart     # Recharts modularity community bar chart
├── components/
│   ├── common/
│   │   ├── DetectiveLogos     # 6 high-detail forensic SVG emblems & agency seals
│   │   └── PathFinderModal    # Multi-hop path tracer with sequential graph highlighting
│   ├── evidence/
│   │   ├── EntityInspector    # Right-side dossier drawer with network position & connections
│   │   └── RelationshipInspector # Evidentiary audit card with verbatim document citations
│   ├── filters/
│   │   └── GraphFilters       # Popover with entity class toggles and risk slider
│   └── layout/
│       ├── AppSidebar         # 240px persistent navigation with live graph status & division seal
│       ├── AppHeader          # Breadcrumbs, active operation badge, day/night switcher, help modal
│       └── Footer             # Institutional footer with division crests, compliance badges, TeamMETX engineering squad & oversized wordmark
├── context/
│   ├── ThemeContext           # Day / Night mode state & localStorage persistence
│   └── ToastContext           # Lower-right notification alerts
├── graph/
│   ├── NetworkGraph           # Cytoscape.js canvas with safe lifecycle cleanup & layout unbinding
│   ├── graphStyles            # Theme-aware node/edge stylesheet
│   └── graphUtils             # Path highlight and focus helpers with defensive destruction checks
├── pages/
│   ├── Home                   # Bureau landing showcase
│   ├── Dashboard              # Overview KPI & hero canvas
│   ├── NetworkAnalysis        # Interactive investigative graph
│   ├── EntityDetails          # Forensic entity directory
│   └── Analytics              # Topological graph analytics
└── App.jsx                    # Root router with global cursor reticle and full-view footer
```

---

## 4. Detective Seals & Logos Suite

The system includes 6 handcrafted SVG emblems in `frontend/src/components/common/DetectiveLogos.jsx`:
1. `DetectiveBadge`: Shield emblem with 7-point star, scales of justice, and engraved chevron banner.
2. `CrimeIntelligenceSeal`: Circular double-ring institutional seal with compass star, graph network nodes, and Veritas motto.
3. `FinancialCrimesBadge`: Hexagonal anti-money laundering crest with currency flow vectors and secure vault grid.
4. `TelecomForensicsLogo`: Diamond radar and burner call vector emblem for CDR signal tracking.
5. `EvidenceVaultSeal`: Heavy institutional evidence vault lock badge with evidentiary certification chain.
6. `FingerprintIcon`: Stylized forensic biometrics fingerprint mark with crosshair alignment ticks.

---

## 5. Typography & Color Palette

### Typography Hierarchy
* **Headings & Metric Numbers**: `Plus Jakarta Sans` (`font-display`) — geometric, tight tracking, crisp editorial hierarchy.
* **Body, Navigation & Labels**: `Inter` (`font-sans`) — high legibility, tabular numbers (`tnum`), dynamic font feature settings (`cv02-cv11`).
* **Identifiers & Timestamps**: `JetBrains Mono` (`font-mono`) — forensic record codes, FIR IDs, risk scores, node IDs.
* **Verbatim Evidentiary Citations**: `Newsreader` (`font-serif italic`) — institutional primary text quotations with authentic provenance styling.

### Professional Intelligence Colors
* **Warm Canvas (Light Mode)**: `#F5F5F1` with `#FFFFFF` cards, `#E3E4DF` subtle borders, and `#16181B` typography.
* **Deep Navy (Night Mode)**: `#101522` background, `#171D2B` surfaces, `#1B2231` elevated cards, `#F1F2F6` typography.
* **Electric Violet Accent**: `#635BFF` (Light) / `#9B93FF` (Dark) — primary actions, focus nodes, person entities.
* **Cyan Data Signals**: `#00D2FF` (Light) / `#72DBEF` (Dark) — telecom CDRs, burner devices, live graph streams.
* **Coral Review Signals**: `#FF6B4A` (Light) / `#FF9A7B` (Dark) — Hawala flags, suspicious anomalies, active path traces.
* **Emerald Verified State**: `#10B981` (Light) / `#79D8AD` (Dark) — location entities, verified evidence records, healthy services.

---

## 7. Production Verification

```bash
# Frontend build
cd frontend
npm run build

# Backend verification
python -m pytest tests/
```

* **Frontend Build**: Built in ~12s with 0 errors (`dist/index.html`, `dist/assets/`).
* **Backend Integration**: 130 passing tests in `tests/` (`python -m pytest tests/`).
* **Development Server**: Run `npm run dev` at `http://localhost:5173/` (proxied to backend on port 8000).
* **Isolation**: Maintained strictly in Member 3 documentation; Member 2 documentation remained untouched.
