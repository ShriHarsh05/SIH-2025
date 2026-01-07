import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_TF"] = "1"

import json
import pickle
import numpy as np
from pathlib import Path

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from scipy import sparse

# -------------------------------------------------------------
# PATHS
# -------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "icd11_standard.json"
INDEX_DIR = BASE_DIR / "indexes"
INDEX_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------
# LOAD ICD-11 STANDARD DATA
# -------------------------------------------------------------
print("📖 Loading ICD-11 Standard data...")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    icd = json.load(f)

codes = [x["code"] for x in icd]
titles = [x["title"] for x in icd]
definitions = [x.get("definition", "") or "" for x in icd]

# Each searchable document = title + definition
docs = []
for title, defi in zip(titles, definitions):
    if defi:
        docs.append(f"{title}. {defi}")
    else:
        docs.append(title)

print(f"✅ Loaded {len(docs)} ICD-11 Standard entries")

# -------------------------------------------------------------
# BM25 INDEX
# -------------------------------------------------------------
print("🔵 Building BM25 (ICD-11 Standard)...")
tokenized_docs = [d.lower().split() for d in docs]
bm25 = BM25Okapi(tokenized_docs)

with open(INDEX_DIR / "bm25_icd11_standard.pkl", "wb") as f:
    pickle.dump({
        "model": bm25,
        "docs": docs,
        "codes": codes
    }, f)

# -------------------------------------------------------------
# TF-IDF INDEX
# -------------------------------------------------------------
print("🟢 Building TF-IDF (ICD-11 Standard)...")
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(docs)

with open(INDEX_DIR / "tfidf_icd11_standard.pkl", "wb") as f:
    pickle.dump({
        "vectorizer": tfidf,
        "docs": docs,
        "codes": codes
    }, f)

sparse.save_npz(INDEX_DIR / "tfidf_matrix_icd11_standard.npz", tfidf_matrix)

# -------------------------------------------------------------
# EMBEDDINGS INDEX
# -------------------------------------------------------------
print("🟣 Building Embeddings (ICD-11 Standard)...")
embedder = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")
embeddings = embedder.encode(docs, show_progress_bar=True)

np.save(INDEX_DIR / "embeddings_icd11_standard.npy", embeddings)

with open(INDEX_DIR / "embeddings_icd11_standard_meta.pkl", "wb") as f:
    pickle.dump({
        "codes": codes,
        "docs": docs
    }, f)

print("\n🎉 ICD-11 Standard Indexing Complete!")
