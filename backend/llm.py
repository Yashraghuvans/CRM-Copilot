"""Claude SDK adapter. Needs ANTHROPIC_API_KEY."""
import anthropic

_client = anthropic.Anthropic()


def ask(question, context):
    msg = _client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        system="You are a CRM copilot. Answer only from the context; say so if it lacks the answer.",
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}],
    )
    return msg.content[0].text
