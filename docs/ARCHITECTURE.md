# System Architecture - VERITAS

```
Heterogeneous Data (FIRs, CDRs, Financial Transactions)
                     │
                     ▼
       AI and NLP Ingestion Pipeline (`ai/`)
   [NER -> Normalization -> Entity Resolution]
                     │
                     ▼
          Graph Store (Neo4j)
                     │
                     ▼
      Backend API and Graph Engine (`backend/`)
 [FastAPI + Graph Algorithms (Centrality, Paths, Communities)]
                     │
                     ▼
        Interactive UI (`frontend/`)
      [React + Cytoscape.js + TailwindCSS]
```
