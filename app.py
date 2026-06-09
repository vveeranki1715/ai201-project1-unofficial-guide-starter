"""
Milestone 5 — Gradio interface
==============================

Minimal web UI over the RAG pipeline. Enter a question; the system retrieves
relevant chunks, generates a grounded answer with the Groq LLM, and shows which
sources the answer was drawn from.

Run:  .venv/bin/python app.py    then open http://localhost:7860
"""

from __future__ import annotations

import gradio as gr

from query import ask


def handle_query(question: str):
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(result["sources"]) or "(no sufficiently relevant sources found)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — Clinical Study Assistant") as demo:
    gr.Markdown(
        "# The Unofficial Guide — Clinical Study Assistant\n"
        "Ask a question about microbiology, pharmacology, surgical care, or "
        "patient safety. Answers are grounded in four open-access textbooks and "
        "cite their source chapter and page."
    )
    inp = gr.Textbox(label="Your question",
                     placeholder="e.g. What are the major classes of antimicrobial drugs?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=5)
    gr.Examples(
        examples=[
            "What are the major classes of antimicrobial drugs and what does each target?",
            "What nursing considerations apply when administering warfarin?",
            "What are the common causes of bacterial meningitis and how is it diagnosed?",
            "How do I file my taxes?",  # out-of-domain — should decline
        ],
        inputs=inp,
    )
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
