# -------------------------------------------------------------
# build_indexes_icd.py
# -------------------------------------------------------------
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
DATA_PATH = Path(r"C:\Users\Shriharsh\Downloads\SIH(10)\SIH\Mapping\data\icd11_no_num.json")
INDEX_DIR = Path(r"C:\Users\Shriharsh\Downloads\SIH(10)\SIH\Mapping\indexes")
INDEX_DIR.mkdir(exist_ok=True)


# -------------------------------------------------------------
# LOAD CLEAN ICD DATA
# -------------------------------------------------------------
with open(DATA_PATH, "r", encoding="utf-8") as f:
    icd = json.load(f)

codes = [x["code"] for x in icd]
titles = [x["title"] for x in icd]
definitions = [x.get("definition", "") for x in icd]

# Each searchable document = title + definition
docs = []
for title, defi in zip(titles, definitions):
    if defi:
        docs.append(f"{title}. {defi}")
    else:
        docs.append(title)


# -------------------------------------------------------------
# 1) BM25 INDEX
# -------------------------------------------------------------
print("🔵 Building BM25 (ICD)...")

tokenized_docs = [d.lower().split() for d in docs]
bm25 = BM25Okapi(tokenized_docs)

with open(INDEX_DIR / "bm25_icd.pkl", "wb") as f:
    pickle.dump({
        "model": bm25,
        "docs": docs,
        "codes": codes
    }, f)


# -------------------------------------------------------------
# 2) TF-IDF INDEX
# -------------------------------------------------------------
print("🟢 Building TF-IDF (ICD)...")

tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(docs)

with open(INDEX_DIR / "tfidf_icd.pkl", "wb") as f:
    pickle.dump({
        "vectorizer": tfidf,
        "docs": docs,
        "codes": codes
    }, f)

sparse.save_npz(INDEX_DIR / "tfidf_matrix_icd.npz", tfidf_matrix)


# -------------------------------------------------------------
# 3) MINI-LM EMBEDDING INDEX
# -------------------------------------------------------------
print("🟣 Building Embeddings (ICD)...")

embedder = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")
embeddings = embedder.encode(docs, show_progress_bar=True)

np.save(INDEX_DIR / "embeddings_icd.npy", embeddings)

with open(INDEX_DIR / "embeddings_icd_meta.pkl", "wb") as f:
    pickle.dump({
        "codes": codes,
        "docs": docs
    }, f)

print("\n🎉 ICD Indexing Complete!")
