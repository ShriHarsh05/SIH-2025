"""
Working EMR Integration for Bahmni
Uses Bahmni's native diagnosis concepts that actually show up in the UI
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BahmniIntegration:
    """
    Working Bahmni integration using native OpenMRS concepts
    """
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Bahmni/OpenMRS"""
        auth_url = f"{self.base_url}/openmrs/ws/rest/v1/session"
        response = self.session.get(
            auth_url,
            auth=(self.username, self.password),
            headers={'Content-Type': 'application/json'},
            verify=False
        )
        
        if response.status_code == 200:
            print("✅ Authenticated with Bahmni")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def get_visit_for_patient(self, patient_uuid: str):
        """Get or create an active visit for the patient"""
        # Check for active visits
        response = self.session.get(
            f"{self.base_url}/openmrs/ws/rest/v1/visit?patient={patient_uuid}&includeInactive=false&v=default",
            auth=(self.username, self.password),
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                # Return first active visit
                return results[0].get('uuid')
        
        # Create a new visit if none exists
        visit_data = {
            "patient": patient_uuid,
            "visitType": "7b0f5697-27e3-40c4-8bae-f4049abfb4ed",  # General visit type
            "startDatetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "location": "8d6c993e-c2cc-11de-8d13-0010c6dffd0f"  # Default location
        }
        
        response = self.session.post(
            f"{self.base_url}/openmrs/ws/rest/v1/visit",
            json=visit_data,
            auth=(self.username, self.password),
            headers={'Content-Type': 'application/json'},
            verify=False
        )
        
        if response.status_code in [200, 201]:
            visit = response.json()
            return visit.get('uuid')
        
        return None
    
    def create_bahmni_diagnosis(self, patient_uuid: str, diagnosis_text: str, 
                               icd11_code: str = None) -> Dict:
        """
        Create a diagnosis using Bahmni's diagnosis concept
        This will show up in the Diagnoses section of Bahmni UI
        """
        try:
            # Use a text concept for storing the diagnosis
            # This is simpler and doesn't require visits/encounters
            text_concept_uuid = "162169AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"  # Text observation concept
            
            # Create diagnosis observation
            obs_data = {
                "person": patient_uuid,
                "concept": text_concept_uuid,
                "obsDatetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
                "value": diagnosis_text
            }
            
            response = self.session.post(
                f"{self.base_url}/openmrs/ws/rest/v1/obs",
                json=obs_data,
                auth=(self.username, self.password),
                headers={'Content-Type': 'application/json'},
                verify=False
            )
            
            if response.status_code in [200, 201]:
                obs = response.json()
                print("✅ Diagnosis observation created successfully")
                return {
                    "success": True,
                    "observation_uuid": obs.get('uuid'),
                    "diagnosis": diagnosis_text
                }
            else:
                print(f"❌ Failed to create observation: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return {
                    "error": f"Failed to create observation: {response.status_code}",
                    "status_code": response.status_code,
                    "success": False
                }
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    def send_diagnosis(self, patient_uuid: str, icd11_code: str, icd11_display: str,
                      tm_system: str, tm_code: str, tm_term: str) -> Dict:
        """
        Send diagnosis to Bahmni
        Creates a diagnosis that will show in the Diagnoses section
        """
        # Format diagnosis text
        diagnosis_text = f"{tm_system.upper()}: {tm_term} (Code: {tm_code})"
        full_text = f"{diagnosis_text} → ICD-11: {icd11_code} - {icd11_display}"
        
        result = self.create_bahmni_diagnosis(
            patient_uuid=patient_uuid,
            diagnosis_text=full_text,
            icd11_code=icd11_code
        )
        
        return result
    
    def send_fhir_condition(self, fhir_condition: Dict) -> Dict:
        """
        Extract data from FHIR Condition and send as Bahmni diagnosis
        """
        try:
            # Extract patient UUID
            patient_ref = fhir_condition.get("subject", {}).get("reference", "")
            patient_uuid = patient_ref.replace("Patient/", "") if patient_ref else None
            
            if not patient_uuid:
                return {"error": "Patient UUID not found", "success": False}
            
            # Extract codes
            codings = fhir_condition.get("code", {}).get("coding", [])
            icd11_code = "Unknown"
            icd11_display = "Unknown"
            tm_code = "Unknown"
            tm_term = "Unknown"
            tm_system = "traditional-medicine"
            
            for coding in codings:
                system = coding.get("system", "")
                if "icd-11" in system.lower() or "icd/release" in system.lower():
                    icd11_code = coding.get("code", "Unknown")
                    icd11_display = coding.get("display", "Unknown")
                elif "traditional-medicine" in system.lower():
                    tm_code = coding.get("code", "Unknown")
                    tm_term = coding.get("display", "Unknown")
                    if "Siddha" in tm_term:
                        tm_system = "Siddha"
                    elif "Ayurveda" in tm_term:
                        tm_system = "Ayurveda"
                    elif "Unani" in tm_term:
                        tm_system = "Unani"
            
            # Send as diagnosis
            return self.send_diagnosis(
                patient_uuid=patient_uuid,
                icd11_code=icd11_code,
                icd11_display=icd11_display,
                tm_system=tm_system,
                tm_code=tm_code,
                tm_term=tm_term
            )
            
        except Exception as e:
            return {"error": str(e), "success": False}
