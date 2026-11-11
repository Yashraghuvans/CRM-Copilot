from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from assembler import assemble
from llm import ask
from router import ROLES, route

app = FastAPI()


class Q(BaseModel):
    role: str
    question: str


@app.get("/roles")
def roles():
    return list(ROLES)


@app.post("/ask")
def ask_endpoint(q: Q):
    try:
        context = assemble(route(q.role, q.question))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"answer": ask(q.question, context), "context": context}
