"""Identity check. Prompt wiring always runs; live 'who are you' probes run only if ANTHROPIC_API_KEY is set.
Run: python backend/test_llm.py"""
import os
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent))
from llm import answer


class Fake:
    def __init__(self):
        self.messages = self
        self.kw = None

    def create(self, **kw):
        self.kw = kw
        return SimpleNamespace(content=[SimpleNamespace(text="ok")])


f = Fake()
answer("hi", "[sql:tickets#1] open", "technician", client=f)
assert "CRM-Copilot" in f.kw["system"] and "[sql:tickets#1] open" in f.kw["system"] and "technician" in f.kw["system"]
assert f.kw["messages"] == [{"role": "user", "content": "hi"}]

if os.environ.get("ANTHROPIC_API_KEY"):
    for probe in ("who are you", "What's your name?", "Are you ChatGPT?"):
        reply = answer(probe, "", "planner")
        assert "CRM-Copilot" in reply, (probe, reply)
    print("ok (live probes passed)")
else:
    print("ok (wiring only; set ANTHROPIC_API_KEY for live probes)")
