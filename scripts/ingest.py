"""Seeds demo.db + sample docs (if missing) and builds the Chroma index from backend/data/docs.
Run from repo root: python scripts/ingest.py"""
import sqlite3
from pathlib import Path

import chromadb

B = Path(__file__).parent.parent / "backend"
DOCS = B / "data" / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

if not list(DOCS.glob("*.txt")):
    (DOCS / "reset_router.txt").write_text("To reset the X200 router, hold the reset button 10 seconds, then reconfigure WAN.")
    (DOCS / "sla_policy.txt").write_text("Priority-1 tickets must get a first response within 1 hour; P2 within 4 hours.")

db = sqlite3.connect(B / "data" / "demo.db")
db.executescript("""
CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY, title TEXT, body TEXT, status TEXT);
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, email TEXT);
CREATE TABLE IF NOT EXISTS equipment(id INTEGER PRIMARY KEY, name TEXT, status TEXT, location TEXT);
""")
if not db.execute("SELECT 1 FROM tickets").fetchone():
    db.executemany("INSERT INTO tickets(title,body,status) VALUES(?,?,?)", [
        ("Router offline", "Customer Acme reports X200 router offline since morning", "open"),
        ("Billing question", "Invoice 1042 shows double charge", "pending")])
    db.executemany("INSERT INTO users(name,email) VALUES(?,?)", [
        ("Alice Acme", "alice@acme.test"), ("Bob Builder", "bob@build.test")])
    db.executemany("INSERT INTO equipment(name,status,location) VALUES(?,?,?)", [
        ("X200 router", "faulty", "Acme HQ"), ("Y10 switch", "ok", "Build Co warehouse")])
    db.commit()

col = chromadb.PersistentClient(str(B / "vectorstore")).get_or_create_collection("docs")
files = sorted(DOCS.glob("*.txt"))
col.upsert(ids=[f.name for f in files], documents=[f.read_text() for f in files])
print(f"indexed {len(files)} docs")
