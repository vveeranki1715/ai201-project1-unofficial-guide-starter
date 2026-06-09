"""
Milestone 5 — Grounded generation
=================================

ask(question) ties the pipeline together: retrieve top-k chunks, format them as
numbered, cited context, and ask a Groq LLM to answer USING ONLY that context.
If the context doesn't contain the answer, the model is instructed to say so.

Grounding is enforced two ways:
  1. A strict system prompt: answer only from the provided sources, cite the
     source number(s) inline, and refuse if the context is insufficient.
  2. Structural: the only domain content in the prompt is the retrieved chunks,
     and source attribution is appended PROGRAMMATICALLY from retrieval metadata
     (not left to the model to invent).

Run directly to test on the evaluation questions:
    .venv/bin/python query.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve

load_dotenv()
MODEL = "llama-3.3-70b-versatile"
TOP_K = 4

SYSTEM_PROMPT = (
    "You are a study assistant for nursing and health-science students. "
    "Answer the question USING ONLY the information in the numbered sources "
    "provided below. Do not use any outside or prior knowledge. "
    "Cite the source number(s) you used inline, like [Source 2]. "
    "If the sources do not contain enough information to answer, reply exactly: "
    "\"I don't have enough information on that in my documents.\" "
    "Do not speculate or fill gaps with general knowledge."
)


def _format_context(hits: list[dict]) -> str:
    blocks = []
    for i, h in enumerate(hits, 1):
        cite = f"{h['source_title']}, {h['chapter_title']} (p. {h['page_start']})"
        blocks.append(f"[Source {i}] {cite}\n{h['text']}")
    return "\n\n".join(blocks)


def ask(question: str, k: int = TOP_K) -> dict:
    """Return {'answer': str, 'sources': list[str], 'hits': list[dict]}."""
    hits = retrieve(question, k=k)
    if not hits:
        return {
            "answer": "I don't have enough information on that in my documents.",
            "sources": [], "hits": [],
        }

    context = _format_context(hits)
    user_msg = (
        f"Sources:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the sources above, citing source numbers."
    )

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    answer = resp.choices[0].message.content.strip()

    # source attribution built programmatically from retrieval metadata.
    # numbering matches the [Source N] labels the model was given, so inline
    # citations in the answer line up with this list.
    sources = [
        f"[Source {i}] {h['source_title']} — {h['chapter_title']} "
        f"(p. {h['page_start']}, distance {h['distance']:.2f})"
        for i, h in enumerate(hits, 1)
    ]
    return {"answer": answer, "sources": sources, "hits": hits}


if __name__ == "__main__":
    from retrieve import EVAL_QUESTIONS
    for q in EVAL_QUESTIONS[:3]:
        out = ask(q)
        print(f"\nQ: {q}\nA: {out['answer']}\nSources:")
        for s in out["sources"]:
            print(f"  {s}")
