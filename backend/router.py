"""Given (query, role, user_id): query SQL / vector / memory, each limited by roles.yaml.
Returns hits [{source, text, score}] with score in 0..1."""
import json
import os
import re
import sqlite3
from pathlib import Path

import chromadb
import yaml

HERE = Path(__file__).parent
CFG = Path(os.environ.get("CRM_CONFIG_DIR", HERE))  # template = roles.yaml + schema.yaml in this dir
ROLES = yaml.safe_load((CFG / "roles.yaml").read_text())
SCHEMA = yaml.safe_load((CFG / "schema.yaml").read_text())
DB = HERE / SCHEMA["db"]
OWNER = SCHEMA["owner_columns"]
STOP = {"the", "and", "for", "with", "what", "who", "how", "are", "was", "this", "that", "from", "has", "have", "does", "can", "you"}


def _words(q):
    return [w for w in re.findall(r"[a-z0-9]+", q.lower()) if len(w) > 2 and w not in STOP]


def _sql(cfg, words, user_id):
    db = sqlite3.connect(DB)
    hits = []
    for table, cols in cfg["sql"].items():
        where, args = "", ()
        if cfg["row_scope"] == "own" and table in OWNER:
            where, args = f" WHERE {OWNER[table]} = ?", (user_id,)
        for row in db.execute(f"SELECT {', '.join(cols)} FROM {table}{where}", args):
            blob = " ".join(map(str, row)).lower()  # only allowed columns are ever searched
            n = sum(w in blob for w in words)
            if n:
                hits.append({"source": f"sql:{table}#{row[0]}", "score": n / len(words),
                             "text": f"{table}: " + ", ".join(f"{c}={v}" for c, v in zip(cols, row))})
    return hits


def _vector(role, query):
    col = chromadb.PersistentClient(str(HERE / SCHEMA["vectorstore"])).get_collection("docs")
    r = col.query(query_texts=[query], n_results=3, where={f"role_{role}": True})
    return [{"source": f"doc:{m['source']}", "text": t, "score": 1 / (1 + d)}
            for t, m, d in zip(r["documents"][0], r["metadatas"][0], r["distances"][0])]


def _memory(scope, words, user_id):
    hits = []
    for i, m in enumerate(json.loads((HERE / SCHEMA["memory_file"]).read_text())):
        n = sum(w in m["text"].lower() for w in words)
        if n and (scope == "team" or m["user_id"] == user_id):
            hits.append({"source": f"memory#{i}", "text": m["text"], "score": n / len(words)})
    return hits


def route(query, role, user_id):
    cfg = ROLES[role]  # KeyError on unknown role: callers validate first
    words = _words(query)
    hits = _sql(cfg, words, user_id) if words else []
    if cfg["doc_tags"]:
        hits += _vector(role, query)
    if cfg["memory"] != "none" and words:
        hits += _memory(cfg["memory"], words, user_id)
    return hits
