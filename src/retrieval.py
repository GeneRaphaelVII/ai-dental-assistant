from fastapi import FastAPI, Header
from pydantic import BaseModel
from retrieval import hybrid_retrieve

app = FastAPI()

class AskRequest(BaseModel):
    query: str
    role: str

class AgentRequest(BaseModel):
    task: str

@app.get("/")
def root():
    return {"message": "AI Dental Assistant API running"}

@app.post("/ask")
def ask(req: AskRequest, x_tenant_id: str = Header(...)):
    # Run retrieval for tenant
    evidence = hybrid_retrieve(req.query, tenant_id=x_tenant_id, top_k=5)

    # Build stub answer with citations
    if not evidence:
        return {"answer": "I don’t know. No evidence found.", "sources": []}

    citations = [f"[doc:{e['id']}]" for e in evidence]
    answer = f"Based on evidence, here’s a stub answer: {citations[0]}"

    return {
        "answer": answer,
        "sources": evidence
    }

@app.post("/agent")
def agent(req: AgentRequest):
    # TODO: add planner + tools + orchestrator
    return {
        "trace": [
            {"agent": "Planner", "output": f"Plan steps for task: {req.task}"}
        ],
        "final_summary": "Stub agent summary"
    }
