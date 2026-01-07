# -------------------------------------------------------------
# search_siddha.py
# -------------------------------------------------------------
import json
import pickle
import numpy as np
from pathlib import Path

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
from sentence_transformers import SentenceTransformer, util
from groq import Groq

from dotenv import load_dotenv
import os
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# -------------------------------------------------------------
# PATHS
# -------------------------------------------------------------
DATA_PATH = Path(r"D:\VIT\SIH with tm2\SIH\Mapping\data\siddha_clean.json")
INDEX_DIR = Path(r"D:\VIT\SIH with tm2\SIH\Mapping\indexes")
INDEX_DIR.mkdir(exist_ok=True)
# -------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------
with open(DATA_PATH, "r", encoding="utf-8") as f:
    siddha = json.load(f)

codes = [x["code"] for x in siddha]
terms = [x["term"] for x in siddha]
defs = [x["definition"] for x in siddha]

docs = []
for c, t, d in zip(codes,terms, defs):
    docs.append(f"{c}. {t}. {d}" if d else t)


# -------------------------------------------------------------
# LOAD INDEX FILES
# -------------------------------------------------------------
bm25_data = pickle.load(open(INDEX_DIR / "bm25_siddha.pkl", "rb"))
bm25 = bm25_data["model"]

tfidf_data = pickle.load(open(INDEX_DIR / "tfidf_siddha.pkl", "rb"))
tfidf_vectorizer = tfidf_data["vectorizer"]

tfidf_matrix = sparse.load_npz(INDEX_DIR / "tfidf_matrix_siddha.npz")

embeddings = np.load(INDEX_DIR / "embeddings_siddha.npy")
embed_meta = pickle.load(open(INDEX_DIR / "embeddings_siddha_meta.pkl", "rb"))

embedder = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")


# -------------------------------------------------------------
# SEARCH FUNCTIONS
# -------------------------------------------------------------
def bm25_search(query, top_k=50):
    tokenized = query.lower().split()
    scores = bm25.get_scores(tokenized)

    top_ids = np.argsort(scores)[::-1][:top_k]
    return top_ids


def tfidf_rerank(query, candidate_ids, top_k=20):
    q_vec = tfidf_vectorizer.transform([query])
    sub_matrix = tfidf_matrix[candidate_ids]

    scores = (sub_matrix @ q_vec.T).toarray().flatten()
    top_local = np.argsort(scores)[::-1][:top_k]

    return [candidate_ids[i] for i in top_local]


def semantic_rerank(query, candidate_ids, top_k=5):
    q_emb = embedder.encode([query])[0]
    sub_emb = embeddings[candidate_ids]

    scores = util.cos_sim(q_emb, sub_emb).cpu().numpy()[0]
    top_local = np.argsort(scores)[::-1][:top_k]

    return [
        {"code": codes[candidate_ids[i]],
         "term": terms[candidate_ids[i]],
         "score": float(scores[i])}
        for i in top_local
    ]

# -------------------------------------------------------------
# 4) LLM Refinement — pick the BEST Siddha diagnosis
# -------------------------------------------------------------
def refine_with_llm(query, candidates):
    """
    candidates = list of dicts:
    [{"code": "...", "term": "...", "score": 0.xx}, ...]
    """

    # Format candidate list for LLM
    cand_text = "\n".join(
        [f"{i+1}. {c['code']} — {c['term']}" for i, c in enumerate(candidates)]
    )

    prompt = f"""
    User symptoms:
    "{query}"

    Here are Siddha diagnosis candidates:

    {cand_text}

    Pick the SINGLE best Siddha diagnosis that matches the symptoms.
    Return ONLY JSON like:
    {{"code": "...", "reason": "..."}}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.2
        )

        raw = response.choices[0].message.content.strip()

        # Safe JSON extraction
        import json
        result = json.loads(raw)
        return result

    except Exception as e:
        print("LLM refine error:", e)
        # fallback → return first candidate
        return {"code": candidates[0]["code"], "reason": "fallback"}

# -------------------------------------------------------------
# UNIFIED SEARCH PIPELINE
# -------------------------------------------------------------
def search_siddha(query):
    # Stage 1 — BM25 (find 50)
    bm25_ids = bm25_search(query, top_k=100)

    # Stage 2 — TF-IDF re-rank (down to 20)
    tfidf_ids = tfidf_rerank(query, bm25_ids, top_k=60)

    # Stage 3 — Semantic re-rank (final 5)
    candidates = semantic_rerank(query, tfidf_ids, top_k=10)

    

    return { "candidates": candidates}



# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------
if __name__ == "__main__":
    q = "hard swelling and redness in eyelids, itching. May be associated with crusting at the eyelid margins or base of the eyelashes, flaking of skin on eyelids, falling of eye lashes. [AYU] aggravated kapha, vata affecting skin, blood and muscle tissue."
    ans = search_siddha(q)

    print("\nFINAL BEST MATCH:")
    print(ans["final"])

    print("\nTOP 5 CANDIDATES:")
    for item in ans["candidates"]:
        print(item)
