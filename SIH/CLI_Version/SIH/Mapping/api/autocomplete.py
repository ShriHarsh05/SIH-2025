# -------------------------------------------------------------
# autocomplete.py  (Fast Autocomplete with Fuzzy Matching & Google Search Fallback)
# -------------------------------------------------------------
import json
import re
import os
from pathlib import Path
from fastapi import APIRouter
import httpx
from typing import List, Dict, Tuple

router = APIRouter()

# Google Custom Search API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")

# Load datasets
BASE_DIR = Path(__file__).parent.parent
SIDDHA_PATH = BASE_DIR / "data" / "siddha_clean.json"
AYURVEDA_PATH = BASE_DIR / "data" / "ayurveda_data.json"
UNANI_PATH = BASE_DIR / "data" / "unani_data.json"
AYURVEDA_SAT_PATH = BASE_DIR / "data" / "ayurveda_sat_data.json"

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

with open(AYURVEDA_SAT_PATH, "r", encoding="utf-8") as f:
    ayurveda_sat = json.load(f)


# -------------------------------------------------------------
# Utility — Normalize for search
# -------------------------------------------------------------
def normalize(text):
    return re.sub(r"[^a-zA-Z0-9 ]", "", text.lower())


# -------------------------------------------------------------
# Fuzzy Matching — Levenshtein Distance (Typo Correction)
# -------------------------------------------------------------
def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    Returns the minimum number of single-character edits needed.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def fuzzy_match_terms(query: str, dataset: List[Dict], max_distance: int = 2) -> List[Tuple[Dict, int]]:
    """
    Find terms that are similar to the query using fuzzy matching.
    Returns list of (item, distance) tuples sorted by distance.
    
    Args:
        query: Search query
        dataset: List of items to search
        max_distance: Maximum Levenshtein distance to consider (default: 2)
    
    Returns:
        List of (item, distance) tuples where distance <= max_distance
    """
    query_norm = normalize(query)
    matches = []
    
    for item in dataset:
        # Check term, code, and first few words of definition
        term_norm = normalize(item["term"])
        code_norm = normalize(item["code"])
        
        # Calculate distances
        term_distance = levenshtein_distance(query_norm, term_norm)
        code_distance = levenshtein_distance(query_norm, code_norm)
        
        # Also check if query is close to any word in the term
        term_words = term_norm.split()
        word_distances = [levenshtein_distance(query_norm, word) for word in term_words if len(word) > 2]
        min_word_distance = min(word_distances) if word_distances else float('inf')
        
        # Use the best (minimum) distance
        best_distance = min(term_distance, code_distance, min_word_distance)
        
        if best_distance <= max_distance:
            matches.append((item, best_distance))
    
    # Sort by distance (closest first)
    matches.sort(key=lambda x: x[1])
    
    return matches


# -------------------------------------------------------------
# MAIN SEARCH FUNCTION WITH FUZZY MATCHING
# -------------------------------------------------------------
def autocomplete_search(query, dataset):
    query_norm = normalize(query)

    if len(query_norm) < 2:
        return {"results": [], "fuzzy_suggestions": []}

    results = []
    fuzzy_suggestions = []

    # Priority 1: Exact prefix match (best UX)
    for item in dataset:
        term_norm = normalize(item["term"])
        code_norm = normalize(item["code"])
        def_norm = normalize(item["definition"])
        
        if term_norm.startswith(query_norm) or code_norm.startswith(query_norm) or def_norm.startswith(query_norm):
            results.append(item)

    # Priority 2: Substring match (contains)
    if len(results) < 20:
        for item in dataset:
            blob = normalize(item["term"] + " " + item["code"] + " " + item["definition"])
            if query_norm in blob and item not in results:
                results.append(item)

    # Priority 3: Fuzzy matching for typos (if no exact matches found)
    if len(results) == 0 and len(query_norm) >= 3:
        # Use fuzzy matching to find similar terms
        fuzzy_matches = fuzzy_match_terms(query_norm, dataset, max_distance=2)
        
        if fuzzy_matches:
            # Add top fuzzy matches as suggestions
            for item, distance in fuzzy_matches[:5]:
                fuzzy_suggestions.append({
                    "item": item,
                    "distance": distance,
                    "suggestion_text": f"Did you mean '{item['term']}'?"
                })
            
            # Also add them to results
            results = [item for item, _ in fuzzy_matches[:10]]

    return {
        "results": results[:20],
        "fuzzy_suggestions": fuzzy_suggestions,
        "has_fuzzy": len(fuzzy_suggestions) > 0
    }


