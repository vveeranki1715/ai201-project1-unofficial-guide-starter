"""
Milestone 3 — Document ingestion
================================

Loads the source PDFs in documents/, splits each book into chapter-level
documents using its bookmark/TOC tree, cleans away non-content (running
headers/footers, page numbers, publisher boilerplate), repairs hyphenation and
soft-wraps, and writes one structured JSON record per document to processed/.

Output per document (processed/doc-NNN-<slug>.json):
    id, source_file, source_title, chapter_title, page_start, page_end,
    char_count, word_count, text

Also writes processed/manifest.json (every field except text) as an index.

Run:  .venv/bin/python ingest.py
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import fitz  # PyMuPDF

DOCS_DIR = Path("documents")
OUT_DIR = Path("processed")

# Per-source segmentation config. Books with a usable TOC are split on the
# bookmark entries that mark chapters; the WHO book has a broken TOC (4 entries)
# so it falls back to fixed page-range slicing.
SOURCES = {
    "OpenStax-Microbiology.pdf": {
        "title": "Microbiology (OpenStax)",
        "mode": "toc", "level": 1,
        "chapter_re": re.compile(r"^Chapter\s+\d+", re.I),
    },
    "OpenStax-Pharmacology-for-Nurses.pdf": {
        "title": "Pharmacology for Nurses (OpenStax)",
        "mode": "toc", "level": 1,
        "chapter_re": re.compile(r"^Chapter\s+\d+", re.I),
    },
    "textbook-of-patient-safety-and-clinical-risk-management-liam-donaldson-walter-ricciardi-susan-sheridan-riccardo-tartaglia-621.pdf": {
        "title": "Patient Safety and Clinical Risk Management",
        "mode": "toc", "level": 2,
        "chapter_re": re.compile(r"^\d+:\s"),
    },
    "surgical-care-at-the-district-hospital-world-health-organization-618.pdf": {
        "title": "Surgical Care at the District Hospital (WHO)",
        "mode": "pages", "section_pages": 50, "start_page": 4,
    },
}

LICENSE_PATTERNS = [
    re.compile(r"access for free at openstax\.org", re.I),
    re.compile(r"^\s*\d+\s*$"),                     # standalone page numbers
    re.compile(r"^chapter\s+\d+\s*[|·-]", re.I),    # running chapter banners
]


def find_running_lines(pages_text: list[str], threshold: float = 0.4) -> set[str]:
    """Lines repeating on >= threshold of pages are headers/footers."""
    counts: Counter[str] = Counter()
    for txt in pages_text:
        for line in {l.strip() for l in txt.splitlines() if 3 <= len(l.strip()) <= 80}:
            counts[line] += 1
    cutoff = max(3, int(len(pages_text) * threshold))
    return {line for line, c in counts.items() if c >= cutoff}


def clean_text(pages_text: list[str], running: set[str]) -> str:
    kept: list[str] = []
    for txt in pages_text:
        for line in txt.splitlines():
            s = line.strip()
            if not s:
                kept.append("")
                continue
            if s in running or any(p.search(s) for p in LICENSE_PATTERNS):
                continue
            kept.append(s)
    text = unicodedata.normalize("NFKC", "\n".join(kept))
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)            # de-hyphenate
    text = re.sub(r"(?<![.!?:;])\n(?=[a-z(])", " ", text)   # join soft wraps
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def segment_by_toc(doc, cfg) -> list[dict]:
    level, rx = cfg["level"], cfg["chapter_re"]
    anchors = [(t.strip(), p - 1) for lvl, t, p in doc.get_toc()
               if lvl == level and rx.search(t.strip())]
    return [{"title": t, "start": s,
             "end": anchors[i + 1][1] if i + 1 < len(anchors) else doc.page_count}
            for i, (t, s) in enumerate(anchors)]


def segment_by_pages(doc, cfg) -> list[dict]:
    step, start0 = cfg["section_pages"], cfg["start_page"] - 1
    segs = []
    for n, s in enumerate(range(start0, doc.page_count, step), 1):
        e = min(s + step, doc.page_count)
        segs.append({"title": f"Section {n} (pp. {s + 1}-{e})", "start": s, "end": e})
    return segs


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    manifest, doc_id = [], 0
    for fname, cfg in SOURCES.items():
        path = DOCS_DIR / fname
        if not path.exists():
            print(f"!! missing {path}, skipping")
            continue
        doc = fitz.open(path)
        segs = (segment_by_toc(doc, cfg) if cfg["mode"] == "toc"
                else segment_by_pages(doc, cfg))
        print(f"\n{fname}: {len(segs)} documents")
        for seg in segs:
            pages = [doc[p].get_text() for p in range(seg["start"], seg["end"])]
            text = clean_text(pages, find_running_lines(pages))
            if len(text) < 500:
                continue
            doc_id += 1
            rec = {
                "id": f"doc-{doc_id:03d}",
                "source_file": fname,
                "source_title": cfg["title"],
                "chapter_title": re.sub(r"\s+", " ", seg["title"]).strip(),
                "page_start": seg["start"] + 1,
                "page_end": seg["end"],
                "char_count": len(text),
                "word_count": len(text.split()),
                "text": text,
            }
            out = OUT_DIR / f"{rec['id']}-{slugify(rec['chapter_title'])}.json"
            out.write_text(json.dumps(rec, ensure_ascii=False, indent=2))
            manifest.append({k: rec[k] for k in rec if k != "text"} | {"file": out.name})
            print(f"  {rec['id']}  {rec['chapter_title'][:48]:48}  "
                  f"p{rec['page_start']}-{rec['page_end']}  {rec['word_count']:>6}w")
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"\nDone: {len(manifest)} documents -> {OUT_DIR}/")


if __name__ == "__main__":
    main()
