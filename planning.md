# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

**Clinical & health-science study knowledge — an "unofficial guide" for nursing
and pre-health students.** The system makes a small library of dense, open-access
medical reference texts (microbiology, pharmacology for nurses, surgical care,
and patient-safety/clinical-risk management) instantly queryable in plain
language. This knowledge is *technically* public but practically hard to find:
the answers a student needs are buried across ~3,500 pages of four separate
textbooks with no semantic search, so finding "which drugs treat Parkinson's and
what are their contraindications" or "what does sterile technique require in a
district hospital" means knowing which book, chapter, and page to open. Official
course materials are organized for linear reading, not for asking a specific
question and getting a cited, grounded answer.

**Five specific questions the system should be able to answer:**
1. What are the main classes of antimicrobial drugs and how do they work? *(Microbiology Ch. 14)*
2. What nursing considerations apply when administering anticoagulant or antiplatelet drugs? *(Pharmacology Ch. 20)*
3. How is bacterial meningitis diagnosed and what causes it? *(Microbiology Ch. 26)*
4. What organizational practices reduce human error in patient care? *(Patient Safety Ch. 3)*
5. What are the steps and requirements for safe surgical/sterile technique in a district hospital? *(WHO Surgical Care)*

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

The corpus is built from **4 open-access reference textbooks** (in `documents/`),
which the ingestion pipeline splits into **111 chapter/section-level documents**.
The table below lists the 4 source texts plus 6 representative chapter-documents
to show subtopic coverage; the full set of 111 is enumerated in
`processed/manifest.json` after running ingestion.

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | OpenStax *Microbiology* | 26 chapters: microbes, pathogenicity, immunology, organ-system infections | `documents/OpenStax-Microbiology.pdf` — https://openstax.org/details/books/microbiology |
| 2 | OpenStax *Pharmacology for Nurses* | 40 chapters: drug classes, administration, nursing considerations by body system | `documents/OpenStax-Pharmacology-for-Nurses.pdf` — https://openstax.org/details/books/pharmacology-for-nurses |
| 3 | WHO *Surgical Care at the District Hospital* | Surgical service organization, anesthesia, procedures, sterile technique | `documents/surgical-care-at-the-district-hospital-world-health-organization-618.pdf` — https://www.who.int/publications/i/item/9241545755 |
| 4 | Springer *Textbook of Patient Safety and Clinical Risk Management* (open access) | 34 chapters: human error, risk management, safety guidelines | `documents/textbook-of-patient-safety-and-clinical-risk-management-...-621.pdf` — https://link.springer.com/book/10.1007/978-3-030-59403-9 |
| 5 | Microbiology, Ch. 14 — Antimicrobial Drugs | Drug classes & mechanisms of action | `processed/doc-014-*.json` |
| 6 | Microbiology, Ch. 26 — Nervous System Infections | Meningitis etc. diagnosis & causes | `processed/doc-026-*.json` |
| 7 | Pharmacology, Ch. 20 — Anticoagulant/Antiplatelet Drugs | Nursing considerations | `processed/doc-046-*.json` |
| 8 | Pharmacology, Ch. 11 — Parkinson's Disease Drugs | Treatments & contraindications | `processed/doc-037-*.json` |
| 9 | Patient Safety, Ch. 3 — Human Error and Patient Safety | Error-reduction practices | `processed/doc-069-*.json` |
| 10 | WHO Surgical Care — sterile-technique sections | Safe surgical/sterile procedure | `processed/doc-101..111-*.json` |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
