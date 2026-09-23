"""
VERITAS - Neo4j Data Loader
Ingests demo entities and relationships into Neo4j graph database using Cypher MERGE statements.
"""
import os
import json
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_DIR = os.path.join(ROOT_DIR, "data", "demo")

def load_data_to_neo4j():
    entities_path = os.path.join(DEMO_DIR, "entities.json")
    relationships_path = os.path.join(DEMO_DIR, "relationships.json")

    if not os.path.exists(entities_path) or not os.path.exists(relationships_path):
        print("ERROR: Demo data files missing. Run 'python scripts/seed_demo.py' first.")
        return False

    with open(entities_path, "r", encoding="utf-8") as f:
        entities = json.load(f)

    with open(relationships_path, "r", encoding="utf-8") as f:
        relationships = json.load(f)

    # Attempt to import neo4j driver
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("WARNING: 'neo4j' package is not installed in the current environment.")
        print("Install with: pip install neo4j")
        return False

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "veritas_password")

    print(f"Connecting to Neo4j at {uri} as '{user}'...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            # Test connectivity
            session.run("RETURN 1 AS test")
            print("Connected to Neo4j successfully!")

            # 1. Clear existing demo data or ensure unique constraints
            print("Setting up schema constraints...")
            for label in ["Person", "Phone", "Vehicle", "Organization", "Location", "BankAccount"]:
                try:
                    session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE")
                except Exception as e:
                    pass

            # 2. Ingest Nodes
            print(f"Ingesting {len(entities)} nodes...")
            for e in entities:
                label = e.get("type", "Entity")
                cypher_node = f"""
                MERGE (n:{label} {{id: $id}})
                SET n.name = $name,
                    n.role = $role,
                    n.risk_score = $risk_score,
                    n.degree = $degree,
                    n.betweenness = $betweenness,
                    n.pagerank = $pagerank,
                    n.community_id = $community_id,
                    n.aliases = $aliases
                """
                session.run(cypher_node, **e)

            # 3. Ingest Relationships
            print(f"Ingesting {len(relationships)} relationships...")
            for r in relationships:
                rel_type = r.get("type", "ASSOCIATED_WITH")
                prov = json.dumps(r.get("provenance", {}))
                cypher_edge = f"""
                MATCH (a {{id: $source}})
                MATCH (b {{id: $target}})
                MERGE (a)-[rel:{rel_type}]->(b)
                SET rel.id = $id,
                    rel.weight = $weight,
                    rel.timestamp = $timestamp,
                    rel.provenance = $provenance
                """
                session.run(
                    cypher_edge,
                    source=r["source"],
                    target=r["target"],
                    id=r["id"],
                    weight=r.get("weight", 1.0),
                    timestamp=r.get("timestamp", ""),
                    provenance=prov
                )

            print("SUCCESS: Ingested all nodes and edges into Neo4j graph store!")
        driver.close()
        return True

    except Exception as e:
        print(f"FAILED to connect or execute on Neo4j: {e}")
        print("Note: In-memory NetworkX mode will automatically be used by the backend if Neo4j is offline.")
        return False

def main():
    print("=" * 60)
    print("VERITAS - Neo4j Graph Ingestion Loader")
    print("=" * 60)
    load_data_to_neo4j()
    print("=" * 60)

if __name__ == "__main__":
    main()
