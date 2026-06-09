"""
Milestone 4 — Retrieval
=======================

retrieve(query, k=4) embeds the query with the same all-MiniLM-L6-v2 model,
queries the ChromaDB collection, and returns the top-k chunks with their source
metadata and cosine distance. A relevance threshold drops weak matches so they
don't pad the generation prompt.

Run directly to test retrieval on the evaluation questions:
    .venv/bin/python retrieve.py
"""

from __future__ import annotations

import functools

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = "chroma_db"
COLLECTION = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
# cosine distance; 0 = identical. Above this we treat a match as too weak.
DISTANCE_THRESHOLD = 0.75


@functools.lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


@functools.lru_cache(maxsize=1)
def _collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(COLLECTION)


def retrieve(query: str, k: int = 4, threshold: float = DISTANCE_THRESHOLD) -> list[dict]:
    """Return up to k relevant chunks, each as a dict with text, metadata,
    and cosine distance, sorted closest-first."""
    q_emb = _model().encode([query], normalize_embeddings=True).tolist()
    res = _collection().query(
        query_embeddings=q_emb, n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        if dist <= threshold:
            hits.append({"text": doc, "distance": dist, **meta})
    return hits


# evaluation questions (mirrors planning.md Evaluation Plan)
EVAL_QUESTIONS = [
    "What are the major classes of antimicrobial drugs and what does each target?",
    "What nursing considerations apply when administering warfarin?",
    "What are the common causes of bacterial meningitis and how is it diagnosed?",
    "What distinguishes active errors from latent conditions in patient safety?",
    "What is required to maintain sterile technique during surgery at a district hospital?",
]


def _demo() -> None:
    for q in EVAL_QUESTIONS[:3]:
        print(f"\n=== Q: {q}")
        for h in retrieve(q, k=4):
            print(f"  [{h['distance']:.3f}] {h['source_title']} / "
                  f"{h['chapter_title'][:38]} (p{h['page_start']})")
            print(f"        {h['text'][:140].strip()}...")


if __name__ == "__main__":
    _demo()
