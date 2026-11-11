import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import llm
from assembler import assemble
from router import DB, ROLES, SCHEMA, route

app = FastAPI()


class Ask(BaseModel):
    role: str
    user_id: int
    query: str


def _users():
    u = SCHEMA["user_table"]  # identifiers come from trusted config, not request input
    return sqlite3.connect(DB).execute(f"SELECT {u['id']}, {u['display']}, {u['role']} FROM {u['name']}").fetchall()


@app.get("/roles")
def roles():
    """role -> [{id, name}] so a client can pick who is asking."""
    return {r: [{"id": i, "name": n} for i, n, ur in _users() if ur == r] for r in ROLES}


@app.post("/ask")
def ask(req: Ask):
    if req.role not in ROLES:
        raise HTTPException(400, f"unknown role {req.role}")
    if (req.user_id, req.role) not in [(i, r) for i, _, r in _users()]:
        raise HTTPException(403, "user_id is not a user with that role")
    context, sources = assemble(route(req.query, req.role, req.user_id))
    return {"answer": llm.answer(req.query, context, req.role), "sources": sources}
