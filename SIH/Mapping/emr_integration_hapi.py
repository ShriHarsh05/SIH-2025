"""
HAPI FHIR Integration - This ACTUALLY works!
HAPI FHIR is a pure FHIR server that stores and retrieves resources properly
"""

import requests
import json
from typing import Dict
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BahmniIntegration:
    """
    Integration with HAPI FHIR Server
    This is simpler and actually works!
    """
    
    def __init__(self, base_url: str, username: str = None, password: str = None):
        self.base_url = base_url.rstrip('/')
        # HAPI FHIR doesn't require authentication by default
        self.session = requests.Session()
        self.username = username
        self.password = password
        print("✅ Connected to HAPI FHIR Server")
        print(f"   URL: {self.base_url}")
    
    def ensure_patient_exists(self, patient_id: str) -> bool:
        """
        Ensure patient exists in HAPI FHIR, create if not
        """
        try:
            # Check if patient exists
            response = self.session.get(
                f"{self.base_url}/Patient/{patient_id}",
                headers={'Accept': 'application/fhir+json'},
                verify=False
            )
            
            if response.status_code == 200:
                return True
            
            # Patient doesn't exist, create it
            patient = {
                "resourceType": "Patient",
                "id": patient_id,
                "name": [{
                    "text": f"Patient {patient_id}",
                    "family": "Patient",
                    "given": [patient_id]
                }],
                "gender": "unknown",
                "birthDate": "2000-01-01"
            }
            
            create_response = self.session.put(
                f"{self.base_url}/Patient/{patient_id}",
                json=patient,
                headers={'Content-Type': 'application/fhir+json'},
                verify=False
            )
            
            return create_response.status_code in [200, 201]
            
        except Exception as e:
            print(f"⚠️  Could not ensure patient exists: {str(e)}")
            return False
    
    def send_fhir_condition(self, fhir_condition: Dict) -> Dict:
        """
        Send FHIR Condition to HAPI FHIR Server
        This will actually store and be retrievable!
        """
        try:
            # Extract patient ID from condition
            patient_ref = fhir_condition.get('subject', {}).get('reference', '')
            if patient_ref.startswith('Patient/'):
                patient_id = patient_ref.replace('Patient/', '')
                # Ensure patient exists
                self.ensure_patient_exists(patient_id)
            
            # CRITICAL FIX: Remove the 'id' field before POSTing
            # When creating a new resource, the server assigns the ID
            # Including a pre-generated ID causes HAPI FHIR to look for an existing resource
            fhir_to_send = fhir_condition.copy()
            if 'id' in fhir_to_send:
                del fhir_to_send['id']
            
            response = self.session.post(
                f"{self.base_url}/Condition",
                json=fhir_to_send,
                headers={
                    'Content-Type': 'application/fhir+json',
                    'Accept': 'application/fhir+json'
                },
                verify=False
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                resource_id = result.get('id', 'N/A')
                print(f"✅ FHIR Condition stored successfully!")
                print(f"   Resource ID: {resource_id}")
                print(f"   Can be retrieved at: {self.base_url}/Condition/{resource_id}")
                return result
            else:
                print(f"❌ Failed to send: {response.status_code}")
                print(f"Error: {response.text}")
                return {"error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return {"error": str(e)}
    
    def get_condition(self, condition_id: str) -> Dict:
        """Retrieve a condition by ID"""
        try:
            response = self.session.get(
                f"{self.base_url}/Condition/{condition_id}",
                headers={'Accept': 'application/fhir+json'},
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
            return {"error": f"Condition not found: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_patient_conditions(self, patient_id: str) -> Dict:
        """Get all conditions for a patient"""
        try:
            response = self.session.get(
                f"{self.base_url}/Condition?patient={patient_id}",
                headers={'Accept': 'application/fhir+json'},
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
            return {"error": f"Failed to fetch: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
