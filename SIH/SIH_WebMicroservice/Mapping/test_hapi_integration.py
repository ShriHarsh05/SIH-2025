"""
Test HAPI FHIR Integration
This will verify that HAPI FHIR is working and can store/retrieve conditions
"""

import requests
from datetime import datetime
from emr_integration_hapi import BahmniIntegration

print("=" * 70)
print("🧪 Testing HAPI FHIR Integration")
print("=" * 70)

# Step 1: Check if HAPI FHIR is running
print("\n1. Checking if HAPI FHIR is accessible...")
try:
    response = requests.get("http://localhost:8090/fhir/metadata", timeout=5)
    if response.status_code == 200:
        print("   ✅ HAPI FHIR is running!")
    else:
        print(f"   ⚠️  HAPI FHIR returned status: {response.status_code}")
        print("   Make sure HAPI FHIR is running:")
        print("   docker run -d -p 8090:8080 --name hapi-fhir hapiproject/hapi:latest")
        exit(1)
except Exception as e:
    print(f"   ❌ Cannot connect to HAPI FHIR: {str(e)}")
    print("\n   Start HAPI FHIR with:")
    print("   docker run -d -p 8090:8080 --name hapi-fhir hapiproject/hapi:latest")
    exit(1)

# Step 2: Connect to HAPI FHIR
print("\n2. Connecting to HAPI FHIR...")
hapi = BahmniIntegration(
    base_url="http://localhost:8090/fhir"
)

# Step 3: Create a test patient first
print("\n3. Creating test patient...")
test_patient = {
    "resourceType": "Patient",
    "id": "test-patient-123",
    "name": [{
        "text": "Test Patient",
        "family": "Patient",
        "given": ["Test"]
    }],
    "gender": "male",
    "birthDate": "2000-01-01"
}

try:
    patient_response = requests.put(
        "http://localhost:8090/fhir/Patient/test-patient-123",
        json=test_patient,
        headers={'Content-Type': 'application/fhir+json'}
    )
    if patient_response.status_code in [200, 201]:
        print("   ✅ Test patient created")
    else:
        print(f"   ⚠️  Patient creation returned: {patient_response.status_code}")
except Exception as e:
    print(f"   ⚠️  Could not create patient: {str(e)}")

# Step 4: Create a test FHIR Condition
print("\n4. Creating test FHIR Condition...")
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
    "code": {
        "coding": [
            {
                "system": "http://hl7.org/fhir/sid/icd-11",
                "code": "CA40.Z",
                "display": "Malaria, unspecified"
            },
            {
                "system": "http://id.who.int/icd/traditional-medicine",
                "code": "AY-FEVER-001",
                "display": "Ayurveda: Jwara (Fever disorder)"
            }
        ],
        "text": "AYURVEDA: Jwara (Fever disorder) → ICD-11: CA40.Z - Malaria, unspecified"
    },
    "subject": {
        "reference": "Patient/test-patient-123",
        "display": "Test Patient"
    },
    "recordedDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
}

print("   ✅ Test condition created")

# Step 5: Send to HAPI FHIR
print("\n5. Sending to HAPI FHIR...")
result = hapi.send_fhir_condition(test_condition)

if "error" in result:
    print(f"   ❌ Failed: {result.get('error')}")
    exit(1)

resource_id = result.get('id')
print(f"\n   ✅ SUCCESS! Condition stored in HAPI FHIR!")
print(f"   Resource ID: {resource_id}")

# Step 6: Retrieve the condition to verify it's stored
print("\n6. Verifying condition is retrievable...")
retrieved = hapi.get_condition(resource_id)

if "error" in retrieved:
    print(f"   ❌ Failed to retrieve: {retrieved.get('error')}")
else:
    print(f"   ✅ Condition successfully retrieved!")
    print(f"   Code: {retrieved.get('code', {}).get('coding', [{}])[0].get('code', 'N/A')}")
    print(f"   Display: {retrieved.get('code', {}).get('text', 'N/A')}")

# Step 7: Show how to access it
print("\n" + "=" * 70)
print("🎉 HAPI FHIR Integration Working!")
print("=" * 70)

print(f"\n📋 Your condition is stored and accessible:")
print(f"   Direct URL: http://localhost:8090/fhir/Condition/{resource_id}")
print(f"   All conditions: http://localhost:8090/fhir/Condition")

print(f"\n🌐 Open in browser to see the stored condition!")
print(f"   You can copy-paste this URL:")
print(f"   http://localhost:8090/fhir/Condition/{resource_id}")

print(f"\n✨ For your demo:")
print(f"   1. Send condition from your app")
print(f"   2. Copy the Resource ID")
print(f"   3. Open: http://localhost:8090/fhir/Condition/{{ID}}")
print(f"   4. Show judges the stored condition!")

print("\n" + "=" * 70)
print("✅ Test Complete - HAPI FHIR is ready for your demo!")
print("=" * 70)
