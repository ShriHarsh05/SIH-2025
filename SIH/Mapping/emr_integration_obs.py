"""
EMR Integration using OpenMRS Observations API
This approach is more stable and works better with Bahmni UI
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BahmniObservationIntegration:
    """
    Integration with Bahmni using OpenMRS Observations API
    More stable than FHIR Conditions for Bahmni
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
    
    def get_or_create_diagnosis_concept(self):
        """
        Get the diagnosis concept UUID
        In OpenMRS, we need a concept to record observations
        """
        # Standard diagnosis concept UUID in OpenMRS
        # This is the "Visit Diagnoses" concept
        return "159947AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    
    def create_encounter(self, patient_uuid: str, encounter_type_uuid: str = None):
        """
        Create an encounter for the patient
        Encounters are required to record observations in OpenMRS
        """
        if not encounter_type_uuid:
            # Default to "Consultation" encounter type
            encounter_type_uuid = "81852aee-3f10-11e4-adec-0800271c1b75"
        
        encounter_data = {
            "patient": patient_uuid,
            "encounterType": encounter_type_uuid,
            "encounterDatetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "location": "8d6c993e-c2cc-11de-8d13-0010c6dffd0f"  # Default location
        }
        
        response = self.session.post(
            f"{self.base_url}/openmrs/ws/rest/v1/encounter",
            json=encounter_data,
            auth=(self.username, self.password),
            headers={'Content-Type': 'application/json'},
            verify=False
        )
        
        if response.status_code in [200, 201]:
            encounter = response.json()
            return encounter.get('uuid')
        else:
            print(f"❌ Failed to create encounter: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    
    def send_diagnosis(self, patient_uuid: str, icd11_code: str, icd11_display: str, 
                      tm_system: str, tm_code: str, tm_term: str) -> Dict:
        """
        Send diagnosis as an observation to Bahmni
        
        Args:
            patient_uuid: Patient UUID
            icd11_code: ICD-11 code
            icd11_display: ICD-11 display name
            tm_system: Traditional medicine system (siddha/ayurveda/unani)
            tm_code: Traditional medicine code
            tm_term: Traditional medicine term
            
        Returns:
            Response from Bahmni
        """
        # Create an encounter first
        encounter_uuid = self.create_encounter(patient_uuid)
        
        if not encounter_uuid:
            return {"error": "Failed to create encounter", "status_code": 500}
        
        # Create observation with diagnosis
        diagnosis_text = f"{tm_system.upper()}: {tm_code} - {tm_term} → ICD-11: {icd11_code} - {icd11_display}"
        
        observation_data = {
            "person": patient_uuid,
            "concept": self.get_or_create_diagnosis_concept(),
            "obsDatetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "value": diagnosis_text,
            "encounter": encounter_uuid,
            "comment": f"Traditional Medicine Mapping: {tm_system} → ICD-11"
        }
        
        response = self.session.post(
            f"{self.base_url}/openmrs/ws/rest/v1/obs",
            json=observation_data,
            auth=(self.username, self.password),
            headers={'Content-Type': 'application/json'},
            verify=False
        )
        
        if response.status_code in [200, 201]:
            obs = response.json()
            print("✅ Diagnosis observation sent successfully")
            return {
                "success": True,
                "observation_uuid": obs.get('uuid'),
                "encounter_uuid": encounter_uuid,
                "diagnosis": diagnosis_text
            }
        else:
            print(f"❌ Failed to send observation: {response.status_code}")
            print(f"Error: {response.text}")
            return {
                "error": response.text,
                "status_code": response.status_code
            }
    
    def get_patient_observations(self, patient_uuid: str) -> Dict:
        """Get all observations for a patient"""
        response = self.session.get(
            f"{self.base_url}/openmrs/ws/rest/v1/obs?patient={patient_uuid}&v=full",
            auth=(self.username, self.password),
            headers={'Accept': 'application/json'},
            verify=False
        )
        
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to fetch observations", "status_code": response.status_code}


# For backward compatibility
class BahmniIntegration(BahmniObservationIntegration):
    """Alias for backward compatibility"""
    pass
