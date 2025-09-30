import psycopg2
import datetime
from typing import List, Dict

from retrieval import hybrid_retrieve


# Simple PHI redaction (very small rule-based)
import re
PHI_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
    r"\b\d{10}\b",  # 10 digit phone
    r"[\w\.-]+@[\w\.-]+"  # email
]

def redact(text: str) -> str:
    redacted = text
    for p in PHI_PATTERNS:
        redacted = re.sub(p, "[REDACTED]", redacted)
    return redacted


class Orchestrator:
    def __init__(self, db_config=None):
        self.db_config = db_config or {
            "dbname": "dental",
            "user": "postgres",
            "password": "postgres",
            "host": "postgres",
            "port": 5432,
        }

    def _db(self):
        return psycopg2.connect(**self.db_config)

    def plan(self, task: str) -> List[str]:
        # Very small planner: detect keywords
        steps = []
        t = task.lower()
        if "appointment" in t or "book" in t or "schedule" in t:
            steps = ["retrieve_availability", "propose_slot", "confirm"]
        elif "claim" in t or "coverage" in t or "insurance" in t:
            steps = ["retrieve_claims", "summarize_coverage"]
        else:
            steps = ["retrieve_docs", "answer_question"]
        return steps

    def retrieve_availability(self, tenant_id: str) -> List[Dict]:
        conn = self._db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, start_time, end_time, booked FROM availability WHERE tenant_id=%s AND booked=false ORDER BY start_time LIMIT 10",
            (tenant_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        slots = []
        for r in rows:
            slots.append({"id": r[0], "start": r[1].isoformat(), "end": r[2].isoformat(), "booked": r[3]})
        return slots

    def propose_slot(self, tenant_id: str, preferred: Dict = None) -> Dict:
        slots = self.retrieve_availability(tenant_id)
        if not slots:
            return {"status": "no_availability"}
        # pick first available slot
        slot = slots[0]
        draft = {"start": slot["start"], "status": "proposed", "slot_id": slot["id"]}
        return draft

    def confirm_slot(self, slot_id: int, tenant_id: str, patient_name: str) -> Dict:
        conn = self._db()
        cur = conn.cursor()
        # mark booked
        cur.execute("UPDATE availability SET booked=true, patient_name=%s WHERE id=%s AND tenant_id=%s", (patient_name, slot_id, tenant_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "confirmed", "slot_id": slot_id}

    def retrieve_claims(self, tenant_id: str, patient_id: str = None) -> List[Dict]:
        conn = self._db()
        cur = conn.cursor()
        if patient_id:
            cur.execute("SELECT claim_id, status, coverage_pct FROM claims WHERE tenant_id=%s AND patient_id=%s", (tenant_id, patient_id))
        else:
            cur.execute("SELECT claim_id, status, coverage_pct FROM claims WHERE tenant_id=%s LIMIT 10", (tenant_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"claim_id": r[0], "status": r[1], "coverage_pct": r[2]} for r in rows]

    def summarize_coverage(self, tenant_id: str, query: str) -> Dict:
        # Use retrieval to find relevant docs and return short summary
        hits = hybrid_retrieve(query, tenant_id=tenant_id, top_k=3)
        summary_text = "; ".join([h["text"] for h in hits])
        return {"summary": redact(summary_text), "sources": hits}

    def run(self, task: str, tenant_id: str, patient_name: str = None) -> Dict:
        trace = []
        steps = self.plan(task)
        trace.append({"agent": "Planner", "output": steps})

        result = {}
        for step in steps:
            if step == "retrieve_availability":
                avail = self.retrieve_availability(tenant_id)
                trace.append({"agent": "Scheduler", "output": avail})
            elif step == "propose_slot":
                draft = self.propose_slot(tenant_id)
                trace.append({"agent": "Scheduler", "output": draft})
                result["draft"] = draft
            elif step == "confirm":
                if "draft" in result and result["draft"].get("slot_id"):
                    conf = self.confirm_slot(result["draft"]["slot_id"], tenant_id, patient_name or "anonymous")
                    trace.append({"agent": "Scheduler", "output": conf})
                    result["confirmed"] = conf
            elif step == "retrieve_claims":
                claims = self.retrieve_claims(tenant_id)
                trace.append({"agent": "Billing", "output": claims})
                result["claims"] = claims
            elif step == "summarize_coverage":
                summ = self.summarize_coverage(tenant_id, task)
                trace.append({"agent": "Retriever", "output": summ})
                result["summary"] = summ
            elif step == "retrieve_docs":
                hits = hybrid_retrieve(task, tenant_id=tenant_id, top_k=5)
                trace.append({"agent": "Retriever", "output": hits})
                result["hits"] = hits
            elif step == "answer_question":
                hits = hybrid_retrieve(task, tenant_id=tenant_id, top_k=3)
                # naive answer composition
                answer = "Based on documents: " + " ".join([h["text"] for h in hits])
                answer = redact(answer)
                trace.append({"agent": "Answerer", "output": answer})
                result["answer"] = answer

        # Summarize trace
        final_summary = " | ".join([str(t.get("output") if isinstance(t.get("output"), str) else (t.get("output")[:1] if isinstance(t.get("output"), list) else str(t.get("output")))) for t in trace])
        return {"trace": trace, "final_summary": final_summary}


# convenience singleton
_orch = Orchestrator()

def run_task(task: str, tenant_id: str, patient_name: str = None):
    return _orch.run(task, tenant_id, patient_name)
