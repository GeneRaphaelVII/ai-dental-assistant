# AI Dental Assistant

[![CI](https://github.com/your-org/ai-dental-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/ai-dental-assistant/actions)

## Overview

This repository contains the implementation of the **AI Dental Assistant** — a Retrieval-Augmented Generation (RAG) and multi-agent system designed for dental practices. It demonstrates secure multi-tenant support, evidence-grounded answers, and workflow automation (appointments, billing, triage). The system is packaged with Docker and can be run entirely on free/local tools.

---

## Features

* **RAG core**: Hybrid retrieval (vector + lexical) with tenant isolation.
* **Multi-agent orchestration**: Planner, Retriever, Scheduler, Billing/Claims, Safety/Compliance, Summarizer.
* **APIs**: `/ask` (grounded answers with citations) and `/agent` (agent trace).
* **Security**: Postgres Row Level Security (RLS), PHI redaction, RBAC.
* **Observability**: JSON logs + Prometheus `/metrics`.
* **Evaluation harness**: Gold sets, pytest tests, hallucination check, retrieval recall.
* **Deployment**: Docker Compose with Postgres, Redis, FastAPI app.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-org/ai-dental-assistant.git
cd ai-dental-assistant
```

### 2. Start services with Docker Compose

```bash
docker compose up --build
```

### 3. Seed mock data

Mock documents are provided in `data/mock_docs.json`.

Run the seeding script inside the app container:

```bash
docker compose exec app python src/ingest/seed_from_json.py
docker compose exec app python src/ingest/embed_docs.py   # optional: compute embeddings
```

### 4. Demo API calls

#### Ask endpoint

```bash
curl -X POST http://localhost:8000/ask   -H "X-Tenant-Id: clinic-123"   -d '{"query":"Does Plan A cover crowns?","role":"staff"}'
```

Example output:

```json
{
  "answer": "Yes, crowns are covered under Plan A at 80% [doc:1]",
  "sources": [{"doc_id": 1, "score": 0.92}]
}
```

#### Agent endpoint

```bash
curl -X POST http://localhost:8000/agent   -H "X-Tenant-Id: clinic-123"   -H "patient-name: Alice"   -d '{"task":"Book appointment for Oct 1, 9am"}'
```

Example output:

```json
{
  "trace": [
    {"agent": "Planner", "output": ["retrieve_availability","propose_slot","confirm"]},
    {"agent": "Scheduler", "output": {"slot_id": 1, "start":"2025-10-01T09:00:00+08:00","status":"confirmed"}}
  ],
  "final_summary": "Appointment confirmed for Alice on 2025-10-01 at 09:00."
}
```

---

## Project Structure

```
ai-dental-assistant/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── .env (local environment variables)
├── services/
│   └── app/
│       ├── Dockerfile
│       └── db/init.sql
├── src/
│   └── app/
│       ├── main.py          # FastAPI app
│       ├── orchestrator.py  # multi-agent logic
│       └── retrieval.py     # retrieval utilities
├── src/ingest/
│   ├── seed_from_json.py
│   └── embed_docs.py
├── data/
│   └── mock_docs.json
├── prompts/
│   └── prompts_and_redteam.md
├── design/
│   └── DesignDoc.md
├── docs/
│   └── readout_slides.md
├── eval/
│   ├── gold.json
│   ├── run_eval.py
│   ├── report.json
│   └── tests/test_eval.py
└── .github/workflows/ci.yml
```

---

## Development

### Run tests

```bash
docker compose exec app pytest
```

### Run evaluation

```bash
docker compose exec app python eval/run_eval.py
```

### Check metrics

```bash
curl http://localhost:8000/metrics
```

---

## Deliverables

* `design/DesignDoc.md` — Architecture + tradeoffs (2–4 pages).
* `prompts/prompts_and_redteam.md` — Prompts and red-team pack.
* `eval/` — Evaluation harness + reports.
* `docs/readout_slides.md` — Slides and one-pager for readout.
* `.github/workflows/ci.yml` — CI pipeline.
* Dockerized working prototype.

---

## License

MIT License.
