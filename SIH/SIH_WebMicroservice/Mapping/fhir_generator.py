"""
FHIR JSON Generator for Bahmni EMR
Generates FHIR-compliant Condition resources with Traditional Medicine and ICD-11 mappings
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import uuid

# Import ICD-11 pipeline for Entity ID lookup
try:
    from icd11_fhir_pipeline import ICD11FHIRPipeline
    ICD11_AVAILABLE = True
except ImportError:
    ICD11_AVAILABLE = False


class FHIRConditionGenerator:
    """Generate FHIR Condition resources for Bahmni EMR"""
    
    def __init__(self):
        self.fhir_version = "4.0.1"
        # Initialize ICD-11 pipeline for Entity ID lookup
        if ICD11_AVAILABLE:
            try:
                CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
                CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='
                self.icd11_pipeline = ICD11FHIRPipeline(CLIENT_ID, CLIENT_SECRET)
            except:
                self.icd11_pipeline = None
        else:
            self.icd11_pipeline = None
        
    def generate_condition(
        self,
        patient_id: str,
        tm_system: str,
        tm_code: str,
        tm_term: str,
        tm_english: Optional[str] = None,
        tm_definition: Optional[str] = None,
        icd11_standard: Optional[Dict] = None,
        icd11_tm2: Optional[Dict] = None,
        encounter_id: Optional[str] = None,
        practitioner_id: Optional[str] = None,
        clinical_status: str = "active",
        verification_status: str = "confirmed",
        doctor_input: Optional[str] = None
    ) -> Dict:
        """
        Generate a FHIR Condition resource
        
        Args:
            patient_id: Patient identifier
            tm_system: Traditional medicine system (siddha/ayurveda/unani)
            tm_code: TM2 code
            tm_term: Original term
            tm_english: English translation
            tm_definition: Definition
            icd11_standard: ICD-11 Standard mapping {code, title, definition, score}
            icd11_tm2: ICD-11 TM2 mapping {code, title, definition, score}
            encounter_id: Encounter reference
            practitioner_id: Practitioner who recorded
            clinical_status: active|recurrence|relapse|inactive|remission|resolved
            verification_status: unconfirmed|provisional|differential|confirmed|refuted|entered-in-error
        """
        
        condition_id = str(uuid.uuid4())
        recorded_date = datetime.utcnow().isoformat() + "Z"
        
        # Build the FHIR Condition resource
        condition = {
            "resourceType": "Condition",
            "id": condition_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": recorded_date,
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/Condition"
                ]
            },
            "text": {
                "status": "generated",
                "div": self._generate_narrative(
                    tm_system, tm_code, tm_term, tm_english, 
                    icd11_standard, icd11_tm2
                )
            },
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": clinical_status,
                    "display": clinical_status.capitalize()
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": verification_status,
                    "display": verification_status.capitalize()
                }]
            },
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                    "code": "encounter-diagnosis",
                    "display": "Encounter Diagnosis"
                }]
            }],
            "code": self._build_code_element(
                tm_system, tm_code, tm_term, tm_english, tm_definition,
                icd11_standard, icd11_tm2, doctor_input
            ),
            "subject": {
                "reference": f"Patient/{patient_id}",
                "display": "Patient"
            },
            "recordedDate": recorded_date
        }
        
        # Add encounter reference if provided
        if encounter_id:
            condition["encounter"] = {
                "reference": f"Encounter/{encounter_id}"
            }
        
        # Add recorder (practitioner) if provided
        if practitioner_id:
            condition["recorder"] = {
                "reference": f"Practitioner/{practitioner_id}",
                "display": "Practitioner"
            }
        
        # Add evidence with confidence scores
        if icd11_standard or icd11_tm2:
            condition["evidence"] = self._build_evidence(icd11_standard, icd11_tm2)
        
        # Add notes with definitions
        notes = []
        if tm_definition and tm_definition != "No description available.":
            notes.append({
                "text": f"Traditional Medicine Definition: {tm_definition}"
            })
        if icd11_standard and icd11_standard.get("definition"):
            notes.append({
                "text": f"ICD-11 Standard Definition: {icd11_standard['definition']}"
            })
        if icd11_tm2 and icd11_tm2.get("definition"):
            notes.append({
                "text": f"ICD-11 TM2 Definition: {icd11_tm2['definition']}"
            })
        
        if notes:
            condition["note"] = notes
        
        return condition
    
    def _build_code_element(
        self,
        tm_system: str,
        tm_code: str,
        tm_term: str,
        tm_english: Optional[str],
        tm_definition: Optional[str],
        icd11_standard: Optional[Dict],
        icd11_tm2: Optional[Dict],
        doctor_input: Optional[str] = None
    ) -> Dict:
        """Build the code element with multiple codings"""
        
        codings = []
        
        # Traditional Medicine coding
        tm_system_url = {
            "siddha": "http://who.int/icd/tm2/siddha",
            "ayurveda": "http://who.int/icd/tm2/ayurveda",
            "unani": "http://who.int/icd/tm2/unani"
        }
        
        # Use term as code if code is missing
        effective_code = tm_code if tm_code else (tm_term[:50] if tm_term else "TM-UNKNOWN")
        effective_display = tm_english or tm_term or "Traditional Medicine Term"
        
        tm_coding = {
            "system": tm_system_url.get(tm_system, "http://who.int/icd/tm2"),
            "code": effective_code,
            "display": effective_display
        }
        
        # Add original term as extension if different
        if tm_english and tm_term and tm_term != tm_english:
            tm_coding["extension"] = [{
                "url": "http://hl7.org/fhir/StructureDefinition/originalText",
                "valueString": tm_term
            }]
        
        codings.append(tm_coding)
        
        # ICD-11 Standard coding with Entity ID
        if icd11_standard:
            icd_extensions = [{
                "url": "http://hl7.org/fhir/StructureDefinition/data-absent-reason",
                "valueCode": "mapped"
            }, {
                "url": "http://example.org/fhir/StructureDefinition/mapping-confidence",
                "valueDecimal": round(icd11_standard.get("score", 0), 4)
            }]
            
            # Try to fetch Entity ID from WHO API
            if self.icd11_pipeline:
                try:
                    icd_code = icd11_standard["code"]
                    entity_data = self.icd11_pipeline.search_icd11_code(icd_code)
                    if entity_data and entity_data.get('entity_id'):
                        icd_extensions.append({
                            "url": "http://id.who.int/icd/entity",
                            "valueString": entity_data['entity_id']
                        })
                except Exception as e:
                    # Silently continue without Entity ID if lookup fails
                    pass
            
            codings.append({
                "system": "http://id.who.int/icd/release/11/mms",
                "code": icd11_standard["code"],
                "display": icd11_standard["title"],
                "extension": icd_extensions
            })
        
        # ICD-11 TM2 coding with Entity ID
        if icd11_tm2:
            tm2_extensions = [{
                "url": "http://hl7.org/fhir/StructureDefinition/data-absent-reason",
                "valueCode": "mapped"
            }, {
                "url": "http://example.org/fhir/StructureDefinition/mapping-confidence",
                "valueDecimal": round(icd11_tm2.get("score", 0), 4)
            }]
            
            # Try to fetch Entity ID from WHO API
            if self.icd11_pipeline:
                try:
                    tm2_code = icd11_tm2["code"]
                    entity_data = self.icd11_pipeline.search_icd11_code(tm2_code)
                    if entity_data and entity_data.get('entity_id'):
                        tm2_extensions.append({
                            "url": "http://id.who.int/icd/entity",
                            "valueString": entity_data['entity_id']
                        })
                except Exception as e:
                    # Silently continue without Entity ID if lookup fails
                    pass
            
            codings.append({
                "system": "http://id.who.int/icd/release/11/tm2",
                "code": icd11_tm2["code"],
                "display": icd11_tm2["title"],
                "extension": tm2_extensions
            })
        
        # Build descriptive text
        text_parts = []
        if doctor_input:
            text_parts.append(f"Symptoms: {doctor_input}")
        if tm_english or tm_term:
            text_parts.append(f"Diagnosis: {tm_english or tm_term}")
        if icd11_standard:
            text_parts.append(f"ICD-11: {icd11_standard['code']} - {icd11_standard['title']}")
        
        condition_text = " | ".join(text_parts) if text_parts else (tm_english or tm_term)
        
        return {
            "coding": codings,
            "text": condition_text
        }
    
    def _build_evidence(
        self,
        icd11_standard: Optional[Dict],
        icd11_tm2: Optional[Dict]
    ) -> List[Dict]:
        """Build evidence array with confidence scores"""
        
        evidence = []
        
        if icd11_standard:
            evidence.append({
                "code": [{
                    "coding": [{
                        "system": "http://id.who.int/icd/release/11/mms",
                        "code": icd11_standard["code"],
                        "display": icd11_standard["title"]
                    }],
                    "text": f"ICD-11 Standard mapping (confidence: {icd11_standard.get('score', 0):.4f})"
                }]
            })
        
        if icd11_tm2:
            evidence.append({
                "code": [{
                    "coding": [{
                        "system": "http://id.who.int/icd/release/11/tm2",
                        "code": icd11_tm2["code"],
                        "display": icd11_tm2["title"]
                    }],
                    "text": f"ICD-11 TM2 mapping (confidence: {icd11_tm2.get('score', 0):.4f})"
                }]
            })
        
        return evidence
    
    def _generate_narrative(
        self,
        tm_system: str,
        tm_code: str,
        tm_term: str,
        tm_english: Optional[str],
        icd11_standard: Optional[Dict],
        icd11_tm2: Optional[Dict]
    ) -> str:
        """Generate human-readable narrative"""
        
        system_name = tm_system.capitalize()
        display_term = tm_english or tm_term
        
        narrative = f'<div xmlns="http://www.w3.org/1999/xhtml">'
        narrative += f'<p><b>{system_name} Diagnosis:</b> {tm_code} - {display_term}</p>'
        
        if tm_english and tm_term != tm_english:
            narrative += f'<p><i>Original term:</i> {tm_term}</p>'
        
        if icd11_standard:
            narrative += f'<p><b>ICD-11 Standard:</b> {icd11_standard["code"]} - {icd11_standard["title"]}</p>'
        
        if icd11_tm2:
            narrative += f'<p><b>ICD-11 TM2:</b> {icd11_tm2["code"]} - {icd11_tm2["title"]}</p>'
        
        narrative += '</div>'
        
        return narrative
    
    def generate_bundle(
        self,
        conditions: List[Dict],
        bundle_type: str = "collection"
    ) -> Dict:
        """Generate a FHIR Bundle containing multiple Condition resources"""
        
        bundle_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        entries = []
        for condition in conditions:
            entries.append({
                "fullUrl": f"urn:uuid:{condition['id']}",
                "resource": condition
            })
        
        bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": {
                "lastUpdated": timestamp
            },
            "type": bundle_type,
            "timestamp": timestamp,
            "total": len(conditions),
            "entry": entries
        }
        
        return bundle


def generate_fhir_from_mapping(
    mapping_result: Dict,
    patient_id: str = "example-patient-123",
    encounter_id: Optional[str] = None,
    practitioner_id: Optional[str] = None
) -> Dict:
    """
    Generate FHIR Condition from mapping result
    
    Args:
        mapping_result: Result from mapper.map_to_icd()
        patient_id: Patient identifier
        encounter_id: Encounter identifier
        practitioner_id: Practitioner identifier
    
    Returns:
        FHIR Condition resource
    """
    
    generator = FHIRConditionGenerator()
    
    # Extract system and candidates
    system = mapping_result.get("system", "siddha")
    candidates_key = f"{system}_candidates"
    tm_candidates = mapping_result.get(candidates_key, [])
    
    if not tm_candidates:
        raise ValueError("No traditional medicine candidates found in mapping result")
    
    # Use the top candidate
    tm_candidate = tm_candidates[0]
    
    # Get ICD mappings (use top candidates)
    icd11_standard_list = mapping_result.get("icd11_standard_candidates", [])
    icd11_tm2_list = mapping_result.get("icd11_tm2_candidates", [])
    
    icd11_standard = icd11_standard_list[0] if icd11_standard_list else None
    icd11_tm2 = icd11_tm2_list[0] if icd11_tm2_list else None
    
    # Get doctor's input (symptoms/description)
    doctor_input = mapping_result.get("input", "")
    
    # Generate FHIR Condition
    condition = generator.generate_condition(
        patient_id=patient_id,
        tm_system=system,
        tm_code=tm_candidate.get("code"),
        tm_term=tm_candidate.get("term", ""),
        tm_english=tm_candidate.get("english"),
        tm_definition=tm_candidate.get("definition"),
        icd11_standard=icd11_standard,
        icd11_tm2=icd11_tm2,
        encounter_id=encounter_id,
        practitioner_id=practitioner_id,
        doctor_input=doctor_input
    )
    
    return condition


def generate_fhir_bundle_from_mappings(
    mapping_results: List[Dict],
    patient_id: str = "example-patient-123",
    encounter_id: Optional[str] = None,
    practitioner_id: Optional[str] = None
) -> Dict:
    """
    Generate FHIR Bundle from multiple mapping results
    
    Args:
        mapping_results: List of results from mapper.map_to_icd()
        patient_id: Patient identifier
        encounter_id: Encounter identifier
        practitioner_id: Practitioner identifier
    
    Returns:
        FHIR Bundle resource
    """
    
    generator = FHIRConditionGenerator()
    conditions = []
    
    for mapping_result in mapping_results:
        try:
            condition = generate_fhir_from_mapping(
                mapping_result,
                patient_id,
                encounter_id,
                practitioner_id
            )
            conditions.append(condition)
        except Exception as e:
            print(f"Error generating FHIR for mapping: {e}")
            continue
    
    bundle = generator.generate_bundle(conditions)
    return bundle


# Example usage
if __name__ == "__main__":
    # Example mapping result
    example_mapping = {
        "input": "joint pain and swelling",
        "system": "ayurveda",
        "ayurveda_candidates": [{
            "code": "SP42",
            "term": "pRuShTha-grahaH",
            "english": "Lumbar spondylosis disorder",
            "definition": "It is characterised by backache of various degrees associated with stiffness and immobility.",
            "score": 0.8542
        }],
        "icd11_standard_candidates": [{
            "code": "FA20.0",
            "title": "Low back pain",
            "definition": "Pain localized to the lower back region.",
            "score": 0.7823
        }],
        "icd11_tm2_candidates": [{
            "code": "SP42",
            "title": "Lumbar spondylosis disorder (TM2)",
            "definition": "It is characterised by backache of various degrees.",
            "score": 0.8123
        }]
    }
    
    # Generate FHIR Condition
    fhir_condition = generate_fhir_from_mapping(
        example_mapping,
        patient_id="patient-123",
        encounter_id="encounter-456",
        practitioner_id="practitioner-789"
    )
    
    print(json.dumps(fhir_condition, indent=2))
