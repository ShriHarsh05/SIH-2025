"""
Final Verification Script
Tests all components before demo
"""

import requests
import sys
from datetime import datetime

print("=" * 70)
print("🔍 FINAL VERIFICATION - Testing All Components")
print("=" * 70)

all_passed = True

# Test 1: HAPI FHIR Server
print("\n1. Testing HAPI FHIR Server...")
try:
    response = requests.get("http://localhost:8090/fhir/metadata", timeout=5)
    if response.status_code == 200:
        print("   ✅ HAPI FHIR is running and accessible")
    else:
        print(f"   ❌ HAPI FHIR returned status: {response.status_code}")
        all_passed = False
except Exception as e:
    print(f"   ❌ Cannot connect to HAPI FHIR: {str(e)}")
    print("   Start with: docker run -d -p 8090:8080 --name hapi-fhir hapiproject/hapi:latest")
    all_passed = False

# Test 2: API Server
print("\n2. Testing API Server...")
try:
    response = requests.get("http://localhost:8000/", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("   ✅ API Server is running")
        print(f"   Systems: {', '.join(data.get('supported_systems', []))}")
    else:
        print(f"   ❌ API Server returned status: {response.status_code}")
        all_passed = False
except Exception as e:
    print(f"   ❌ Cannot connect to API Server: {str(e)}")
    print("   Start with: python -m uvicorn api.server:app --reload --port 8000")
    all_passed = False

# Test 3: Authentication
print("\n3. Testing Authentication...")
try:
    response = requests.post(
        "http://localhost:8000/auth/token",
        data={
            "username": "demo@example.com",
            "password": "demo123"
        },
        timeout=5
    )
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("   ✅ Authentication working")
        print(f"   Token: {token[:20]}...")
    else:
        print(f"   ❌ Authentication failed: {response.status_code}")
        all_passed = False
except Exception as e:
    print(f"   ❌ Authentication error: {str(e)}")
    all_passed = False

# Test 4: Search Functionality
print("\n4. Testing Search Functionality...")
try:
    response = requests.post(
        "http://localhost:8000/map",
        json={
            "query": "fever",
            "system": "ayurveda",
            "top_k": 5
        },
        timeout=10
    )
    if response.status_code == 200:
        results = response.json()
        if results:
            print("   ✅ Search working")
            print(f"   Found {len(results)} results")
            print(f"   Top result: {results[0].get('term', 'N/A')}")
        else:
            print("   ⚠️  Search returned no results")
            all_passed = False
    else:
        print(f"   ❌ Search failed: {response.status_code}")
        all_passed = False
except Exception as e:
    print(f"   ❌ Search error: {str(e)}")
    all_passed = False

# Test 5: ICD-11 Mapping
print("\n5. Testing ICD-11 Mapping...")
try:
    response = requests.post(
        "http://localhost:8000/map/ayurveda-code",
        json={
            "code": "AY-FEVER-001",
            "term": "Jwara (Fever disorder)"
        },
        timeout=10
    )
    if response.status_code == 200:
        mappings = response.json()
        if mappings:
            print("   ✅ ICD-11 mapping working")
            print(f"   Found {len(mappings)} mappings")
            print(f"   Top mapping: {mappings[0].get('icd_code', 'N/A')}")
        else:
            print("   ⚠️  Mapping returned no results")
            all_passed = False
    else:
        print(f"   ❌ Mapping failed: {response.status_code}")
        all_passed = False
except Exception as e:
    print(f"   ❌ Mapping error: {str(e)}")
    all_passed = False

# Test 6: FHIR Generation
print("\n6. Testing FHIR Generation...")
try:
    response = requests.post(
        "http://localhost:8000/fhir/condition",
        json={
            "patient_id": "test-patient-verify",
            "encounter_id": None,
            "practitioner_id": None,
            "mapping_result": {
                "system": "ayurveda",
                "ayurveda_candidates": [{
                    "code": "AY-FEVER-001",
                    "term": "Jwara (Fever disorder)",
                    "score": 0.95
                }],
                "icd11_standard_candidates": [{
                    "code": "CA40.Z",
                    "title": "Malaria, unspecified",
                    "score": 0.85
                }],
                "icd11_tm2_candidates": []
            }
        },
        timeout=10
    )
    if response.status_code == 200:
        fhir = response.json()
        if fhir.get("resourceType") == "Condition":
            print("   ✅ FHIR generation working")
            print(f"   Resource type: {fhir.get('resourceType')}")
            print(f"   Codes: {len(fhir.get('code', {}).get('coding', []))}")
        else:
            print("   ⚠️  Invalid FHIR resource")
            print(f"   Response: {fhir}")
            all_passed = False
    else:
        print(f"   ❌ FHIR generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        all_passed = False
except Exception as e:
    print(f"   ❌ FHIR generation error: {str(e)}")
    all_passed = False

# Test 7: EMR Integration (End-to-End)
print("\n7. Testing EMR Integration (End-to-End)...")
try:
    # Create test FHIR condition
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
            "reference": "Patient/final-verify-patient",
            "display": "Final Verification Patient"
        },
        "recordedDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Send to EMR
    response = requests.post(
        "http://localhost:8000/emr/send",
        json={
            "fhir_condition": test_condition,
            "emr_url": "http://localhost:8090/fhir"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            resource_id = result.get("resource_id")
            print("   ✅ EMR integration working")
            print(f"   Resource ID: {resource_id}")
            
            # Verify it's retrievable
            verify_response = requests.get(
                f"http://localhost:8090/fhir/Condition/{resource_id}",
                timeout=5
            )
            if verify_response.status_code == 200:
                print("   ✅ Condition is retrievable from FHIR server")
                print(f"   URL: http://localhost:8090/fhir/Condition/{resource_id}")
            else:
                print("   ⚠️  Condition stored but not retrievable")
                all_passed = False
        else:
            print(f"   ❌ EMR send failed: {result.get('error')}")
            all_passed = False
    else:
        print(f"   ❌ EMR integration failed: {response.status_code}")
        all_passed = False
except Exception as e:
    print(f"   ❌ EMR integration error: {str(e)}")
    all_passed = False

# Final Summary
print("\n" + "=" * 70)
if all_passed:
    print("✅ ALL TESTS PASSED - SYSTEM IS READY FOR DEMO!")
    print("=" * 70)
    print("\n📋 Quick Start:")
    print("   1. Open: http://localhost:8000/ui/index.html")
    print("   2. Login: demo@example.com / demo123")
    print("   3. Search: 'fever' in Ayurveda")
    print("   4. Map to ICD-11")
    print("   5. Send to EMR")
    print("   6. View at: http://localhost:8090/fhir/Condition/{ID}")
    print("\n🎉 You're ready for your demo!")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED - PLEASE FIX BEFORE DEMO")
    print("=" * 70)
    print("\n🔧 Check the errors above and:")
    print("   1. Make sure HAPI FHIR is running")
    print("   2. Make sure API server is running")
    print("   3. Check for any error messages")
    print("   4. Run this script again")
    sys.exit(1)
