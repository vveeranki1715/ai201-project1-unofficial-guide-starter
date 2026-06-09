"""
Milestone 3 — Chunking (token-aware)
====================================

Reads processed/*.json (chapter documents from ingest.py) and splits each into
retrieval-ready chunks, per the Chunking Strategy in planning.md.

Why token-aware: the embedding model all-MiniLM-L6-v2 has a hard 256-token
limit and silently truncates anything longer. Character counts are a poor proxy
for tokens on clinical text — drug/disease names tokenize into many subwords, so
an 800-char chunk can be 400+ tokens. We therefore measure size with the
model's OWN tokenizer and guarantee every chunk fits.

  * Target ~200 tokens per chunk, hard ceiling 256.
  * ~30-token (~15%) overlap so a fact split across a boundary survives whole.
  * Boundaries chosen recursively: paragraph -> sentence -> word window, so we
    never split mid-sentence unless a single sentence exceeds the budget.

Writes chunks.jsonl (one JSON per line) with full source/chapter/page metadata.

Run:  .venv/bin/python chunk.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from sentence_transformers import SentenceTransformer

OUT_DIR = Path("processed")
CHUNKS_FILE = Path("chunks.jsonl")

TARGET_TOKENS = 200
OVERLAP_TOKENS = 30
MAX_TOKENS = 256
MIN_TOKENS = 20  # don't emit tiny standalone fragments

_tok = SentenceTransformer("all-MiniLM-L6-v2").tokenizer


def ntok(s: str) -> int:
    return len(_tok.encode(s, add_special_tokens=False))


def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def split_long_sentence(sent: str) -> list[str]:
    """Split a single over-budget sentence into word windows <= TARGET_TOKENS."""
    words, out, buf = sent.split(), [], []
    for w in words:
        buf.append(w)
        if ntok(" ".join(buf)) > TARGET_TOKENS:
            buf.pop()
            if buf:
                out.append(" ".join(buf))
            buf = [w]
    if buf:
        out.append(" ".join(buf))
    return out


def split_units(text: str) -> list[str]:
    """Break text into semantic units each <= TARGET_TOKENS tokens."""
    units: list[str] = []
    for para in re.split(r"\n{2,}", text):
        para = para.strip()
        if not para:
            continue
        if ntok(para) <= TARGET_TOKENS:
            units.append(para)
            continue
        for sent in split_sentences(para):
            if ntok(sent) <= TARGET_TOKENS:
                units.append(sent)
            else:
                units.extend(split_long_sentence(sent))
    return units


def overlap_tail(text: str) -> str:
    """Return the trailing words of `text` worth ~OVERLAP_TOKENS tokens."""
    words = text.split()
    tail: list[str] = []
    for w in reversed(words):
        tail.insert(0, w)
        if ntok(" ".join(tail)) >= OVERLAP_TOKENS:
            break
    return " ".join(tail)


def pack(units: list[str]) -> list[str]:
    """Pack units up to TARGET_TOKENS, carrying a token-sized overlap tail."""
    chunks: list[str] = []
    cur = ""
    for u in units:
        candidate = f"{cur}\n\n{u}".strip() if cur else u
        if cur and ntok(candidate) > TARGET_TOKENS:
            chunks.append(cur.strip())
            cur = f"{overlap_tail(cur)}\n\n{u}".strip()
        else:
            cur = candidate
    if cur:
        if chunks and ntok(cur) < MIN_TOKENS:
            chunks[-1] = f"{chunks[-1]}\n\n{cur}".strip()
        else:
            chunks.append(cur.strip())
    # safety net: hard-cap anything still over MAX_TOKENS (rare)
    capped: list[str] = []
    for c in chunks:
        if ntok(c) <= MAX_TOKENS:
            capped.append(c)
        else:
            capped.extend(split_long_sentence(c))
    return [c for c in capped if c.strip()]


def main() -> None:
    docs = sorted(OUT_DIR.glob("doc-*.json"))
    total = 0
    with CHUNKS_FILE.open("w", encoding="utf-8") as fh:
        for p in docs:
            rec = json.loads(p.read_text())
            chunks = pack(split_units(rec["text"]))
            for i, ch in enumerate(chunks):
                fh.write(json.dumps({
                    "chunk_id": f"{rec['id']}-c{i:03d}",
                    "doc_id": rec["id"],
                    "source_file": rec["source_file"],
                    "source_title": rec["source_title"],
                    "chapter_title": rec["chapter_title"],
                    "page_start": rec["page_start"],
                    "page_end": rec["page_end"],
                    "chunk_index": i,
                    "n_chunks": len(chunks),
                    "char_count": len(ch),
                    "token_count": ntok(ch),
                    "text": ch,
                }, ensure_ascii=False) + "\n")
            total += len(chunks)
    toks = [json.loads(l)["token_count"] for l in CHUNKS_FILE.read_text().splitlines()]
    print(f"{len(docs)} documents -> {total} chunks  ({CHUNKS_FILE})")
    print(f"tokens: min={min(toks)} avg={sum(toks)//len(toks)} max={max(toks)}")
    print(f"chunks over {MAX_TOKENS} tokens: {sum(1 for t in toks if t > MAX_TOKENS)}")


if __name__ == "__main__":
    main()
