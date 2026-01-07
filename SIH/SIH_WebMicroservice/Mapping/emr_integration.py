"""
EMR Integration Module
Connects Traditional Medicine Mapping System to Open EMR Systems
Supports: Bahmni, OpenMRS, OpenEMR
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime


class EMRIntegration:
    """Base class for EMR integration"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.authenticate()
    
    def authenticate(self):
        """Override in subclass"""
        pass
    
    def send_fhir_condition(self, fhir_resource: Dict) -> Dict:
        """Override in subclass"""
        pass


class BahmniIntegration(EMRIntegration):
    """
    Integration with Bahmni EMR
    Bahmni is built on OpenMRS and supports FHIR R4
    """
    
    def authenticate(self):
        """Authenticate with Bahmni/OpenMRS"""
        auth_url = f"{self.base_url}/openmrs/ws/rest/v1/session"
        response = self.session.get(
            auth_url,
            auth=(self.username, self.password),
            headers={'Content-Type': 'application/json'},
            verify=False  # Disable SSL verification for local development
        )
        
        if response.status_code == 200:
            print("✅ Authenticated with Bahmni")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def send_fhir_condition(self, fhir_resource: Dict) -> Dict:
        """
        Send FHIR Condition resource to Bahmni
        
        Args:
            fhir_resource: FHIR R4 Condition resource
            
        Returns:
            Response from Bahmni
        """
        fhir_url = f"{self.base_url}/openmrs/ws/fhir2/R4/Condition"
        
        response = self.session.post(
            fhir_url,
            json=fhir_resource,
            auth=(self.username, self.password),  # Add auth to FHIR request
            headers={
                'Content-Type': 'application/fhir+json',
                'Accept': 'application/fhir+json'
            },
            verify=False  # Disable SSL verification for local development
        )
        
        if response.status_code in [200, 201]:
            print("✅ FHIR Condition sent successfully")
            return response.json()
        else:
            print(f"❌ Failed to send: {response.status_code}")
            print(f"Error: {response.text}")
            return {"error": response.text, "status_code": response.status_code}
    
    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Get patient details from Bahmni"""
        patient_url = f"{self.base_url}/openmrs/ws/fhir2/R4/Patient/{patient_id}"
        
        response = self.session.get(
            patient_url,
            headers={'Accept': 'application/fhir+json'},
            verify=False
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def create_encounter(self, patient_id: str, encounter_type: str = "Consultation") -> Dict:
        """Create an encounter in Bahmni"""
        encounter_url = f"{self.base_url}/openmrs/ws/fhir2/R4/Encounter"
        
        encounter = {
            "resourceType": "Encounter",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "period": {
                "start": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        response = self.session.post(
            encounter_url,
            json=encounter,
            headers={
                'Content-Type': 'application/fhir+json',
                'Accept': 'application/fhir+json'
            }
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        return {"error": response.text}


class OpenEMRIntegration(EMRIntegration):
    """
    Integration with OpenEMR
    OpenEMR has FHIR API certification
    """
    
    def authenticate(self):
        """Authenticate with OpenEMR using OAuth2"""
        # OpenEMR uses OAuth2 - simplified version
        auth_url = f"{self.base_url}/oauth2/default/token"
        
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'scope': 'openid fhirUser offline_access'
        }
        
        response = requests.post(auth_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            print("✅ Authenticated with OpenEMR")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def send_fhir_condition(self, fhir_resource: Dict) -> Dict:
        """Send FHIR Condition to OpenEMR"""
        fhir_url = f"{self.base_url}/apis/default/fhir/Condition"
        
        response = self.session.post(
            fhir_url,
            json=fhir_resource,
            headers={
                'Content-Type': 'application/fhir+json',
                'Accept': 'application/fhir+json'
            }
        )
        
        if response.status_code in [200, 201]:
            print("✅ FHIR Condition sent successfully")
            return response.json()
        else:
            print(f"❌ Failed to send: {response.status_code}")
            return {"error": response.text}


class OpenMRSIntegration(EMRIntegration):
    """
    Integration with OpenMRS
    Similar to Bahmni but standalone OpenMRS
    """
    
    def authenticate(self):
        """Authenticate with OpenMRS"""
        auth_url = f"{self.base_url}/ws/rest/v1/session"
        response = self.session.get(
            auth_url,
            auth=(self.username, self.password),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Authenticated with OpenMRS")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def send_fhir_condition(self, fhir_resource: Dict) -> Dict:
        """Send FHIR Condition to OpenMRS"""
        fhir_url = f"{self.base_url}/ws/fhir2/R4/Condition"
        
        response = self.session.post(
            fhir_url,
            json=fhir_resource,
            headers={
                'Content-Type': 'application/fhir+json',
                'Accept': 'application/fhir+json'
            }
        )
        
        if response.status_code in [200, 201]:
            print("✅ FHIR Condition sent successfully")
            return response.json()
        else:
            print(f"❌ Failed to send: {response.status_code}")
            return {"error": response.text}


# ===== USAGE EXAMPLES =====

def example_bahmni_integration():
    """Example: Send Traditional Medicine mapping to Bahmni"""
    
    # Initialize Bahmni connection
    bahmni = BahmniIntegration(
        base_url="http://localhost:8050",  # Bahmni default
        username="admin",
        password="Admin123"
    )
    
    # Your FHIR Condition from mapping
    fhir_condition = {
        "resourceType": "Condition",
        "id": "tm-mapping-001",
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        },
        "code": {
            "coding": [
                {
                    "system": "http://hl7.org/fhir/sid/icd-11",
                    "code": "SP42",
                    "display": "Lumbar spondylosis disorder"
                }
            ],
            "text": "Siddha: SP42 - Lumbar spondylosis"
        },
        "subject": {
            "reference": "Patient/12345"
        }
    }
    
    # Send to Bahmni
    result = bahmni.send_fhir_condition(fhir_condition)
    print("Result:", result)


def example_openemr_integration():
    """Example: Send to OpenEMR"""
    
    openemr = OpenEMRIntegration(
        base_url="http://localhost:8080",
        username="admin",
        password="pass"
    )
    
    # Send FHIR resource
    # ... similar to Bahmni example


if __name__ == "__main__":
    print("EMR Integration Module")
    print("=" * 50)
    print("\nSupported EMR Systems:")
    print("1. Bahmni (Recommended for India)")
    print("2. OpenMRS")
    print("3. OpenEMR")
    print("\nUsage:")
    print("  from emr_integration import BahmniIntegration")
    print("  bahmni = BahmniIntegration(url, user, pass)")
    print("  bahmni.send_fhir_condition(fhir_resource)")
