# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Setup & Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your Groq API key into .env

python ingest.py    # 1. load 4 PDFs in documents/, split by chapter, clean -> processed/*.json
python chunk.py     # 2. token-aware chunking -> chunks.jsonl (14,176 chunks)
python embed.py     # 3. embed into ChromaDB (chroma_db/) with source metadata
python retrieve.py  # 4. (optional) sanity-check retrieval on the eval questions
python query.py     # 5. (optional) run grounded generation on the eval questions
python app.py       # launch the Gradio UI at http://localhost:7860
```

**Pipeline:** `ingest.py` → `chunk.py` → `embed.py` → `retrieve.py` →
`query.py` → `app.py`. See `planning.md` for the architecture diagram and design
rationale.

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

**Chunk size:** ~200 tokens per chunk, **hard ceiling 256 tokens**, measured
with the embedding model's own tokenizer (not character count).

**Overlap:** ~30 tokens (~15%), trimmed to start at a word boundary.

**Why these choices fit your documents:** My documents are dense, long-form
textbook prose — a single fact (a drug's mechanism, a procedure's steps) unfolds
across a paragraph, so tiny review-style chunks would scatter one concept across
many vectors. The hard ceiling comes from the embedding model: `all-MiniLM-L6-v2`
truncates anything past **256 tokens**. I initially sized chunks by characters
(~1,000 chars), but verifying against the model's tokenizer showed clinical text
tokenizes far denser than ~4 chars/token (drug/disease names explode into
subwords) — some 800-char chunks were **435 tokens** and would have been silently
truncated, dropping ~40% of the text before it was ever embedded. I therefore made
the chunker **token-aware**: it splits recursively (paragraph → sentence → word
window) and measures every unit with MiniLM's tokenizer, guaranteeing 0 chunks
exceed the limit. Overlap protects facts that straddle a chunk boundary.

Preprocessing before chunking (in `ingest.py`): split each PDF into chapter-level
documents via its TOC; remove running headers/footers (lines repeating on ≥40%
of a chapter's pages), standalone page numbers, and publisher boilerplate (e.g.
"Access for free at openstax.org"); de-hyphenate line-break splits; rejoin
soft-wrapped lines; NFKC-normalize Unicode.

**Final chunk count:** **14,176 chunks** from 111 chapter-level documents (4
PDFs). Token stats: min 34 / avg 182 / max 239 — **0 chunks over the 256-token
limit**. (This far exceeds the "≤2,000" rule of thumb, which targets a ~10-doc
review corpus; here the corpus is four full textbooks, ~3,500 pages.)

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (384-dim,
normalized embeddings, cosine similarity). Vectors stored in a persistent
**ChromaDB** collection. Chosen because it runs locally with no API key, no
rate limits, and no per-call cost — ideal for a free student tool — and is fast
enough to embed 14k chunks on CPU in a couple of minutes.

**Production tradeoff reflection:** If cost weren't a constraint I'd weigh:
- **Domain accuracy:** MiniLM is small and general-purpose. A biomedical encoder
  (e.g. PubMedBERT / MedCPT embeddings) would better separate near-synonym
  drug/disease terms and likely improve retrieval precision on this corpus.
- **Context length:** MiniLM's 256-token cap forced small chunks. A long-context
  model (OpenAI `text-embedding-3-large`, BGE-M3 at 8k tokens) could embed whole
  chapter-sections without truncation, capturing more context per vector — at the
  cost of an API dependency and per-call pricing.
- **Latency & privacy:** local MiniLM keeps queries private and offline; a hosted
  API adds network latency and sends text to a third party — a real consideration
  for any sensitive clinical query.
- **Multilingual:** not needed here (English texts); BGE-M3 would matter if I
  added non-English sources.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The Groq LLM
(`llama-3.3-70b-versatile`, temperature 0.1) is given this system prompt
(`query.py`):

> You are a study assistant for nursing and health-science students. Answer the
> question USING ONLY the information in the numbered sources provided below. Do
> not use any outside or prior knowledge. Cite the source number(s) you used
> inline, like [Source 2]. If the sources do not contain enough information to
> answer, reply exactly: "I don't have enough information on that in my
> documents." Do not speculate or fill gaps with general knowledge.

**Structural grounding (beyond the prompt):**
- The *only* domain content in the prompt is the retrieved chunks, formatted as
  numbered, individually-cited blocks (`[Source N] <book>, <chapter> (p. X)`).
- A **distance threshold (cosine ≤ 0.75)** filters weak matches before
  generation; if nothing passes, the system returns the refusal string **without
  ever calling the LLM**, so an off-topic query can't elicit a hallucinated
  answer. (Verified: "How do I file my taxes?" → refusal, 0 sources.)
- Low temperature (0.1) minimizes creative drift from the source text.

**How source attribution is surfaced in the response:** Attribution is built
**programmatically** from each retrieved chunk's ChromaDB metadata — not left to
the model to invent. The response object carries a `sources` list
(`[Source N] <book> — <chapter> (p. X, distance Y)`) numbered identically to the
`[Source N]` labels the model saw, so the model's inline citations line up with
the displayed source list. In the Gradio UI these appear in a dedicated
"Retrieved from" pane next to the answer.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Major classes of antimicrobial drugs and what each targets? | β-lactams (cell wall/PBPs), aminoglycosides & tetracyclines (30S), macrolides (50S), fluoroquinolones (DNA), sulfonamides (folate), etc. | Listed 9 classes with correct molecular targets, cited Microbiology Ch.14; added the antibiotic/antiviral/antifungal/antiparasitic grouping from Pharmacology Ch.7. | Relevant (all top hits 0.27–0.33, correct chapter) | **Accurate** |
| 2 | Nursing considerations for administering warfarin? | Monitor INR/PT, assess bleeding, vitamin K antidote, watch interacting drugs. | Correctly gave INR monitoring, bleeding/hgb/hct & platelet checks, same-time dosing, double-checks, and drug interactions — all from Pharmacology Ch.20. | Relevant (top hit 0.29 from correct chapter; 2 of 4 hits were loosely-related drug chapters) | **Accurate** |
| 3 | Common causes of bacterial meningitis and how is it diagnosed? | Causes: *N. meningitidis, S. pneumoniae, H. influenzae, S. agalactiae*; diagnosis: lumbar puncture / CSF analysis. | Gave the causative organisms correctly, **but stated it lacked information on diagnosis** and declined that half. | Partially relevant (causes retrieved; diagnostic-procedure chunk missed) | **Partially accurate** |
| 4 | What distinguishes active errors from latent conditions? | Active = unsafe acts by front-line staff (immediate); latent = upstream system/design weaknesses (dormant). | Correctly contrasted active failures (people in direct contact) vs latent conditions (designers/management decisions), citing the Patient Safety text + Pharmacology Ch.3. | Relevant (top hits 0.27–0.34; correct content, though pulled from an unexpected chapter) | **Accurate** |
| 5 | What's required to maintain sterile technique during district-hospital surgery? | Sterilized instruments, hand scrub, sterile gowns/gloves/drapes, maintain sterile field, skin antisepsis. | Gave equipment sterilization/storage, minimizing OR traffic, between-case cleaning, antiseptic immersion fallback, universal precautions — from WHO Surgical Care. | Relevant (all hits 0.31–0.35 from the WHO text) | **Accurate** |

**Summary:** 4 of 5 Accurate, 1 Partially accurate (Q3). Top-result cosine
distances ranged 0.26–0.35 — comfortably below the 0.5 quality bar.

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

**Question that failed:** Q3 — "What are the common causes of bacterial
meningitis and how is it diagnosed?"

**What the system returned:** The correct causative organisms (*H. influenzae,
N. meningitidis, S. pneumoniae, S. agalactiae*), but then: *"the sources provided
do not contain information on how bacterial meningitis is diagnosed… I don't have
enough information on that in my documents."* The diagnosis half was dropped even
though Microbiology Ch.26 does describe diagnosis (lumbar puncture, CSF Gram
stain/culture, glucose/protein).

**Root cause (tied to a specific pipeline stage): Retrieval — chunk redundancy
crowded out the diagnostic chunk.** The query embeds toward two distinct
sub-topics (*causes* and *diagnosis*), but top-k=4 returned **three near-duplicate
chunks from the Ch.26 overview** plus one reference-list chunk; the chunk
actually describing the diagnostic procedure ranked below position 4 and was never
passed to the LLM. This is a chunking↔retrieval interaction: ~200-token chunks
split the chapter's "causes" and "diagnosis" discussions into separate vectors,
and the overview/causes language matched the query more strongly, so the limited
top-k budget filled up with semantically similar (redundant) causes-chunks. The
grounding worked *correctly* — the model honestly refused the part it had no
context for, rather than hallucinating a diagnosis.

**What you would change to fix it:**
1. **Add diversity to retrieval (MMR / max-marginal-relevance)** so the top-k
   isn't dominated by near-duplicate chunks from the same passage — this would
   free a slot for the diagnostic chunk.
2. **Increase k** (e.g. 6–8) for multi-part questions, accepting slightly more
   prompt context.
3. **Query decomposition:** split a two-part question ("causes *and* diagnosis")
   into separate retrievals and merge the results before generation.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the Chunking
Strategy and Retrieval Approach sections *before* coding forced me to confront
the embedding model's 256-token limit up front, so the chunker was designed
around that constraint instead of discovering truncation after indexing. The
spec's "how I'll know the chunks are wrong" notes also gave me a concrete check
to run (inspect the chunk-size distribution), which is exactly what caught the
oversized chunks. Having the architecture diagram with each tool labeled
(PyMuPDF → MiniLM → ChromaDB → Groq) made wiring the stages together
mechanical rather than improvised.

**One way your implementation diverged from the spec, and why:** The spec
specified chunk size in **characters** (~1,000 chars). In implementation I
diverged to a **token-aware** chunker (~200 tokens, hard 256 cap) because
verifying against MiniLM's actual tokenizer revealed that clinical text
tokenizes far denser than ~4 chars/token — some 800-char chunks were 435 tokens
and would have been silently truncated. Character count turned out to be an
unreliable proxy for the thing that actually mattered (tokens vs. the model
limit), so I updated `planning.md` to reflect the token-based decision and the
reason for the change.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — Chunking implementation**

- *What I gave the AI:* My Documents and Chunking Strategy sections from
  `planning.md` (4 PDFs, ~1,000-char target, 15% overlap, sentence-aware) and
  asked it to implement the ingestion + chunking scripts.
- *What it produced:* A character-based recursive chunker (paragraph → sentence →
  hard word-cut) at ~1,000 chars with ~150-char overlap.
- *What I changed or overrode:* I verified the output against MiniLM's real
  tokenizer and found ~960 chunks over 256 tokens (max 435) — they'd be
  truncated at embed time. I overrode the design to be **token-aware**: measure
  every unit with the model's tokenizer, target ~200 tokens, hard-cap at 256.
  This dropped truncated chunks to **zero** and is the version in `chunk.py`.

**Instance 2 — Grounded generation prompt**

- *What I gave the AI:* My grounding requirement (answer from retrieved context
  only, cite sources, refuse when context is insufficient) and the retrieval
  function's output schema.
- *What it produced:* A first-pass `ask()` that injected the chunks and a system
  prompt instructing the model to use only the provided documents, plus a
  source list deduplicated by chapter.
- *What I changed or overrode:* (1) I removed the source dedup because it broke
  the `[Source N]` numbering — the answer cited `[Source 2]` but the displayed
  list had renumbered it; I made the displayed sources match the prompt's
  numbering exactly. (2) I added a **pre-LLM relevance gate**: if no retrieved
  chunk passes the distance threshold, return the refusal string without calling
  the model at all, so off-topic queries can't trigger a hallucinated answer.
