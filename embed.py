"""
Milestone 4 — Embedding + vector store
=======================================

Loads the chunks from chunks.jsonl, embeds each with all-MiniLM-L6-v2
(sentence-transformers, local, 384-dim), and stores them in a persistent
ChromaDB collection together with source metadata for later attribution.

Metadata stored per chunk: doc_id, source_file, source_title, chapter_title,
page_start, page_end, chunk_index.

Run:  .venv/bin/python embed.py
"""

from __future__ import annotations

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path("chunks.jsonl")
CHROMA_DIR = "chroma_db"
COLLECTION = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH = 256


def load_chunks() -> list[dict]:
    return [json.loads(l) for l in CHUNKS_FILE.read_text().splitlines() if l.strip()]


def main() -> None:
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # fresh build each run so re-embedding never duplicates
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
    col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        texts = [c["text"] for c in batch]
        embeddings = model.encode(texts, show_progress_bar=False,
                                  normalize_embeddings=True).tolist()
        col.add(
            ids=[c["chunk_id"] for c in batch],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{
                "doc_id": c["doc_id"],
                "source_file": c["source_file"],
                "source_title": c["source_title"],
                "chapter_title": c["chapter_title"],
                "page_start": c["page_start"],
                "page_end": c["page_end"],
                "chunk_index": c["chunk_index"],
            } for c in batch],
        )
        print(f"  embedded {min(i + BATCH, len(chunks))}/{len(chunks)}")

    print(f"Done: collection '{COLLECTION}' has {col.count()} vectors in {CHROMA_DIR}/")


if __name__ == "__main__":
    main()
