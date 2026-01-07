"""
Quick test script to verify Bahmni Demo integration
No local installation required!
"""

from emr_integration import BahmniIntegration
from datetime import datetime

print("=" * 60)
print("🏥 Testing Bahmni Demo Integration")
print("=" * 60)

# Connect to Bahmni Demo Server
print("\n1. Connecting to Bahmni Demo Server...")
print("   URL: https://demo.mybahmni.org")

try:
    bahmni = BahmniIntegration(
        base_url="https://demo.mybahmni.org",
        username="superman",
        password="Admin123"
    )
    print("   ✅ Connected successfully!")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    exit(1)

# Create a test FHIR Condition from Traditional Medicine mapping
print("\n2. Creating FHIR Condition resource...")

test_fhir = {
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
                "code": "SP42",
                "display": "Lumbar spondylosis disorder"
            }
        ],
        "text": "Siddha: SP42 - Lumbar spondylosis disorder (Traditional Medicine Mapping)"
    },
    "subject": {
        "reference": "Patient/1",
        "display": "Test Patient"
    },
    "recordedDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "note": [{
        "text": "Mapped from Traditional Medicine (Siddha) to ICD-11 using AI-powered hybrid retrieval system"
    }]
}

print("   ✅ FHIR resource created")
print(f"   Code: {test_fhir['code']['coding'][0]['code']}")
print(f"   Display: {test_fhir['code']['coding'][0]['display']}")

# Send to Bahmni
print("\n3. Sending to Bahmni EMR...")

try:
    result = bahmni.send_fhir_condition(test_fhir)
    
    if "error" in result:
        print(f"   ❌ Failed: {result['error']}")
    else:
        print("   ✅ Successfully sent to Bahmni!")
        print(f"   Resource ID: {result.get('id', 'N/A')}")
        print("\n4. View in Bahmni:")
        print("   URL: https://demo.mybahmni.org/")
        print("   Login: superman / Admin123")
        print("   Navigate to: Clinical → Patient Dashboard")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Test Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Add EMR endpoint to your FastAPI server")
print("2. Update UI with 'Send to EMR' button")
print("3. Test with your actual mapping results")
print("\nSee QUICK_EMR_DEMO.md for detailed integration guide")
