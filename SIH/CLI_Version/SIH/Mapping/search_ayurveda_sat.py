#!/usr/bin/env python3
"""
Search module for Ayurveda-SAT system
Hybrid retrieval: BM25 → TF-IDF → Semantic ranking
"""

import json
import pickle
import numpy as np
from pathlib import Path

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
from sentence_transformers import SentenceTransformer, util

# -------------------------------------------------------------
# PATHS
# -------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "ayurveda_sat_data.json"
INDEX_DIR = BASE_DIR / "indexes"

# -------------------------------------------------------------
# LOAD DATA (for fallback if old index format)
# -------------------------------------------------------------
with open(DATA_PATH, "r", encoding="utf-8") as f:
    ayurveda_sat_data = json.load(f)

# -------------------------------------------------------------
# LOAD INDEX FILES
# -------------------------------------------------------------
bm25_data = pickle.load(open(INDEX_DIR / "bm25_ayurveda_sat.pkl", "rb"))
bm25 = bm25_data["model"]

# Load metadata from BM25 data (includes codes, terms, definitions)
if "codes" in bm25_data:
    codes = bm25_data["codes"]
    terms = bm25_data["terms"]
    definitions = bm25_data["definitions"]
else:
    # Fallback to loading from original data if old index format
    codes = [x["code"] for x in ayurveda_sat_data]
    terms = [x["term"] for x in ayurveda_sat_data]
    definitions = [x["definition"] for x in ayurveda_sat_data]

tfidf_data = pickle.load(open(INDEX_DIR / "tfidf_ayurveda_sat.pkl", "rb"))
tfidf_vectorizer = tfidf_data["vectorizer"]

tfidf_matrix = sparse.load_npz(INDEX_DIR / "tfidf_matrix_ayurveda_sat.npz")

embeddings = np.load(INDEX_DIR / "embeddings_ayurveda_sat.npy")
embed_meta = pickle.load(open(INDEX_DIR / "embeddings_ayurveda_sat_meta.pkl", "rb"))

embedder = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")

# -------------------------------------------------------------
# SEARCH FUNCTIONS
# -------------------------------------------------------------
def bm25_search(query, top_k=50):
    """Stage 1: BM25 retrieval"""
    tokenized = query.lower().split()
    scores = bm25.get_scores(tokenized)
    top_ids = np.argsort(scores)[::-1][:top_k]
    return top_ids


def tfidf_rerank(query, candidate_ids, top_k=20):
    """Stage 2: TF-IDF re-ranking"""
    q_vec = tfidf_vectorizer.transform([query])
    sub_matrix = tfidf_matrix[candidate_ids]
    scores = (sub_matrix @ q_vec.T).toarray().flatten()
    top_local = np.argsort(scores)[::-1][:top_k]
    return [candidate_ids[i] for i in top_local]


def semantic_rerank(query, candidate_ids, top_k=10):
    """Stage 3: Semantic re-ranking"""
    q_emb = embedder.encode([query])[0]
    sub_emb = embeddings[candidate_ids]
    scores = util.cos_sim(q_emb, sub_emb).cpu().numpy()[0]
    top_local = np.argsort(scores)[::-1][:top_k]
    
    return [
        {
            "code": codes[candidate_ids[i]],
            "term": terms[candidate_ids[i]],
            "definition": definitions[candidate_ids[i]] if definitions[candidate_ids[i]] else "No description available.",
            "score": float(scores[i])
        }
        for i in top_local
    ]


# -------------------------------------------------------------
# UNIFIED SEARCH PIPELINE
# -------------------------------------------------------------
def search_ayurveda_sat(query):
    """
    Unified search pipeline for Ayurveda-SAT
    
    Args:
        query: Search query string
    
    Returns:
        Dictionary with candidates list
    """
    # Stage 1 — BM25 (find 50)
    bm25_ids = bm25_search(query, top_k=100)
    
    # Stage 2 — TF-IDF re-rank (down to 20)
    tfidf_ids = tfidf_rerank(query, bm25_ids, top_k=60)
    
    # Stage 3 — Semantic re-rank (final 10)
    candidates = semantic_rerank(query, tfidf_ids, top_k=10)
    
    return {"candidates": candidates}


# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------
if __name__ == "__main__":
    # Test search
    test_query = "disease syndrome pain distress"
    
    print("=" * 70)
    print("AYURVEDA-SAT SEARCH TEST")
    print("=" * 70)
    print(f"\nQuery: {test_query}")
    
    result = search_ayurveda_sat(test_query)
    
    print(f"\nTop {len(result['candidates'])} Results:")
    print("-" * 70)
    
    for i, candidate in enumerate(result["candidates"], 1):
        print(f"\n{i}. Code: {candidate['code']}")
        print(f"   Term: {candidate['term']}")
        print(f"   Definition: {candidate['definition'][:100]}..." if len(candidate['definition']) > 100 else f"   Definition: {candidate['definition']}")
        print(f"   Score: {candidate['score']:.4f}")
    
    print("\n" + "=" * 70)
