"""Dedupe, rank, and trim hits to a character budget."""


def assemble(hits, budget=4000):
    seen, out, used = set(), [], 0
    for h in sorted(hits, key=lambda h: -h["score"]):
        if h["text"] in seen:
            continue
        seen.add(h["text"])
        if used + len(h["text"]) > budget:
            break
        used += len(h["text"])
        out.append(f"[{h['source']}] {h['text']}")
    return "\n".join(out)
