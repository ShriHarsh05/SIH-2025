"""
Test sending a condition to the actual patient in Bahmni
"""

import requests
import json
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BAHMNI_URL = "http://localhost"
USERNAME = "superman"
PASSWORD = "Admin123"
PATIENT_ID = "b4f7d426-7471-4e9d-a204-64441b18a147"

print("=" * 70)
print("🧪 Testing Condition Send to Bahmni")
print("=" * 70)

# Step 1: Verify patient exists
print(f"\n1. Verifying patient {PATIENT_ID[:8]}...")
response = requests.get(
    f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Patient/{PATIENT_ID}",
    auth=(USERNAME, PASSWORD),
    headers={'Accept': 'application/fhir+json'},
    verify=False
)

if response.status_code == 200:
    patient = response.json()
    print(f"   ✅ Patient found!")
    names = patient.get('name', [{}])
    name = names[0].get('text', 'Unknown') if names else 'Unknown'
    print(f"   Name: {name}")
else:
    print(f"   ❌ Patient not found: {response.status_code}")
    exit(1)

# Step 2: Create a test FHIR Condition
print(f"\n2. Creating test FHIR Condition...")

test_condition = {
    "resourceType": "Condition",
    "clinicalStatus": {
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "active",
            "display": "Active"
        }]
    },
    "verificationStatus": {
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
            "code": "confirmed",
            "display": "Confirmed"
        }]
    },
    "category": [{
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
            "code": "encounter-diagnosis",
            "display": "Encounter Diagnosis"
        }]
    }],
    "code": {
        "coding": [
            {
                "system": "http://hl7.org/fhir/sid/icd-11",
                "code": "CA40.Z",
                "display": "Malaria, unspecified"
            },
            {
                "system": "http://id.who.int/icd/release/11/mms",
                "code": "TM1.AY11",
                "display": "Siddha: Fever disorder"
            }
        ],
        "text": "Test condition from Traditional Medicine Mapping System"
    },
    "subject": {
        "reference": f"Patient/{PATIENT_ID}",
        "display": name
    },
    "recordedDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "note": [{
        "text": "Test condition sent from Traditional Medicine → ICD-11 Mapping System. This demonstrates successful EMR integration."
    }]
}

print(f"   ✅ FHIR Condition created")
print(f"   ICD-11 Code: {test_condition['code']['coding'][0]['code']}")
print(f"   Display: {test_condition['code']['coding'][0]['display']}")

# Step 3: Send to Bahmni
print(f"\n3. Sending to Bahmni EMR...")

response = requests.post(
    f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Condition",
    json=test_condition,
    auth=(USERNAME, PASSWORD),
    headers={
        'Content-Type': 'application/fhir+json',
        'Accept': 'application/fhir+json'
    },
    verify=False
)

if response.status_code in [200, 201]:
    result = response.json()
    resource_id = result.get('id', 'N/A')
    print(f"   ✅ Successfully sent to Bahmni!")
    print(f"   Resource ID: {resource_id}")
    
    # Step 4: Verify it was saved
    print(f"\n4. Verifying condition was saved...")
    verify_response = requests.get(
        f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Condition/{resource_id}",
        auth=(USERNAME, PASSWORD),
        headers={'Accept': 'application/fhir+json'},
        verify=False
    )
    
    if verify_response.status_code == 200:
        print(f"   ✅ Condition verified in EMR!")
        
        # Step 5: Get all conditions for this patient
        print(f"\n5. Fetching all conditions for patient...")
        patient_cond_response = requests.get(
            f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Condition?patient={PATIENT_ID}",
            auth=(USERNAME, PASSWORD),
            headers={'Accept': 'application/fhir+json'},
            verify=False
        )
        
        if patient_cond_response.status_code == 200:
            bundle = patient_cond_response.json()
            total = bundle.get('total', 0)
            print(f"   ✅ Patient now has {total} condition(s)")
            
            print("\n" + "=" * 70)
            print("🎉 SUCCESS!")
            print("=" * 70)
            print(f"\nCondition successfully sent and verified!")
            print(f"\n📋 Details:")
            print(f"   - Patient ID: {PATIENT_ID}")
            print(f"   - Patient Name: {name}")
            print(f"   - Condition ID: {resource_id}")
            print(f"   - Total Conditions: {total}")
            
            print(f"\n🌐 View in Bahmni:")
            print(f"   1. Open: http://localhost")
            print(f"   2. Login: superman / Admin123")
            print(f"   3. Go to: Clinical → Search Patient")
            print(f"   4. Search for: {name}")
            print(f"   5. View conditions in patient dashboard")
            
            print(f"\n🔗 Direct FHIR Access:")
            print(f"   Patient: {BAHMNI_URL}/openmrs/ws/fhir2/R4/Patient/{PATIENT_ID}")
            print(f"   Condition: {BAHMNI_URL}/openmrs/ws/fhir2/R4/Condition/{resource_id}")
    else:
        print(f"   ⚠️  Could not verify: {verify_response.status_code}")
else:
    print(f"   ❌ Failed to send: {response.status_code}")
    print(f"   Error: {response.text}")

print("\n✨ Test complete!")