# -------------------------------------------------------------
# GOOGLE SEARCH FALLBACK
# -------------------------------------------------------------
async def google_search_fallback(query: str, system: str) -> List[Dict]:
    """
    Fallback to Google Custom Search API when no local results found.
    Searches for medical/traditional medicine terms related to the query.
    """
    if not GOOGLE_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        return []
    
    try:
        # Enhance query with system context
        system_context = {
            "siddha": "Siddha medicine",
            "ayurveda": "Ayurveda medicine",
            "unani": "Unani medicine",
            "ayurveda-sat": "Ayurveda SAT"
        }
        
        search_query = f"{query} {system_context.get(system, 'traditional medicine')} term definition"
        
        # Google Custom Search API endpoint
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_SEARCH_ENGINE_ID,
            "q": search_query,
            "num": 5  # Get top 5 results
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            items = data.get("items", [])
            
            # Format results to match our structure
            results = []
            for idx, item in enumerate(items):
                results.append({
                    "code": f"WEB-{idx+1}",
                    "term": item.get("title", ""),
                    "definition": item.get("snippet", ""),
                    "source": "google_search",
                    "link": item.get("link", "")
                })
            
            return results
            
    except Exception as e:
        print(f"Google Search fallback error: {e}")
        return []


# -------------------------------------------------------------
# API ROUTES WITH FUZZY MATCHING & GOOGLE FALLBACK
# -------------------------------------------------------------
@router.get("/siddha/autocomplete")
async def siddha_autocomplete(q: str):
    search_result = autocomplete_search(q, siddha)
    matches = search_result["results"]
    fuzzy_suggestions = search_result["fuzzy_suggestions"]
    has_fuzzy = search_result["has_fuzzy"]
    
    # If fuzzy matches found, return them with suggestion message
    if has_fuzzy:
        return {
            "query": q,
            "results": matches,
            "fuzzy_suggestions": fuzzy_suggestions,
            "source": "fuzzy_match",
            "message": f"Did you mean '{fuzzy_suggestions[0]['item']['term']}'?"
        }
    
    # If no local results at all, try Google Search fallback
    if len(matches) == 0:
        google_results = await google_search_fallback(q, "siddha")
        if google_results:
            return {
                "query": q,
                "results": google_results,
                "source": "google_fallback",
                "message": "No local results found. Showing web search results."
            }
    
    return {"query": q, "results": matches, "source": "local"}

@router.get("/ayurveda/autocomplete")
async def ayurveda_autocomplete(q: str):
    search_result = autocomplete_search(q, ayurveda)
    matches = search_result["results"]
    fuzzy_suggestions = search_result["fuzzy_suggestions"]
    has_fuzzy = search_result["has_fuzzy"]
    
    # If fuzzy matches found, return them with suggestion message
    if has_fuzzy:
        return {
            "query": q,
            "results": matches,
            "fuzzy_suggestions": fuzzy_suggestions,
            "source": "fuzzy_match",
            "message": f"Did you mean '{fuzzy_suggestions[0]['item']['term']}'?"
        }
    
    # If no local results at all, try Google Search fallback
    if len(matches) == 0:
        google_results = await google_search_fallback(q, "ayurveda")
        if google_results:
            return {
                "query": q,
                "results": google_results,
                "source": "google_fallback",
                "message": "No local results found. Showing web search results."
            }
    
    return {"query": q, "results": matches, "source": "local"}

@router.get("/unani/autocomplete")
async def unani_autocomplete(q: str):
    search_result = autocomplete_search(q, unani)
    matches = search_result["results"]
    fuzzy_suggestions = search_result["fuzzy_suggestions"]
    has_fuzzy = search_result["has_fuzzy"]
    
    # If fuzzy matches found, return them with suggestion message
    if has_fuzzy:
        return {
            "query": q,
            "results": matches,
            "fuzzy_suggestions": fuzzy_suggestions,
            "source": "fuzzy_match",
            "message": f"Did you mean '{fuzzy_suggestions[0]['item']['term']}'?"
        }
    
    # If no local results at all, try Google Search fallback
    if len(matches) == 0:
        google_results = await google_search_fallback(q, "unani")
        if google_results:
            return {
                "query": q,
                "results": google_results,
                "source": "google_fallback",
                "message": "No local results found. Showing web search results."
            }
    
    return {"query": q, "results": matches, "source": "local"}

@router.get("/ayurveda-sat/autocomplete")
async def ayurveda_sat_autocomplete(q: str):
    search_result = autocomplete_search(q, ayurveda_sat)
    matches = search_result["results"]
    fuzzy_suggestions = search_result["fuzzy_suggestions"]
    has_fuzzy = search_result["has_fuzzy"]
    
    # If fuzzy matches found, return them with suggestion message
    if has_fuzzy:
        return {
            "query": q,
            "results": matches,
            "fuzzy_suggestions": fuzzy_suggestions,
            "source": "fuzzy_match",
            "message": f"Did you mean '{fuzzy_suggestions[0]['item']['term']}'?"
        }
    
    # If no local results at all, try Google Search fallback
    if len(matches) == 0:
        google_results = await google_search_fallback(q, "ayurveda-sat")
        if google_results:
            return {
                "query": q,
                "results": google_results,
                "source": "google_fallback",
                "message": "No local results found. Showing web search results."
            }
    
    return {"query": q, "results": matches, "source": "local"}
