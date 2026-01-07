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
DATA_PATH = BASE_DIR / "data" / "ayurveda_data.json"
INDEX_DIR = BASE_DIR / "indexes"

# -------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------
with open(DATA_PATH, "r", encoding="utf-8") as f:
    ayurveda = json.load(f)

codes = [x["tm2_code"] for x in ayurveda]
original_terms = [x["term"] for x in ayurveda]
english_terms = [x["english"] for x in ayurveda]
definitions = [x["description"] for x in ayurveda]

docs = []
for orig_term, eng_term, defi in zip(original_terms, english_terms, definitions):
    if defi and defi != "No description available.":
        docs.append(f"{orig_term}. {eng_term}. {defi}")
    else:
        docs.append(f"{orig_term}. {eng_term}")

# -------------------------------------------------------------
# LOAD INDEX FILES
# -------------------------------------------------------------
bm25_data = pickle.load(open(INDEX_DIR / "bm25_ayurveda.pkl", "rb"))
bm25 = bm25_data["model"]

tfidf_data = pickle.load(open(INDEX_DIR / "tfidf_ayurveda.pkl", "rb"))
tfidf_vectorizer = tfidf_data["vectorizer"]

tfidf_matrix = sparse.load_npz(INDEX_DIR / "tfidf_matrix_ayurveda.npz")

embeddings = np.load(INDEX_DIR / "embeddings_ayurveda.npy")
embed_meta = pickle.load(open(INDEX_DIR / "embeddings_ayurveda_meta.pkl", "rb"))

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
        {
            "code": codes[candidate_ids[i]],
            "term": original_terms[candidate_ids[i]],
            "english": english_terms[candidate_ids[i]],
            "definition": definitions[candidate_ids[i]],
            "score": float(scores[i])
        }
        for i in top_local
    ]

# -------------------------------------------------------------
# UNIFIED SEARCH PIPELINE
# -------------------------------------------------------------
def search_ayurveda(query):
    bm25_ids = bm25_search(query, top_k=100)
    tfidf_ids = tfidf_rerank(query, bm25_ids, top_k=60)
    candidates = semantic_rerank(query, tfidf_ids, top_k=10)
    return {"candidates": candidates}

# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------
if __name__ == "__main__":
    q = "knee pain and swelling"
    ans = search_ayurveda(q)
    print("\nTOP CANDIDATES:")
    for item in ans["candidates"]:
        print(item)
