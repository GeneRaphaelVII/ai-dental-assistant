# AI Dental Assistant — Readout Slides

---

## Slide 1 — Title
**AI Dental Assistant**  
Retrieval-Augmented Multi-Agent Prototype  
Dockerized • Secure • Evaluated

---

## Slide 2 — Problem & Scope
- Dental practices need quick, **evidence-grounded** answers.  
- Support workflows: **coverage Q&A, appointment scheduling, claims lookup**.  
- Must enforce **multi-tenant security** + **PHI protection**.  
- Goal: Deliver a working prototype that demonstrates feasibility.

---

## Slide 3 — Architecture Overview
- **FastAPI app** → APIs: `/ask`, `/agent`  
- **Postgres (pgvector)** → documents, availability, claims  
- **Redis** → cache  
- **Multi-agent orchestrator** → Planner, Retriever, Scheduler, Billing, Safety, Summarizer  
- **Observability** → structured logs + `/metrics`

[Diagram: user → FastAPI → orchestrator → Postgres/Redis → response]

---

## Slide 4 — Retrieval Strategy
- Docs stored with embeddings (MiniLM-384).  
- **Hybrid retrieval**: vector similarity + lexical search.  
- Evidence-first prompting with inline `[doc:ID]` citations.  
- Fallback: "I don’t know." if no evidence.

---

## Slide 5 — Multi-Agent Orchestration
- **Planner**: break down tasks.  
- **Retriever**: run hybrid search.  
- **Scheduler**: suggest/confirm appointments.  
- **Billing/Claims**: fetch claim status.  
- **Safety/Compliance**: redact PHI + block cross-tenant.  
- **Summarizer**: final concise answer.

---

## Slide 6 — Security & Compliance
- **Row Level Security (RLS)** in Postgres.  
- Tenant isolation via `X-Tenant-Id`.  
- PHI redaction in outputs/logs.  
- **Red-team tested**: cross-tenant access, prompt injection, PHI exfiltration.

---

## Slide 7 — Evaluation Harness
- Gold set: Plan A crowns (covered), Plan B orthodontics (excluded).  
- Script runs queries, collects grounding, hallucination, latency.  
- JSON report + pytest integration.

---

## Slide 8 — Observability
- JSON structured logs for all requests.  
- Prometheus metrics: `requests_total`, `request_latency_seconds`.  
- `/metrics` endpoint for scraping.

---

## Slide 9 — Demo Flow
1. **Ask**: "Does Plan A cover crowns?" → "Yes, covered at 80% [doc:1]".  
2. **Ask**: "Are orthodontics covered under Plan B?" → "No, excluded [doc:2]".  
3. **Agent**: "Book appointment for Oct 1, 9am" → Planner → Scheduler → confirmation.

---

## Slide 10 — Evaluation Results (sample)
- Total queries: 2  
- **Grounding rate**: 100%  
- **Hallucination rate**: 0%  
- **Avg latency**: ~0.5s

---

## Slide 11 — Roadmap
- Scale to larger doc sets (ElasticSearch / FAISS).  
- Stronger PHI redaction (NER).  
- Streaming answers.  
- Integration with real EHR/claims APIs.

---

## Slide 12 — Conclusion
- Prototype meets all requirements:  
  - Evidence-first, multi-agent, secure, observable, evaluated.  
- Ready for demo + extension.

---

**End**