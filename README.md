# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

**Clinical & health-science study knowledge — an unofficial study guide for
nursing and pre-health students.** The system makes four dense, open-access
medical reference texts (microbiology, pharmacology for nurses, surgical care,
and patient safety / clinical-risk management) searchable in plain language and
returns cited, grounded answers. This knowledge is public but practically hard
to find: the answer a student needs is buried across ~3,500 pages of four
separate textbooks with no semantic search, so answering a focused clinical
question normally means already knowing which book, chapter, and page to open.
Official course materials are built for linear reading, not for asking a
specific question and getting a sourced answer back.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

Four source textbooks (in `documents/`) are split by the ingestion pipeline into
**111 chapter/section-level documents** (indexed in `processed/manifest.json`).
The table lists the source texts plus representative chapters showing coverage.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | OpenStax *Microbiology* (26 chapters) | PDF textbook | `documents/OpenStax-Microbiology.pdf` · https://openstax.org/details/books/microbiology |
| 2 | OpenStax *Pharmacology for Nurses* (40 chapters) | PDF textbook | `documents/OpenStax-Pharmacology-for-Nurses.pdf` · https://openstax.org/details/books/pharmacology-for-nurses |
| 3 | WHO *Surgical Care at the District Hospital* | PDF (WHO) | `documents/surgical-care-at-the-district-hospital-world-health-organization-618.pdf` · https://www.who.int/publications/i/item/9241545755 |
| 4 | *Textbook of Patient Safety and Clinical Risk Management* (34 chapters) | PDF (Springer, open access) | `documents/textbook-of-patient-safety-...-621.pdf` · https://link.springer.com/book/10.1007/978-3-030-59403-9 |
| 5 | Microbiology Ch. 14 — Antimicrobial Drugs | Chapter doc | `processed/doc-014-*.json` |
| 6 | Microbiology Ch. 26 — Nervous System Infections | Chapter doc | `processed/doc-026-*.json` |
| 7 | Pharmacology Ch. 20 — Anticoagulant/Antiplatelet Drugs | Chapter doc | `processed/doc-046-*.json` |
| 8 | Pharmacology Ch. 11 — Parkinson's Disease Drugs | Chapter doc | `processed/doc-037-*.json` |
| 9 | Patient Safety Ch. 3 — Human Error and Patient Safety | Chapter doc | `processed/doc-069-*.json` |
| 10 | WHO Surgical Care — surgical/sterile-technique sections | Section docs | `processed/doc-101..111-*.json` |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
