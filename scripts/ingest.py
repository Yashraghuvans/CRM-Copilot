"""Builds the Chroma index from backend/data/docs. Run once: python scripts/ingest.py
Doc tag = filename prefix (manual_x.txt -> 'manual'). visible_to comes from roles.yaml doc_tags."""
from pathlib import Path

import chromadb
import yaml

B = Path(__file__).parent.parent / "backend"
ROLES = yaml.safe_load((B / "roles.yaml").read_text())


def chunks(text, size=500):
    """Pack blank-line separated paragraphs into chunks of <= size chars."""
    out, cur = [], ""
    for p in filter(None, (p.strip() for p in text.split("\n\n"))):
        if cur and len(cur) + len(p) > size:
            out.append(cur)
            cur = ""
        cur = f"{cur}\n\n{p}".strip()
    return out + [cur] if cur else out


client = chromadb.PersistentClient(str(B / "vectorstore"))
if "docs" in [c.name for c in client.list_collections()]:
    client.delete_collection("docs")  # rebuild from scratch
col = client.create_collection("docs")

ids, docs, metas = [], [], []
for f in sorted((B / "data" / "docs").glob("*.txt")):
    tag = f.stem.split("_")[0]
    roles = [r for r, cfg in ROLES.items() if tag in cfg["doc_tags"]]
    # chroma metadata can't hold lists: keep visible_to readable + one bool per role to filter on
    meta = {"source": f.name, "tag": tag, "visible_to": ",".join(roles), **{f"role_{r}": True for r in roles}}
    for i, c in enumerate(chunks(f.read_text())):
        ids.append(f"{f.name}#{i}")
        docs.append(c)
        metas.append(meta)
col.add(ids=ids, documents=docs, metadatas=metas)
print(f"indexed {len(docs)} chunks from {len(set(m['source'] for m in metas))} docs")
