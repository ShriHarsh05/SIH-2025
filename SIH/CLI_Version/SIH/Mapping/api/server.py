# -------------------------------------------------------------
# server.py  (FastAPI Backend for Siddha → ICD Mapping System)
# -------------------------------------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .autocomplete import router as autocomplete_router

# Import your logic
from search import search_siddha
from search_ayurveda import search_ayurveda
from search_unani import search_unani
from search_ayurveda_sat import search_ayurveda_sat
from build_indexes.mapper import map_to_icd
from fhir_generator import generate_fhir_from_mapping, generate_fhir_bundle_from_mappings
from database import log_mapping_session
from reranking import rerank_results

app = FastAPI(
    title="Traditional Medicine → ICD Mapping API",
    description="Hybrid Retrieval + LLM mapping engine for Siddha, Ayurveda, and Unani",
    version="2.0.0"
)

# -------------------------------------------------------------
# CORS (for your frontend)
# -------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------

class SiddhaSearchInput(BaseModel):
    query: str

class DiagnoseInput(BaseModel):
    symptoms: str

class MapInput(BaseModel):
    query: str
    system: str = "siddha"

class MapSiddhaCodeInput(BaseModel):
    code: str
    term: str

class FHIRGenerationInput(BaseModel):
    mapping_result: dict
    patient_id: str = "example-patient-123"
    encounter_id: str = None
    practitioner_id: str = None


# -------------------------------------------------------------
# ROUTE 1 — Siddha Search (Autocomplete)
# -------------------------------------------------------------
@app.post("/siddha/search")
def siddha_search(body: SiddhaSearchInput):
    """
    Autocomplete for Siddha term or code.
    Used for dropdown in the UI.
    """
    result = search_siddha(body.query)
    return {
        "query": body.query,
        "candidates": result["candidates"]
    }


# -------------------------------------------------------------
# ROUTE 2 — Diagnose (Symptoms → Best Code) - All Systems
# -------------------------------------------------------------
@app.post("/siddha/diagnose")
def siddha_diagnose(body: DiagnoseInput):
    """User enters symptoms → AI chooses best Siddha diagnosis."""
    result = search_siddha(body.symptoms)
    return {
        "input": body.symptoms,
        "candidates": result["candidates"]
    }

@app.post("/ayurveda/diagnose")
def ayurveda_diagnose(body: DiagnoseInput):
    """User enters symptoms → AI chooses best Ayurveda diagnosis."""
    result = search_ayurveda(body.symptoms)
    return {
        "input": body.symptoms,
        "candidates": result["candidates"]
    }

@app.post("/unani/diagnose")
def unani_diagnose(body: DiagnoseInput):
    """User enters symptoms → AI chooses best Unani diagnosis."""
    result = search_unani(body.symptoms)
    return {
        "input": body.symptoms,
        "candidates": result["candidates"]
    }

@app.post("/ayurveda-sat/diagnose")
def ayurveda_sat_diagnose(body: DiagnoseInput):
    """User enters symptoms → AI chooses best Ayurveda-SAT diagnosis."""
    result = search_ayurveda_sat(body.symptoms)
    return {
        "input": body.symptoms,
        "candidates": result["candidates"]
    }


# -------------------------------------------------------------
# ROUTE 3 — Final Mapping (Traditional Medicine → ICD)
# -------------------------------------------------------------
@app.post("/map")
def map_to_icd_system(body: MapInput):
    """
    Full Traditional Medicine → ICD mapping pipeline.
    Supports Siddha, Ayurveda, and Unani systems.
    """
    # Get candidates from the selected system
    if body.system == "ayurveda":
        result = search_ayurveda(body.query)
        candidates_key = "ayurveda_candidates"
    elif body.system == "unani":
        result = search_unani(body.query)
        candidates_key = "unani_candidates"
    elif body.system == "ayurveda-sat":
        result = search_ayurveda_sat(body.query)
        candidates_key = "ayurveda_sat_candidates"
    else:  # default to siddha
        result = search_siddha(body.query)
        candidates_key = "siddha_candidates"
    
    return {candidates_key: result["candidates"]}


@app.post("/map/siddha-code")
def map_specific_siddha_to_icd(body: MapSiddhaCodeInput):
    """Map a specific Siddha code to ICD-11 Standard and ICD-11 TM2."""
    query = f"{body.code} {body.term}"
    result = map_to_icd(query, system="siddha")
    # Apply re-ranking based on database selection history
    result = rerank_results(result, "siddha", query)
    return result

