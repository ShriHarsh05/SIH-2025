# -------------------------------------------------------------
# mapper.py  (Siddha → ICD Mapping Brain, FINAL PRODUCTION VERSION)
# -------------------------------------------------------------
import json
import re
import sys
from pathlib import Path
from groq import Groq

# -------------------------------------------------------------
# FIX IMPORT PATHS (based on your folder structure)
# -------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from search import search_siddha
from search_ayurveda import search_ayurveda
from search_unani import search_unani
from search_icd import search_icd
from search_icd_tm2 import search_icd as search_icd_tm2
from search_icd11_standard import search_icd11_standard

from dotenv import load_dotenv
import os
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# -------------------------------------------------------------
# Safe JSON extraction
# -------------------------------------------------------------
def safe_json_extract(text):
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except:
        return None


# -------------------------------------------------------------
# LLM picks BEST 3 ICD codes
# -------------------------------------------------------------
def llm_pick_best(siddha_code, siddha_term, siddha_reason, icd_list):

    icd_text = "\n".join([
        f"{i+1}. {x['code']} — {x['title']}"
        for i, x in enumerate(icd_list)
    ])

    prompt = f"""
    Siddha diagnosis:
    Code: {siddha_code}
    Term: {siddha_term}
    Reasoning: {siddha_reason}

    ICD-11 Candidates:
    {icd_text}

    TASK:
    Pick the BEST 3 matching ICD-11 codes.

    RULES:
    - Output ONLY JSON.
    - No extra text.
    - Format:
    {{
        "matches": [
            {{"code": "...", "reason": "..."}},
            {{"code": "...", "reason": "..."}},
            {{"code": "...", "reason": "..."}}
        ]
    }}
    """

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1
        )

        raw = res.choices[0].message.content
        parsed = safe_json_extract(raw)

        if parsed:
            return parsed

        raise ValueError("JSON error")

    except Exception as e:
        print("LLM mapping error:", e)

        # fallback — return top 3
        return {
            "matches": [
                {"code": x["code"], "reason": "fallback"}
                for x in icd_list[:3]
            ]
        }


# -------------------------------------------------------------
# FULL PIPELINE - Supports multiple traditional medicine systems
# -------------------------------------------------------------
def map_to_icd(user_input: str, system: str = "siddha"):

    # STEP 1 — Traditional medicine search based on system
    if system == "ayurveda":
        tm_out = search_ayurveda(user_input)
    elif system == "unani":
        tm_out = search_unani(user_input)
    else:  # default to siddha
        tm_out = search_siddha(user_input)
    
    tm_candidates = tm_out["candidates"]    # top candidates

    tm_term = tm_candidates[0]["term"]
    tm_reason = tm_out.get("reason", "")

    # STEP 2 — Build search blob for ICD
    search_blob = f"{user_input} {tm_term} {tm_reason}"

    # STEP 3 — ICD retrieval (BM25 → TF-IDF → Semantic)
    icd11_standard_raw = search_icd11_standard(search_blob)
    icd11_tm2_raw = search_icd_tm2(search_blob)

    return {
        "input": user_input,
        "system": system,
        f"{system}_candidates": tm_candidates,
        "icd11_standard_candidates": icd11_standard_raw["candidates"][:10],
        "icd11_tm2_candidates": icd11_tm2_raw[:10]
    }


# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------
if __name__ == "__main__":
    q = "knee swelling and pain"
    out = map_to_icd(q)

    print("\n===== FINAL ICD MAPPING =====")
    print(json.dumps(out["icd_final"], indent=2))

    print("\n===== TOP SIDDHA CANDIDATES =====")
    for s in out["siddha_candidates"]:
        print(s)

    print("\n===== TOP ICD CANDIDATES =====")
    for c in out["icd_candidates"]:
        print(c)