"""
Retrieval service — the "R" in RAG.

Loads the curated knowledge base (backend/app/data/knowledge_base.json) and,
for a given English question, finds the most similar entries using TF-IDF +
cosine similarity. This keeps the MVP dependency-light (scikit-learn only,
no vector DB or embedding API needed) while still grounding every answer in
a real source rather than letting the LLM free-generate agricultural advice.

For a larger knowledge base, swap this for a proper embedding-based vector
store (e.g. FAISS + sentence-transformers) without changing the public
`retrieve` function's signature.
"""

import json
import os
from typing import List, Dict, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.json")

with open(_DATA_PATH, "r", encoding="utf-8") as f:
    _KNOWLEDGE_BASE: List[Dict] = json.load(f)

_CORPUS = [entry["question"] for entry in _KNOWLEDGE_BASE]
_VECTORIZER = TfidfVectorizer(stop_words="english")
_TFIDF_MATRIX = _VECTORIZER.fit_transform(_CORPUS)


def knowledge_base_size() -> int:
    return len(_KNOWLEDGE_BASE)


def retrieve(english_question: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
    """
    Return up to top_k (entry, similarity_score) pairs, most relevant first.
    """
    query_vec = _VECTORIZER.transform([english_question])
    scores = cosine_similarity(query_vec, _TFIDF_MATRIX)[0]
    ranked_indices = scores.argsort()[::-1][:top_k]
    return [(_KNOWLEDGE_BASE[i], float(scores[i])) for i in ranked_indices if scores[i] > 0]
