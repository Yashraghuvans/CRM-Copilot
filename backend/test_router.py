"""Permission + assembler check. Needs `python scripts/seed_db.py` and `python scripts/ingest.py` first.
Run: python backend/test_router.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from assembler import assemble
from router import route

tech = route("router offline ticket", "technician", 4)
assert any(h["source"] == "sql:tickets#1" for h in tech)                      # own ticket visible
assert not any(h["source"] in ("sql:tickets#2", "sql:tickets#3") for h in tech)  # others' tickets hidden
assert not any(h["source"].startswith("sql:users") for h in route("Tom Tech", "technician", 4))

plan = route("router offline", "planner", 1)
assert all("notes=" not in h["text"] for h in plan)                           # column hidden
assert not any(h["source"].startswith("memory") for h in plan)                # memory: none
assert all(h["source"] != "doc:manual_x200_reset.txt" for h in plan)          # manual not planner-visible

sup = route("Priority-1 router escalated", "supervisor", 2)
assert any(h["source"].startswith("memory") for h in sup)                     # team memory
assert not any(h["source"].startswith("memory") for h in route("Tom power supply", "technician", 5))  # own only

ctx, srcs = assemble(tech + tech, budget=40)                                  # dedupe + budget
assert len(srcs) == len(set(srcs)) and len(ctx) <= 40 * 4 + 200
print("ok")
