#!/usr/bin/env python3
"""
Build search indexes for Ayurveda-SAT system
Creates BM25, TF-IDF, and embedding indexes with full metadata
"""

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

print("=" * 70)
print("BUILDING AYURVEDA-SAT INDEXES")
print("=" * 70)

# -------------------------------------------------------------
# PATHS
# -------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "ayurveda_sat_data.json"
INDEX_DIR = BASE_DIR / "indexes"
INDEX_DIR.mkdir(exist_ok=True)

print(f"\nData file: {DATA_PATH}")
print(f"Index directory: {INDEX_DIR}")

# -------------------------------------------------------------
# LOAD AYURVEDA-SAT DATA
# -------------------------------------------------------------
print("\nLoading Ayurveda-SAT data...")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    ayurveda_sat_data = json.load(f)

print(f"Loaded {len(ayurveda_sat_data)} Ayurveda-SAT entries")

# Extract fields
codes = []
terms = []
definitions = []

for entry in ayurveda_sat_data:
    codes.append(entry.get("code", ""))
    terms.append(entry.get("term", ""))
    definitions.append(entry.get("definition", ""))

# Create searchable documents (code + term + definition)
docs = []
for code, term, definition in zip(codes, terms, definitions):
    if definition:
        docs.append(f"{code}. {term}. {definition}")
    else:
        docs.append(f"{code}. {term}")

print(f"Created {len(docs)} searchable documents")

# -------------------------------------------------------------
# BUILD BM25 INDEX
# -------------------------------------------------------------
print("\n🔵 Building BM25 index...")
tokenized_docs = [doc.lower().split() for doc in docs]
bm25 = BM25Okapi(tokenized_docs)

bm25_data = {
    "model": bm25,
    "codes": codes,
    "terms": terms,
    "definitions": definitions,
    "docs": docs
}

bm25_path = INDEX_DIR / "bm25_ayurveda_sat.pkl"
with open(bm25_path, "wb") as f:
    pickle.dump(bm25_data, f)

print(f"✓ BM25 index saved: {bm25_path}")

# -------------------------------------------------------------
# BUILD TF-IDF INDEX
# -------------------------------------------------------------
print("\n🟢 Building TF-IDF index...")
tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = tfidf_vectorizer.fit_transform(docs)

tfidf_data = {
    "vectorizer": tfidf_vectorizer,
    "codes": codes,
    "terms": terms,
    "definitions": definitions,
    "docs": docs
}

tfidf_path = INDEX_DIR / "tfidf_ayurveda_sat.pkl"
with open(tfidf_path, "wb") as f:
    pickle.dump(tfidf_data, f)

tfidf_matrix_path = INDEX_DIR / "tfidf_matrix_ayurveda_sat.npz"
sparse.save_npz(tfidf_matrix_path, tfidf_matrix)

print(f"✓ TF-IDF index saved: {tfidf_path}")
print(f"✓ TF-IDF matrix saved: {tfidf_matrix_path}")

# -------------------------------------------------------------
# BUILD EMBEDDING INDEX
# -------------------------------------------------------------
print("\n🟣 Building embedding index...")
print("Loading sentence transformer model...")
embedder = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")

print("Encoding documents (this may take a few minutes)...")
embeddings = embedder.encode(docs, show_progress_bar=True, batch_size=32)

embeddings_path = INDEX_DIR / "embeddings_ayurveda_sat.npy"
np.save(embeddings_path, embeddings)

embeddings_meta = {
    "codes": codes,
    "terms": terms,
    "definitions": definitions,
    "docs": docs,
    "model_name": "pritamdeka/S-PubMedBert-MS-MARCO"
}

embeddings_meta_path = INDEX_DIR / "embeddings_ayurveda_sat_meta.pkl"
with open(embeddings_meta_path, "wb") as f:
    pickle.dump(embeddings_meta, f)

print(f"✓ Embeddings saved: {embeddings_path}")
print(f"✓ Embeddings metadata saved: {embeddings_meta_path}")

# -------------------------------------------------------------
# SUMMARY
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("AYURVEDA-SAT INDEX BUILDING COMPLETE")
print("=" * 70)
print(f"\nTotal entries indexed: {len(codes)}")
print(f"Index files created:")
print(f"  - {bm25_path.name}")
print(f"  - {tfidf_path.name}")
print(f"  - {tfidf_matrix_path.name}")
print(f"  - {embeddings_path.name}")
print(f"  - {embeddings_meta_path.name}")
print("\n✓ All Ayurveda-SAT indexes built successfully!")
print("=" * 70)