@app.post("/map/ayurveda-code")
def map_specific_ayurveda_to_icd(body: MapSiddhaCodeInput):
    """Map a specific Ayurveda code to ICD-11 Standard and ICD-11 TM2."""
    query = f"{body.code} {body.term}"
    result = map_to_icd(query, system="ayurveda")
    # Apply re-ranking based on database selection history
    result = rerank_results(result, "ayurveda", query)
    return result

@app.post("/map/unani-code")
def map_specific_unani_to_icd(body: MapSiddhaCodeInput):
    """Map a specific Unani code to ICD-11 Standard and ICD-11 TM2."""
    query = f"{body.code} {body.term}"
    result = map_to_icd(query, system="unani")
    # Apply re-ranking based on database selection history
    result = rerank_results(result, "unani", query)
    return result

@app.post("/map/ayurveda-sat-code")
def map_specific_ayurveda_sat_to_icd(body: MapSiddhaCodeInput):
    """Map a specific Ayurveda-SAT code to ICD-11 Standard and ICD-11 TM2."""
    query = f"{body.code} {body.term}"
    result = map_to_icd(query, system="ayurveda-sat")
    # Apply re-ranking based on database selection history
    result = rerank_results(result, "ayurveda-sat", query)
    return result

app.include_router(autocomplete_router)

# -------------------------------------------------------------
# ROUTE 4 — FHIR Generation
# -------------------------------------------------------------
@app.post("/fhir/condition")
def generate_fhir_condition(body: FHIRGenerationInput):
    """
    Generate FHIR Condition resource from mapping result.
    Compatible with Bahmni EMR.
    Logs the session to database.
    """
    try:
        fhir_condition = generate_fhir_from_mapping(
            mapping_result=body.mapping_result,
            patient_id=body.patient_id,
            encounter_id=body.encounter_id,
            practitioner_id=body.practitioner_id
        )
        
        # Log to database
        try:
            # Extract data from mapping_result
            system = body.mapping_result.get("system", "unknown")
            query = body.mapping_result.get("input", "")
            
            # Normalize system key for candidates
            system_key = system.replace("-", "_")
            tm_candidates = body.mapping_result.get(f"{system_key}_candidates", [])
            icd11_standard_candidates = body.mapping_result.get("icd11_standard_candidates", [])
            icd11_tm2_candidates = body.mapping_result.get("icd11_tm2_candidates", [])
            
            # Get selected candidates (first in each list)
            selected_tm = tm_candidates[0] if tm_candidates else None
            selected_icd11_standard = icd11_standard_candidates[0] if icd11_standard_candidates else None
            selected_icd11_tm2 = icd11_tm2_candidates[0] if icd11_tm2_candidates else None
            
            # Log to database
            if selected_tm:
                record_id = log_mapping_session(
                    practitioner_id=body.practitioner_id,
                    encounter_id=body.encounter_id,
                    patient_id=body.patient_id,
                    selected_system=system,
                    query=query,
                    tm_candidates=tm_candidates[:10],
                    icd11_standard_candidates=icd11_standard_candidates[:10],
                    icd11_tm2_candidates=icd11_tm2_candidates[:10],
                    selected_tm_candidate=selected_tm,
                    selected_icd11_standard=selected_icd11_standard,
                    selected_icd11_tm2=selected_icd11_tm2,
                    fhir_json=fhir_condition
                )
                print(f"✓ Session logged to database (Record ID: {record_id})")
        except Exception as db_error:
            print(f"⚠ Database logging failed: {str(db_error)}")
            # Don't fail the request if database logging fails
        
        return fhir_condition
    except Exception as e:
        return {"error": str(e)}

@app.post("/fhir/bundle")
def generate_fhir_bundle(
    mapping_results: list,
    patient_id: str = "example-patient-123",
    encounter_id: str = None,
    practitioner_id: str = None
):
    """
    Generate FHIR Bundle from multiple mapping results.
    Compatible with Bahmni EMR.
    """
    try:
        fhir_bundle = generate_fhir_bundle_from_mappings(
            mapping_results=mapping_results,
            patient_id=patient_id,
            encounter_id=encounter_id,
            practitioner_id=practitioner_id
        )
        return fhir_bundle
    except Exception as e:
        return {"error": str(e)}

# -------------------------------------------------------------
# Health Check
# -------------------------------------------------------------
@app.get("/")
def home():
    return {
        "status": "ok", 
        "message": "Traditional Medicine → ICD Mapping API running",
        "supported_systems": ["siddha", "ayurveda", "unani"],
        "fhir_support": "FHIR R4 Condition resources for Bahmni EMR"
    }



# -------------------------------------------------------------
# Run with:  uvicorn api.server:app --reload
# -------------------------------------------------------------
