"""
Answer generation service.

Takes the farmer's English-translated question plus the retrieved knowledge-
base entries, and asks Claude to produce a short, grounded answer. The
prompt explicitly instructs the model to only use the provided context and
say so if the context doesn't cover the question — this is what keeps
Krishi Sahayak from hallucinating agricultural or scheme advice.
"""

import os
from typing import List, Dict, Tuple
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

SYSTEM_PROMPT = """You are Krishi Sahayak, a voice assistant that gives farmers in India \
grounded, practical advice on crops, fertilizer, pests, and government schemes.

Rules you must always follow:
- Only use the information given to you in the "Context" section below to answer.
- If the context does not contain enough information to answer the question, say so \
plainly and suggest the farmer consult their local agriculture extension office \
instead of guessing.
- Keep the answer short (2-4 sentences), practical, and in plain English — it will \
be translated to Telugu and read aloud, so avoid complex sentence structure, \
bullet points, or markdown.
- Never state that you have submitted, applied for, or filed anything on the \
farmer's behalf. You may only explain steps the farmer themselves would take.
"""


def generate_answer(english_question: str, retrieved: List[Tuple[Dict, float]]) -> Tuple[str, str]:
    """
    Returns (answer_text, matched_source_id). matched_source_id is None if
    nothing relevant was retrieved (low-confidence / out-of-scope question).
    """
    if not retrieved:
        return (
            "I don't have grounded information on that yet in my knowledge base. "
            "Please check with your local agriculture extension office or the "
            "official government portal for this.",
            None,
        )

    context_blocks = []
    for entry, score in retrieved:
        context_blocks.append(f"- Source [{entry['id']}]: {entry['answer']}")
    context_text = "\n".join(context_blocks)

    user_message = f"""Context:
{context_text}

Farmer's question: {english_question}

Answer the farmer's question using only the context above."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    answer_text = "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()

    best_match_id = retrieved[0][0]["id"]
    return answer_text, best_match_id
