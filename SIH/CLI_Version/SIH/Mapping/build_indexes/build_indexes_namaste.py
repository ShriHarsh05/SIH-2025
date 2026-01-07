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
DATA_PATH = Path(r"D:\VIT\SIH with tm2\SIH\Mapping\data\namaste_data.json")
INDEX_DIR = Path(r"D:\VIT\SIH with tm2\SIH\Mapping\indexes")
INDEX_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------
# LOAD CLEAN SIDDHA DATA
# -------------------------------------------------------------
with open(DATA_PATH, "r", encoding="utf-8") as f:
    siddha = json.load(f)

codes = [x["tm2_code"] for x in siddha]
terms = [x["term"] for x in siddha]
definitions = [x["description"] for x in siddha]

docs = []
for term, defi in zip(terms, definitions):
    docs.append(f"{term}. {defi}" if defi else term)

# -------------------------------------------------------------
# BM25
# -------------------------------------------------------------
print("🔵 Building BM25...")
tokenized_docs = [d.lower().split() for d in docs]
bm25 = BM25Okapi(tokenized_docs)

with open(INDEX_DIR / "bm25_namaste.pkl", "wb") as f:
    pickle.dump({"model": bm25, "docs": docs, "codes": codes}, f)


# -------------------------------------------------------------
# TF-IDF
# -------------------------------------------------------------
print("🟢 Building TF-IDF...")
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(docs)

with open(INDEX_DIR / "tfidf_namaste.pkl", "wb") as f:
    pickle.dump({"vectorizer": tfidf, "docs": docs, "codes": codes}, f)

sparse.save_npz(INDEX_DIR / "tfidf_matrix_namaste.npz", tfidf_matrix)

# -------------------------------------------------------------
# EMBEDDINGS
# -------------------------------------------------------------
print("🟣 Building Embeddings...")
embedder = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")
embeddings = embedder.encode(docs, show_progress_bar=True)

np.save(INDEX_DIR / "embeddings_namaste.npy", embeddings)

with open(INDEX_DIR / "embeddings_namasate_meta.pkl", "wb") as f:
    pickle.dump({"codes": codes, "docs": docs}, f)

print("\n🎉 Indexing Complete!")
