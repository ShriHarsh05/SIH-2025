# -------------------------------------------------------------
# autocomplete.py  (Fast Autocomplete for Siddha Terms)
# -------------------------------------------------------------
import json
import re
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()

# Load datasets
BASE_DIR = Path(__file__).parent.parent
SIDDHA_PATH = BASE_DIR / "data" / "siddha_clean.json"
AYURVEDA_PATH = BASE_DIR / "data" / "ayurveda_data.json"
UNANI_PATH = BASE_DIR / "data" / "unani_data.json"

with open(SIDDHA_PATH, "r", encoding="utf-8") as f:
    siddha = json.load(f)

with open(AYURVEDA_PATH, "r", encoding="utf-8") as f:
    ayurveda_raw = json.load(f)
    # Convert to same format as siddha
    ayurveda = [
        {
            "code": x["tm2_code"],
            "term": x["english"],
            "definition": x["description"]
        }
        for x in ayurveda_raw
    ]

with open(UNANI_PATH, "r", encoding="utf-8") as f:
    unani_raw = json.load(f)
    # Convert to same format as siddha
    unani = [
        {
            "code": x["tm2_code"],
            "term": x["english"],
            "definition": x["description"]
        }
        for x in unani_raw
    ]


# -------------------------------------------------------------
# Utility — Normalize for search
# -------------------------------------------------------------
def normalize(text):
    return re.sub(r"[^a-zA-Z0-9 ]", "", text.lower())


# -------------------------------------------------------------
# MAIN SEARCH FUNCTION
# -------------------------------------------------------------
def autocomplete_search(query, dataset):
    query = normalize(query)

    if len(query) < 2:
        return []  # don't return anything for 1-letter matches

    results = []

    # Priority 1: prefix match (best UX)
    for item in dataset:
        if normalize(item["term"]).startswith(query) or normalize(item["code"]).startswith(query) or normalize(item["definition"]).startswith(query):
            results.append(item)

    # Priority 2: substring match (contains)
    if len(results) < 20:
        for item in dataset:
            blob = normalize(item["term"] + " " + item["code"] + " " + item["definition"])
            if query in blob and item not in results:
                results.append(item)

    # Priority 3: fallback — return top 10 unique
    return results[:20]


# -------------------------------------------------------------
# API ROUTES
# -------------------------------------------------------------
@router.get("/siddha/autocomplete")
def siddha_autocomplete(q: str):
    matches = autocomplete_search(q, siddha)
    return {"query": q, "results": matches}

@router.get("/ayurveda/autocomplete")
def ayurveda_autocomplete(q: str):
    matches = autocomplete_search(q, ayurveda)
    return {"query": q, "results": matches}

@router.get("/unani/autocomplete")
def unani_autocomplete(q: str):
    matches = autocomplete_search(q, unani)
    return {"query": q, "results": matches}
