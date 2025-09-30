# src/ingest/seed_from_json.py
import json
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

DATA_PATH = Path("data/mock_docs.json")

def main():
    data = json.loads(DATA_PATH.read_text())
    rows = [
        (d["tenant_id"], d.get("doc_type"), d.get("effective_date"), d.get("chunk_text"), None, d.get("source_doc"))
        for d in data
    ]

    conn = psycopg2.connect(dbname="dental", user="postgres", password="postgres", host="postgres", port=5432)
    cur = conn.cursor()
    execute_values(
        cur,
        "INSERT INTO docs (tenant_id, doc_type, effective_date, chunk_text, embedding, source_doc) VALUES %s",
        rows
    )
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Seeded mock docs")

if __name__ == "__main__":
    main()
