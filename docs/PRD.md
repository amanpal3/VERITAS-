# Product Requirements Document (PRD) - VERITAS

## 1. Executive Summary
AI-powered system for law enforcement to extract, map, and analyze criminal networks from heterogeneous structured and unstructured data.

## 2. Key Personas and Use Cases
- **Lead Investigator**: Wants high-level network topology, top influencers, and risk scores.
- **Forensic Analyst**: Wants deep dive into CDRs, transaction trails, and shortest paths between suspects.
- **Intelligence Officer**: Uploads FIR documents and surveillance logs to extract new entities and links.

## 3. Core Features
1. Multi-source Data Ingestion (FIRs, CDRs, Banking records)
2. NER and Entity Resolution (Alias resolution, deduplication)
3. Graph Relationship Modeling and Neo4j Storage
4. Centrality and Key Influencer Analytics (PageRank, Betweenness, Degree)
5. Community / Gang Cluster Detection (Louvain modularity)
6. Interactive Network Visualization (Cytoscape.js)
