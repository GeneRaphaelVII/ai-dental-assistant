import psycopg2
from psycopg2.extras import execute_values
import datetime

# Mock documents
DOCS = [
    {
        "tenant_id": "clinic-123",
        "doc_type": "coverage",
        "effective_date": datetime.date(2025, 1, 1),
        "chunk_text": "Plan A covers crowns at 80% of cost.",
        "source_doc": "coverage_plan_a.pdf"
    },
    {
        "tenant_id": "clinic-123",
        "doc_type": "coverage",
        "effective_date": datetime.date(2025, 1, 1),
        "chunk_text": "Plan B excludes orthodontics.",
        "source_doc": "coverage_plan_b.pdf"
    },
    {
        "tenant_id": "clinic-456",
        "doc_type": "policy",
        "effective_date": datetime.date(2025, 1, 1),
        "chunk_text": "Appointments must be confirmed within 24 hours.",
        "source_doc": "clinic_policy.pdf"
    }
]


def init_db():
    conn = psycopg2.connect(
        dbname="dental",
        user="postgres",
        password="postgres",
        host="postgres",
        port=5432
    )
    cur = conn.cursor()

    cur.execute("""
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE IF NOT EXISTS docs (
        id serial PRIMARY KEY,
        tenant_id text NOT NULL,
        doc_type text,
        effective_date date,
        chunk_text text,
        embedding vector(384),
        source_doc text
    );
    """)

    rows = [(d["tenant_id"], d["doc_type"], d["effective_date"], d["chunk_text"], None, d["source_doc"]) for d in DOCS]

    execute_values(
        cur,
        "INSERT INTO docs (tenant_id, doc_type, effective_date, chunk_text, embedding, source_doc) VALUES %s",
        rows
    )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Seeded mock documents into Postgres")


if __name__ == "__main__":
    init_db()
