# -------------------------------------------------------------
# server.py  (FastAPI Backend for Siddha → ICD Mapping System)
# -------------------------------------------------------------

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from .autocomplete import router as autocomplete_router
from .auth_simple import router as auth_router, get_optional_user, User
import os
from emr_integration_hapi import BahmniIntegration

# Import your logic
from search import search_siddha
from search_ayurveda import search_ayurveda
from search_unani import search_unani
from build_indexes.mapper import map_to_icd
from fhir_generator import generate_fhir_from_mapping, generate_fhir_bundle_from_mappings
from icd11_fhir_pipeline import ICD11FHIRPipeline
# from emr_integration import BahmniIntegration
import urllib3

# Disable SSL warnings for local Bahmni
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ICD-11 FHIR Pipeline configuration (lazy initialization)
CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='
icd11_pipeline = None  # Will be initialized on first use

def get_icd11_pipeline():
    """Get or initialize ICD-11 pipeline (lazy loading)"""
    global icd11_pipeline
    if icd11_pipeline is None:
        try:
            icd11_pipeline = ICD11FHIRPipeline(CLIENT_ID, CLIENT_SECRET)
        except Exception as e:
            print(f"Warning: Could not initialize ICD-11 pipeline: {e}")
            icd11_pipeline = False  # Mark as failed to avoid retrying
    return icd11_pipeline if icd11_pipeline is not False else None

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
    encounter_id: Optional[str] = None
    practitioner_id: Optional[str] = None

class EMRSendInput(BaseModel):
    fhir_condition: dict
    emr_url: str = "http://localhost"
    username: str = "superman"
    password: str = "Admin123"

class ICD11CodeInput(BaseModel):
    code: str


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
    else:  # default to siddha
        result = search_siddha(body.query)
        candidates_key = "siddha_candidates"
    
    return {candidates_key: result["candidates"]}


@app.post("/map/siddha-code")
def map_specific_siddha_to_icd(body: MapSiddhaCodeInput):
    """Map a specific Siddha code to ICD-11 Standard and ICD-11 TM2."""
    query = f"{body.code} {body.term}"
    result = map_to_icd(query, system="siddha")
    return result

@app.post("/map/ayurveda-code")
def map_specific_ayurveda_to_icd(body: MapSiddhaCodeInput):
    """Map a specific Ayurveda code to ICD-11 Standard and ICD-11 TM2."""
    query = f"{body.code} {body.term}"
    result = map_to_icd(query, system="ayurveda")
    return result

@app.post("/map/unani-code")
def map_specific_unani_to_icd(body: MapSiddhaCodeInput):
    """Map a specific Unani code to ICD-11 Standard and ICD-11 TM2."""
    query = f"{body.code} {body.term}"
    result = map_to_icd(query, system="unani")
    return result

app.include_router(autocomplete_router)
app.include_router(auth_router)

# Mount static files for UI
ui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
if os.path.exists(ui_path):
    app.mount("/ui", StaticFiles(directory=ui_path, html=True), name="ui")

# -------------------------------------------------------------
# ROUTE 4 — FHIR Generation
# -------------------------------------------------------------
@app.post("/fhir/condition")
def generate_fhir_condition(body: FHIRGenerationInput):
    """
    Generate FHIR Condition resource from mapping result.
    Compatible with Bahmni EMR.
    """
    try:
        fhir_condition = generate_fhir_from_mapping(
            mapping_result=body.mapping_result,
            patient_id=body.patient_id,
            encounter_id=body.encounter_id,
            practitioner_id=body.practitioner_id
        )
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
# ROUTE 5 — Send to EMR (Bahmni)
# -------------------------------------------------------------
@app.post("/emr/send")
def send_to_emr(body: EMRSendInput):
    """
    Send FHIR Condition resource to Bahmni EMR.
    """
    try:
        # Connect to Bahmni
        bahmni = BahmniIntegration(
            base_url=body.emr_url,
            username=body.username,
            password=body.password
        )
        
        # Send FHIR Condition
        result = bahmni.send_fhir_condition(body.fhir_condition)
        
        if "error" in result:
            return {
                "success": False,
                "error": result.get("error"),
                "status_code": result.get("status_code")
            }
        
        return {
            "success": True,
            "message": "Successfully sent to Bahmni EMR",
            "resource_id": result.get("id"),
            "resource": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# -------------------------------------------------------------
# ROUTE 6 — ICD-11 Code to FHIR CodeSystem Pipeline
# -------------------------------------------------------------
@app.post("/icd11/to-fhir")
def icd11_code_to_fhir(body: ICD11CodeInput):
    """
    Convert ICD-11 code to FHIR CodeSystem JSON with Entity ID.
    
    Input: ICD-11 code (e.g., "1A00")
    Output: FHIR CodeSystem with code, display, and Entity ID extension
    
    Example:
        POST /icd11/to-fhir
        {"code": "1A00"}
        
        Returns:
        {
            "resourceType": "CodeSystem",
            "status": "active",
            "content": "complete",
            "concept": [{
                "code": "1A00",
                "display": "Cholera",
                "extension": [{
                    "url": "http://id.who.int/icd/entity",
                    "valueString": "257068234"
                }]
            }]
        }
    """
    pipeline = get_icd11_pipeline()
    if not pipeline:
        return {
            "error": "ICD-11 pipeline not available",
            "code": body.code,
            "message": "Could not initialize WHO ICD-11 API connection"
        }
    
    try:
        result = pipeline.process_code(body.code)
        return result
    except ValueError as e:
        return {
            "error": str(e),
            "code": body.code,
            "message": "ICD-11 code not found or invalid"
        }
    except Exception as e:
        return {
            "error": str(e),
            "code": body.code,
            "message": "Error processing ICD-11 code"
        }

@app.get("/icd11/to-fhir/{code}")
def icd11_code_to_fhir_get(code: str):
    """
    Convert ICD-11 code to FHIR CodeSystem JSON with Entity ID (GET method).
    
    Example: GET /icd11/to-fhir/1A00
    """
    pipeline = get_icd11_pipeline()
    if not pipeline:
        return {
            "error": "ICD-11 pipeline not available",
            "code": code,
            "message": "Could not initialize WHO ICD-11 API connection"
        }
    
    try:
        result = pipeline.process_code(code)
        return result
    except ValueError as e:
        return {
            "error": str(e),
            "code": code,
            "message": "ICD-11 code not found or invalid"
        }
    except Exception as e:
        return {
            "error": str(e),
            "code": code,
            "message": "Error processing ICD-11 code"
        }

# -------------------------------------------------------------
# Health Check
# -------------------------------------------------------------
@app.get("/")
def home():
    return {
        "status": "ok", 
        "message": "Traditional Medicine → ICD Mapping API running",
        "supported_systems": ["siddha", "ayurveda", "unani"],
        "fhir_support": "FHIR R4 Condition resources for Bahmni EMR",
        "emr_integration": "Bahmni EMR (OpenMRS + FHIR R4)",
        "icd11_pipeline": "ICD-11 code to FHIR CodeSystem with Entity ID"
    }



# -------------------------------------------------------------
# Run with:  uvicorn api.server:app --reload
# -------------------------------------------------------------
