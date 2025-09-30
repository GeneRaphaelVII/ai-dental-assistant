# src/ingest/embed_docs.py
from sentence_transformers import SentenceTransformer
import psycopg2

model = SentenceTransformer("all-MiniLM-L6-v2")

conn = psycopg2.connect(dbname="dental", user="postgres", password="postgres", host="postgres", port=5432)
cur = conn.cursor()
cur.execute("SELECT id, chunk_text FROM docs WHERE embedding IS NULL")
rows = cur.fetchall()

for doc_id, text in rows:
    emb = model.encode(text).tolist()
    # format vector literal for pgvector
    vec_literal = "[" + ",".join(str(float(x)) for x in emb) + "]"
    cur.execute("UPDATE docs SET embedding = %s::vector WHERE id = %s", (vec_literal, doc_id))

conn.commit()
cur.close()
conn.close()
print("✅ Updated embeddings for docs")
