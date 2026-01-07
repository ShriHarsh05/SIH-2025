"""
Quick test to verify EMR send fix (removing ID before POST)
"""

import requests
import json

# Test data
test_mapping = {
    "system": "siddha",
    "input": "Test symptoms",
    "siddha_candidates": [{
        "code": "TEST",
        "term": "Test Term",
        "score": 0.9
    }],
    "icd11_standard_candidates": [{
        "code": "1A00",
        "title": "Cholera",
        "definition": "Test",
        "score": 0.8
    }],
    "icd11_tm2_candidates": []
}

patient_id = "b4f7d426-7471-4e9d-a204-64441b18a147"

print("=" * 70)
print("TESTING EMR SEND FIX")
print("=" * 70)

# Step 1: Generate FHIR Condition
print("\n1. Generating FHIR Condition...")
try:
    response = requests.post(
        "http://localhost:8000/fhir/condition",
        json={
            "mapping_result": test_mapping,
            "patient_id": patient_id
        },
        timeout=10
    )
    
    if response.status_code == 200:
        fhir_data = response.json()
        print(f"   ✓ FHIR generated successfully")
        print(f"   - Resource Type: {fhir_data.get('resourceType')}")
        print(f"   - Generated ID: {fhir_data.get('id')}")
        print(f"   - Has 'id' field: {'id' in fhir_data}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
        print(f"   {response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Step 2: Send to EMR
print("\n2. Sending to HAPI FHIR EMR...")
try:
    response = requests.post(
        "http://localhost:8000/emr/send",
        json={
            "fhir_condition": fhir_data,
            "emr_url": "http://localhost:8090/fhir",
            "username": "",
            "password": ""
        },
        timeout=30
    )
    
    result = response.json()
    
    if result.get('success'):
        print(f"   ✓ Successfully sent to EMR!")
        print(f"   - Resource ID: {result.get('resource_id')}")
        print(f"   - View at: http://localhost:8090/fhir/Condition/{result.get('resource_id')}")
    else:
        print(f"   ✗ Failed to send to EMR")
        print(f"   - Error: {result.get('error')}")
        print(f"   - Status Code: {result.get('status_code')}")
        print(f"\n   Full response:")
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
