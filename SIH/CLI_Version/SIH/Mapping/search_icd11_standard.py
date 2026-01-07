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
DATA_PATH = BASE_DIR / "data" / "icd11_standard.json"
INDEX_DIR = BASE_DIR / "indexes"

# -------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------
with open(DATA_PATH, "r", encoding="utf-8") as f:
    icd = json.load(f)

codes = [x["code"] for x in icd]
titles = [x["title"] for x in icd]
definitions = [x.get("definition", "") or "" for x in icd]

docs = []
for title, defi in zip(titles, definitions):
    if defi:
        docs.append(f"{title}. {defi}")
    else:
        docs.append(title)

# -------------------------------------------------------------
# LOAD INDEX FILES
# -------------------------------------------------------------
bm25_data = pickle.load(open(INDEX_DIR / "bm25_icd11_standard.pkl", "rb"))
bm25 = bm25_data["model"]

tfidf_data = pickle.load(open(INDEX_DIR / "tfidf_icd11_standard.pkl", "rb"))
tfidf_vectorizer = tfidf_data["vectorizer"]

tfidf_matrix = sparse.load_npz(INDEX_DIR / "tfidf_matrix_icd11_standard.npz")

embeddings = np.load(INDEX_DIR / "embeddings_icd11_standard.npy")
embed_meta = pickle.load(open(INDEX_DIR / "embeddings_icd11_standard_meta.pkl", "rb"))

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
            "title": titles[candidate_ids[i]],
            "definition": definitions[candidate_ids[i]],
            "score": float(scores[i])
        }
        for i in top_local
    ]

# -------------------------------------------------------------
# UNIFIED SEARCH PIPELINE
# -------------------------------------------------------------
def search_icd11_standard(query):
    bm25_ids = bm25_search(query, top_k=100)
    tfidf_ids = tfidf_rerank(query, bm25_ids, top_k=60)
    candidates = semantic_rerank(query, tfidf_ids, top_k=10)
    return {"candidates": candidates}

# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------
if __name__ == "__main__":
    q = "cholera infection"
    ans = search_icd11_standard(q)
    print("\nTOP CANDIDATES:")
    for item in ans["candidates"]:
        print(item)
