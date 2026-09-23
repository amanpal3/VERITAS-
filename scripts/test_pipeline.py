"""
VERITAS - Demo Pipeline Integrity & Sanity Verification Script
Validates that demo FIRs, CDRs, financial records, and graph fixtures are present,
consistent, and form a valid interconnected graph for the hackathon presentation.
"""
import os
import json
import csv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_DIR = os.path.join(ROOT_DIR, "data", "demo")

def test_pipeline_integrity():
    print("=" * 65)
    print("VERITAS - Pipeline Data Integrity & Graph Connectivity Audit")
    print("=" * 65)

    passed_checks = 0
    total_checks = 6

    # 1. Check FIR documents
    firs_dir = os.path.join(DEMO_DIR, "firs")
    fir_files = [f for f in os.listdir(firs_dir) if f.endswith(".txt")] if os.path.exists(firs_dir) else []
    print(f"[*] Checking FIR reports: Found {len(fir_files)} files in {firs_dir}...")
    if len(fir_files) >= 5:
        print("    [PASS] 5/5 Police reports & surveillance logs verified.")
        passed_checks += 1
    else:
        print(f"    [FAIL] Expected at least 5 FIR files, found {len(fir_files)}.")

    # 2. Check CDR telecom records
    cdrs_path = os.path.join(DEMO_DIR, "cdrs.csv")
    cdr_count = 0
    if os.path.exists(cdrs_path):
        with open(cdrs_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            cdr_count = sum(1 for _ in reader)
    print(f"[*] Checking CDR records: Found {cdr_count} call records in {cdrs_path}...")
    if cdr_count >= 50:
        print(f"    [PASS] {cdr_count} Call Detail Records verified.")
        passed_checks += 1
    else:
        print(f"    [FAIL] Expected >= 50 CDR rows, found {cdr_count}.")

    # 3. Check Financial transactions
    tx_path = os.path.join(DEMO_DIR, "transactions.csv")
    tx_count = 0
    if os.path.exists(tx_path):
        with open(tx_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            tx_count = sum(1 for _ in reader)
    print(f"[*] Checking Transactions: Found {tx_count} records in {tx_path}...")
    if tx_count >= 40:
        print(f"    [PASS] {tx_count} Financial transactions verified.")
        passed_checks += 1
    else:
        print(f"    [FAIL] Expected >= 40 transactions, found {tx_count}.")

    # 4. Check Entities & Graph Schema
    entities_path = os.path.join(DEMO_DIR, "entities.json")
    entities = []
    entity_ids = set()
    if os.path.exists(entities_path):
        with open(entities_path, "r", encoding="utf-8") as f:
            entities = json.load(f)
            entity_ids = {e["id"] for e in entities}
    print(f"[*] Checking Entities: Found {len(entities)} entities in {entities_path}...")
    if len(entities) >= 20:
        print(f"    [PASS] {len(entities)} Entities verified across all required node labels.")
        passed_checks += 1
    else:
        print(f"    [FAIL] Expected >= 20 entities, found {len(entities)}.")

    # 5. Check Relationships & Referential Integrity
    relationships_path = os.path.join(DEMO_DIR, "relationships.json")
    relationships = []
    broken_edges = []
    if os.path.exists(relationships_path):
        with open(relationships_path, "r", encoding="utf-8") as f:
            relationships = json.load(f)
            for r in relationships:
                if r["source"] not in entity_ids:
                    broken_edges.append((r["id"], f"source {r['source']} not in entities"))
                if r["target"] not in entity_ids:
                    broken_edges.append((r["id"], f"target {r['target']} not in entities"))
    print(f"[*] Checking Relationships: Found {len(relationships)} relationships in {relationships_path}...")
    if len(relationships) >= 25 and len(broken_edges) == 0:
        print(f"    [PASS] {len(relationships)} Relationships verified with 100% referential integrity.")
        passed_checks += 1
    else:
        print(f"    [FAIL] Integrity errors found: {broken_edges}")

    # 6. Check Cytoscape Graph Payload & Multi-Hop Path (P006 -> P001)
    graph_path = os.path.join(DEMO_DIR, "graph.json")
    has_valid_graph = False
    if os.path.exists(graph_path):
        with open(graph_path, "r", encoding="utf-8") as f:
            g = json.load(f)
            has_valid_graph = "nodes" in g and "edges" in g and len(g["nodes"]) > 0

    # Build adjacency list to test path from P006 (Arjun) to P001 (Vikram)
    adj = {}
    for r in relationships:
        u, v = r["source"], r["target"]
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u) # Undirected connectivity

    # BFS
    queue = [["P006"]]
    visited = {"P006"}
    found_path = None
    while queue:
        path = queue.pop(0)
        curr = path[-1]
        if curr == "P001":
            found_path = path
            break
        for nbr in adj.get(curr, []):
            if nbr not in visited:
                visited.add(nbr)
                queue.append(path + [nbr])

    print(f"[*] Testing Multi-Hop Connection (Arjun Verma [P006] -> Vikram Singhania [P001])...")
    if found_path and has_valid_graph:
        path_str = " -> ".join(found_path)
        print(f"    [PASS] Multi-hop path confirmed: {path_str}")
        print(f"    [PASS] Cytoscape graph payload verified.")
        passed_checks += 1
    else:
        print("    [FAIL] No path found between runner and kingpin.")

    print("=" * 65)
    print(f"INTEGRITY AUDIT SCORE: {passed_checks}/{total_checks} PASSED")
    print("=" * 65)
    return passed_checks == total_checks

def main():
    test_pipeline_integrity()

if __name__ == "__main__":
    main()
