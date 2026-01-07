"""
Diagnostic script to check EMR integration
"""

import requests
import json

print("="*70)
print("EMR INTEGRATION DIAGNOSTIC")
print("="*70)

# Step 1: Check if HAPI FHIR server is running
print("\n1. Checking HAPI FHIR Server...")
try:
    response = requests.get("http://localhost:8090/fhir/metadata", timeout=5)
    if response.status_code == 200:
        print("   ✓ HAPI FHIR server is running on port 8090")
    else:
        print(f"   ✗ HAPI FHIR server returned status {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot connect to HAPI FHIR server: {e}")
    print("   → Make sure HAPI FHIR is running (docker-compose up)")

# Step 2: Check if API server is running
print("\n2. Checking API Server...")
try:
    response = requests.get("http://localhost:8000/", timeout=5)
    if response.status_code == 200:
        print("   ✓ API server is running on port 8000")
    else:
        print(f"   ✗ API server returned status {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot connect to API server: {e}")
    print("   → Start the server: uvicorn api.server:app --reload")

# Step 3: Check if patient exists
print("\n3. Checking Patient in HAPI FHIR...")
patient_id = "b4f7d426-7471-4e9d-a204-64441b18a147"
try:
    response = requests.get(f"http://localhost:8090/fhir/Patient/{patient_id}", timeout=5)
    if response.status_code == 200:
        print(f"   ✓ Patient {patient_id} exists")
    elif response.status_code == 404:
        print(f"   ✗ Patient {patient_id} not found")
        print("   → Create patient first or use a different patient ID")
    else:
        print(f"   ✗ Unexpected status {response.status_code}")
except Exception as e:
    print(f"   ✗ Error checking patient: {e}")

# Step 4: List existing conditions
print("\n4. Checking Existing Conditions...")
try:
    response = requests.get("http://localhost:8090/fhir/Condition", timeout=5)
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', 0)
        print(f"   ✓ Found {total} conditions in EMR")
        
        if total > 0:
            print("\n   Recent conditions:")
            entries = data.get('entry', [])[:3]  # Show first 3
            for entry in entries:
                resource = entry.get('resource', {})
                cond_id = resource.get('id', 'N/A')
                recorded = resource.get('recordedDate', 'N/A')
                print(f"   - ID: {cond_id}, Recorded: {recorded}")
    else:
        print(f"   ✗ Cannot list conditions: status {response.status_code}")
except Exception as e:
    print(f"   ✗ Error listing conditions: {e}")

# Step 5: Test FHIR generation
print("\n5. Testing FHIR Generation...")
try:
    test_mapping = {
        "system": "siddha",
        "input": "test symptoms",
        "siddha_candidates": [{
            "code": "TEST",
            "term": "Test Term",
            "english": "Test English",
            "definition": "Test definition",
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
        if 'error' in fhir_data:
            print(f"   ✗ FHIR generation error: {fhir_data['error']}")
        else:
            print("   ✓ FHIR Condition generated successfully")
            print(f"   - Resource Type: {fhir_data.get('resourceType')}")
            print(f"   - ID: {fhir_data.get('id')}")
    else:
        print(f"   ✗ FHIR generation failed: status {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ✗ Error testing FHIR generation: {e}")

# Step 6: Test EMR send
print("\n6. Testing EMR Send...")
try:
    # First generate FHIR
    response = requests.post(
        "http://localhost:8000/fhir/condition",
        json={
            "mapping_result": test_mapping,
            "patient_id": patient_id
        },
        timeout=10
    )
    
    if response.status_code == 200:
        fhir_condition = response.json()
        
        # Now send to EMR
        emr_response = requests.post(
            "http://localhost:8000/emr/send",
            json={
                "fhir_condition": fhir_condition,
                "emr_url": "http://localhost:8090/fhir",
                "username": "",
                "password": ""
            },
            timeout=15
        )
        
        if emr_response.status_code == 200:
            result = emr_response.json()
            if result.get('success'):
                print("   ✓ Successfully sent to EMR")
                print(f"   - Resource ID: {result.get('resource_id')}")
                print(f"   - View at: http://localhost:8090/fhir/Condition/{result.get('resource_id')}")
            else:
                print(f"   ✗ EMR send failed: {result.get('error')}")
        else:
            print(f"   ✗ EMR send failed: status {emr_response.status_code}")
            print(f"   Response: {emr_response.text[:200]}")
    else:
        print("   ✗ Cannot test EMR send (FHIR generation failed)")
        
except Exception as e:
    print(f"   ✗ Error testing EMR send: {e}")

# Summary
print("\n" + "="*70)
print("DIAGNOSTIC SUMMARY")
print("="*70)
print("\nIf you see errors above, fix them in this order:")
print("1. Start HAPI FHIR server (docker-compose up)")
print("2. Start API server (uvicorn api.server:app --reload)")
print("3. Ensure patient exists in HAPI FHIR")
print("4. Test sending data through the UI")
print("\nFor UI issues:")
print("- Hard refresh browser (Ctrl+F5)")
print("- Check browser console for errors (F12)")
print("- Verify you're logged in (demo@example.com / demo123)")
print("="*70)
