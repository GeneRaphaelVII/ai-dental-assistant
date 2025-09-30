# Design Document — AI Dental Assistant

## 1. Problem & Scope

Dental practices need an AI assistant to:

* Provide accurate, evidence-grounded answers from practice policies, coverage docs, and knowledge bases.
* Support workflows (appointment scheduling, claims lookup, triage).
* Enforce multi-tenant security, PHI protection, and compliance.
* Run locally or with free-tier cloud tools.

This MVP demonstrates these capabilities using open-source tools, while remaining extensible to production scale.

---

## 2. Architecture Overview

**Components (Docker Compose):**

* **FastAPI App** — `/ask` and `/agent` endpoints.
* **Postgres + pgvector** — storage for docs and embeddings; row-level security for tenants.
* **Redis** — cache for embeddings + LLM responses.
* **n8n (optional)** — workflow automation (external integration demo).
* **Prometheus (optional)** — metrics scraping.

**Data Flow:**

1. User query → FastAPI endpoint.
2. Planner decides required steps.
3. Retriever fetches hybrid results from Postgres (vector + lexical).
4. Evidence-first prompt assembled.
5. LLM generates grounded answer with citations.
6. Safety layer redacts PHI and logs.
7. Output returned as JSON (with sources or agent trace).

---

## 3. Retrieval Strategy

* **Ingestion:** chunk documents into ~500 tokens, embed with `sentence-transformers/all-MiniLM-L6-v2`.
* **Storage:** embeddings + metadata stored in Postgres with pgvector.
* **Hybrid retrieval:** combine vector similarity with lexical (tsvector).
* **Reranking:** merge results with weighted scoring.
* **Tenant isolation:** enforce WHERE `tenant_id = $tenant` and Postgres RLS.

---

## 4. Agent Roles

* **Planner:** Determines workflow (Q&A, scheduling, claims).
* **Retriever:** Runs hybrid retrieval.
* **Scheduler tool:** Queries availability table, proposes appointment slot; optional n8n integration for invites.
* **Billing/Claims tool:** Fetches coverage or claim status from mock DB.
* **Safety/Compliance:** Redacts PHI, enforces policies.
* **Summarizer:** Produces concise summary of agent trace.

Agents communicate through a lightweight orchestrator (custom Python) with trace logging.

---

## 5. Model Choices & LLM Strategy

* **Embeddings:** `all-MiniLM-L6-v2` (384-dim, lightweight, free).
* **LLM Primary:** Hugging Face inference (free-tier) or local models (`transformers`).
* **LLM Fallback:** OpenAI GPT-4 (if API key available).
* **Abstraction Layer:** Provider interface allows easy swap.
* **Caching:** Redis for prompt→response.
* **Resilience:** Backoff/retry with `tenacity`.

Tradeoffs:

* Local models = cost-free, slower, limited quality.
* Cloud models = faster/better, but costs and PHI concerns.

---

## 6. Security & Compliance

* **Multi-tenancy:** Postgres RLS ensures tenant isolation.
* **RBAC:** Tokens contain role (staff/patient); app enforces access scope.
* **PHI redaction:** Regex-based removal of names, SSNs, emails, phone numbers before logging.
* **Logs:** Only anonymized tokens or IDs are logged.
* **Output safety:** If evidence is absent, answer defaults to "I don’t know."

---

## 7. Observability

* **Logs:** Structured JSON logs with tenant_id (hashed).
* **Metrics (Prometheus):**

  * `requests_total`
  * `latency_p95`
  * `retrieval_recall@k`
  * `llm_tokens_total`
  * `llm_cost_estimate`
* **Dashboards:** Can integrate Grafana.

---

## 8. Evaluation

* **Gold sets:** JSON with queries, expected docs, expected answers.
* **Metrics:**

  * Correctness (manual + auto check)
  * Grounding overlap (retrieved vs gold docs)
  * Hallucination rate (answers without citations)
  * Latency, token usage
* **Harness:** pytest + `eval/run_eval.py`.
* **Red-team:** attempts at cross-tenant leakage, PHI exfiltration, prompt injection.

---

## 9. Deployment & CI/CD

* **Docker Compose:** one command to run locally.
* **CI/CD:** GitHub Actions runs tests on push; builds docker image on `main`.
* **Rollback:** Tagged docker images enable revert.
* **Secrets:** Use `.env` for keys (ignored in repo).

---

## 10. Roadmap

* Scale RAG to >10k docs with FAISS or ElasticSearch.
* Replace regex PHI redaction with trained NER model.
* Add streaming API responses.
* Integrate with production EHRs via secure APIs.
* Add fine-grained access control policies.

---

## 11. Conclusion

This MVP satisfies the assessment goals:

* Evidence-first grounded Q&A with citations.
* Multi-agent orchestration for scheduling and claims.
* Secure, multi-tenant system with PHI safeguards.
* Evaluation harness + observability.
* Dockerized demo with reproducibility.
