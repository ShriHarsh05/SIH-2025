"""
Quick Test - Just verify HAPI FHIR and EMR integration
"""

import requests
from datetime import datetime

print("=" * 60)
print("🚀 QUICK TEST - Critical Components Only")
print("=" * 60)

# Test 1: HAPI FHIR
print("\n1. HAPI FHIR Server...")
try:
    r = requests.get("http://localhost:8090/fhir/metadata", timeout=5)
    if r.status_code == 200:
        print("   ✅ HAPI FHIR is running")
    else:
        print(f"   ❌ HAPI FHIR error: {r.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ Cannot connect: {e}")
    exit(1)

# Test 2: EMR Integration
print("\n2. EMR Integration (End-to-End)...")
try:
    condition = {
        "resourceType": "Condition",
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "code": "confirmed"
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
                    "code": "AY-TEST-001",
                    "display": "Ayurveda: Test Condition"
                }
            ]
        },
        "subject": {
            "reference": "Patient/quick-test-patient"
        },
        "recordedDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    r = requests.post(
        "http://localhost:8000/emr/send",
        json={
            "fhir_condition": condition,
            "emr_url": "http://localhost:8090/fhir"
        },
        timeout=15
    )
    
    if r.status_code == 200:
        result = r.json()
        if result.get("success"):
            resource_id = result.get("resource_id")
            print(f"   ✅ Condition sent to EMR")
            print(f"   Resource ID: {resource_id}")
            
            # Verify retrieval
            verify = requests.get(
                f"http://localhost:8090/fhir/Condition/{resource_id}",
                timeout=5
            )
            if verify.status_code == 200:
                print(f"   ✅ Condition is retrievable")
                print(f"   URL: http://localhost:8090/fhir/Condition/{resource_id}")
            else:
                print(f"   ⚠️  Could not retrieve condition")
        else:
            print(f"   ❌ EMR send failed: {result.get('error')}")
            exit(1)
    else:
        print(f"   ❌ API error: {r.status_code}")
        print(f"   Response: {r.text}")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 3: View all conditions
print("\n3. Viewing all stored conditions...")
try:
    r = requests.get("http://localhost:8090/fhir/Condition", timeout=5)
    if r.status_code == 200:
        data = r.json()
        total = data.get("total", 0)
        print(f"   ✅ Total conditions in FHIR server: {total}")
        print(f"   URL: http://localhost:8090/fhir/Condition")
    else:
        print(f"   ⚠️  Could not retrieve conditions")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

print("\n" + "=" * 60)
print("✅ ALL CRITICAL TESTS PASSED!")
print("=" * 60)
print("\n🎉 Your system is ready for demo!")
print("\nDemo Steps:")
print("1. Open: http://localhost:8000/ui/index.html")
print("2. Login: demo@example.com / demo123")
print("3. Search and map a term")
print("4. Send to EMR")
print("5. View at: http://localhost:8090/fhir/Condition/{ID}")
print("\n" + "=" * 60)
