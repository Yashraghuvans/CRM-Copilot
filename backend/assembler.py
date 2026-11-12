"""Dedupe, rank, and trim hits to a token budget."""


def tokens(text):
    return len(text) // 4 + 1  # ponytail: ~4 chars/token estimate, swap for a real counter if budgets get tight


def assemble(hits, budget=1500):
    """Returns (context_text, sources)."""
    seen, lines, sources, used = set(), [], [], 0
    for h in sorted(hits, key=lambda h: -h["score"]):
        if h["text"] in seen:
            continue
        seen.add(h["text"])
        cost = tokens(h["text"])
        if used + cost > budget:
            continue  # a smaller, lower-ranked hit may still fit
        used += cost
        lines.append(f"[{h['source']}] {h['text']}")
        sources.append(h["source"])
    return "\n".join(lines), sources
