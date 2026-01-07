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
DATA_PATH = BASE_DIR / "data" / "ayurveda_data.json"
INDEX_DIR = BASE_DIR / "indexes"
INDEX_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------
# LOAD AYURVEDA DATA
# -------------------------------------------------------------
print("📖 Loading Ayurveda data...")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    ayurveda = json.load(f)

codes = [x["tm2_code"] for x in ayurveda]
original_terms = [x["term"].lower() for x in ayurveda]
english_terms = [x["english"].lower() for x in ayurveda]
definitions = [x["description"].lower() for x in ayurveda]

# Build searchable documents with both original and English terms
docs = []
for orig_term, eng_term, defi in zip(original_terms, english_terms, definitions):
    # Include both original term and English term for better search
    if defi and defi != "No description available.":
        docs.append(f"{orig_term}. {eng_term}. {defi}")
    else:
        docs.append(f"{orig_term}. {eng_term}")

print(f"✅ Loaded {len(docs)} Ayurveda entries")

# -------------------------------------------------------------
# BM25
# -------------------------------------------------------------
print("🔵 Building BM25...")
tokenized_docs = [d.lower().split() for d in docs]
bm25 = BM25Okapi(tokenized_docs)

with open(INDEX_DIR / "bm25_ayurveda.pkl", "wb") as f:
    pickle.dump({"model": bm25, "docs": docs, "codes": codes}, f)

# -------------------------------------------------------------
# TF-IDF
# -------------------------------------------------------------
print("🟢 Building TF-IDF...")
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(docs)

with open(INDEX_DIR / "tfidf_ayurveda.pkl", "wb") as f:
    pickle.dump({"vectorizer": tfidf, "docs": docs, "codes": codes}, f)

sparse.save_npz(INDEX_DIR / "tfidf_matrix_ayurveda.npz", tfidf_matrix)

# -------------------------------------------------------------
# EMBEDDINGS
# -------------------------------------------------------------
print("🟣 Building Embeddings...")
embedder = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")
embeddings = embedder.encode(docs, show_progress_bar=True)

np.save(INDEX_DIR / "embeddings_ayurveda.npy", embeddings)

with open(INDEX_DIR / "embeddings_ayurveda_meta.pkl", "wb") as f:
    pickle.dump({
        "codes": codes,
        "original_terms": original_terms,
        "english_terms": english_terms,
        "definitions": definitions,
        "docs": docs
    }, f)

print("\n🎉 Ayurveda Indexing Complete!")
