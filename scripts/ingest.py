"""Seeds sample docs (if missing) and builds the Chroma index from backend/data/docs.
Run from repo root: python scripts/ingest.py"""
from pathlib import Path

import chromadb

B = Path(__file__).parent.parent / "backend"
DOCS = B / "data" / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

if not list(DOCS.glob("*.txt")):
    (DOCS / "reset_router.txt").write_text("To reset the X200 router, hold the reset button 10 seconds, then reconfigure WAN.")
    (DOCS / "sla_policy.txt").write_text("Priority-1 tickets must get a first response within 1 hour; P2 within 4 hours.")

col = chromadb.PersistentClient(str(B / "vectorstore")).get_or_create_collection("docs")
files = sorted(DOCS.glob("*.txt"))
col.upsert(ids=[f.name for f in files], documents=[f.read_text() for f in files])
print(f"indexed {len(files)} docs")
