# AI Dental Assistant

## Overview

This repository contains the implementation of the **AI Dental Assistant** — a Retrieval-Augmented Generation (RAG) and multi-agent system designed for dental practices. It demonstrates secure multi-tenant support, evidence-grounded answers, and workflow automation (appointments, billing, triage). The system is packaged with Docker and can be run entirely on free/local tools.

---

## Features

* **RAG core**: Hybrid retrieval (vector + lexical) with tenant isolation.
* **Multi-agent orchestration**: Planner, Retriever, Scheduler, Billing/Claims, Safety/Compliance, Summarizer.
* **APIs**: `/ask` (grounded answers with citations) and `/agent` (agent trace).
* **Security**: Postgres Row Level Security (RLS), PHI redaction, RBAC.
* **Observability**: JSON logs + Prometheus metrics.
* **Evaluation harness**: Gold sets, pytest tests, hallucination check, retrieval recall.
* **Deployment**: Docker Compose with Postgres, Redis, FastAPI app, and optional n8n.

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

```bash
docker compose exec app python src/ingest/seed.py
```

### 4. Demo API calls

#### Ask endpoint

```bash
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer staff-token" \
  -H "X-Tenant-Id: clinic-123" \
  -d '{"query":"Is crown coverage included for procedure X?","role":"staff"}'
```

Expected output:

```json
{
  "answer": "Yes, crowns are covered under plan A ... [doc:23#2]",
  "sources": [{"doc_id": 23, "chunk_id": 2, "score": 0.92}]
}
```

#### Agent endpoint

```bash
curl -X POST http://localhost:8000/agent \
  -d '{"task":"Book appointment for Oct 1, 9am"}'
```

Expected output:

```json
{
  "trace": [
    {"agent": "Planner", "output": "Plan: retrieve availability, draft appointment"},
    {"agent": "Scheduler", "draft": {"start":"2025-10-01T09:00:00","status":"proposed"}}
  ],
  "final_summary": "Drafted appointment on 2025-10-01 09:00"
}
```

---

## Project Structure

```
ai-dental-assistant/
├── README.md
├── docker-compose.yml
├── services/
│   └── app/ (FastAPI app, Dockerfile)
├── src/
│   ├── ingest/ (ingestion pipeline)
│   ├── agents/ (orchestrator + agent tools)
│   └── app/ (FastAPI endpoints)
├── data/ (mock documents + seed SQL)
├── prompts/ (system prompts + red-team pack)
├── design/DesignDoc.md (architecture doc)
├── eval/ (gold sets, eval harness, tests)
├── docs/ (slides + one-pager)
└── .github/workflows/ci.yml (CI pipeline)
```

---

## Development

### Run tests

```bash
docker compose exec app pytest
```

### Lint code

```bash
docker compose exec app black src/
```

### Check evaluation metrics

```bash
docker compose exec app python eval/run_eval.py
```

---

## Deliverables

* `design/DesignDoc.md` — Architecture + tradeoffs (2–4 pages).
* `prompts/` — Prompts and red-team pack.
* `eval/` — Evaluation harness + reports.
* `docs/` — Slides and one-pager for readout.
* Dockerized working prototype.

---

## License

MIT License.
