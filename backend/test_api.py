"""API check with the LLM stubbed. Needs seeded DB + ingested docs. Run: python backend/test_api.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fastapi.testclient import TestClient

import llm
from main import app

llm.answer = lambda q, ctx, role, client=None: f"[{role}] {ctx}"
c = TestClient(app)

assert [u["name"] for u in c.get("/roles").json()["technician"]] == ["Tom Tech", "Tina Tech", "Raj Tech"]
r = c.post("/ask", json={"role": "technician", "user_id": 4, "query": "router offline"}).json()
assert "sql:tickets#1" in r["sources"] and "sql:tickets#2" not in r["sources"]
assert c.post("/ask", json={"role": "wizard", "user_id": 4, "query": "x"}).status_code == 400
assert c.post("/ask", json={"role": "supervisor", "user_id": 4, "query": "x"}).status_code == 403  # role spoofing
assert c.post("/ask", json={"role": "planner", "query": "x"}).status_code == 422
print("ok")
