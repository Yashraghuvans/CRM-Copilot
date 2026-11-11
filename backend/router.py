"""Context router: role -> allowed sources -> raw hits [{source, text, score}]."""
import sqlite3
from pathlib import Path

import chromadb
import yaml

HERE = Path(__file__).parent
ROLES = yaml.safe_load((HERE / "roles.yaml").read_text())
# column concat searched per table
TABLES = {
    "tickets": "title || ' ' || body || ' ' || status",
    "users": "name || ' ' || email",
    "equipment": "name || ' ' || status || ' ' || location",
}


def _sql(source, words):
    db = sqlite3.connect(HERE / "data" / "demo.db")
    hits = []
    for row in db.execute(f"SELECT *, {TABLES[source]} FROM {source}"):
        blob = row[-1].lower()
        score = sum(w in blob for w in words)
        if score:
            hits.append({"source": source, "text": " | ".join(map(str, row[:-1])), "score": score})
    return hits


def _docs(question):
    col = chromadb.PersistentClient(str(HERE / "vectorstore")).get_or_create_collection("docs")
    if not col.count():
        return []
    r = col.query(query_texts=[question], n_results=3)
    return [{"source": "docs", "text": t, "score": 1 - d}
            for t, d in zip(r["documents"][0], r["distances"][0])]


def route(role, question):
    if role not in ROLES:
        raise ValueError(f"unknown role {role}")
    words = [w for w in question.lower().split() if len(w) > 2]
    hits = []
    for s in ROLES[role]:
        hits += _docs(question) if s == "docs" else _sql(s, words)
    return hits
