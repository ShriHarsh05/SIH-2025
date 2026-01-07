"""
Test Siddha Condition Sending
"""

import requests
from datetime import datetime

print("Testing Siddha Condition...")

# Step 1: Search for Siddha term
print("\n1. Searching for 'Vali'...")
search_response = requests.post(
    "http://localhost:8000/map",
    json={
        "query": "Vali",
        "system": "siddha",
        "top_k": 5
    }
)

if search_response.status_code == 200:
    results = search_response.json()
    if results:
        print(f"   Found {len(results)} results")
        first_result = results[0]
        print(f"   Top result: {first_result.get('term', 'N/A')}")
        print(f"   Code: {first_result.get('code', 'N/A')}")
        
        # Step 2: Map to ICD-11
        print("\n2. Mapping to ICD-11...")
        map_response = requests.post(
            "http://localhost:8000/map/siddha-code",
            json={
                "code": first_result.get('code', ''),
                "term": first_result.get('term', '')
            }
        )
        
        if map_response.status_code == 200:
            mappings = map_response.json()
            print(f"   Found {len(mappings)} mappings")
            
            # Step 3: Generate FHIR
            print("\n3. Generating FHIR Condition...")
            fhir_response = requests.post(
                "http://localhost:8000/fhir/condition",
                json={
                    "patient_id": "test-siddha-patient",
                    "mapping_result": mappings[0] if mappings else {}
                }
            )
            
            if fhir_response.status_code == 200:
                fhir_condition = fhir_response.json()
                print("   ✅ FHIR Condition generated")
                
                # Check the coding
                codings = fhir_condition.get('code', {}).get('coding', [])
                print(f"\n   Codings in FHIR resource:")
                for i, coding in enumerate(codings):
                    print(f"   {i+1}. System: {coding.get('system', 'N/A')}")
                    print(f"      Code: {coding.get('code', 'N/A')}")
                    print(f"      Display: {coding.get('display', 'N/A')}")
                
                # Step 4: Send to EMR
                print("\n4. Sending to HAPI FHIR...")
                emr_response = requests.post(
                    "http://localhost:8000/emr/send",
                    json={
                        "fhir_condition": fhir_condition,
                        "emr_url": "http://localhost:8090/fhir"
                    }
                )
                
                if emr_response.status_code == 200:
                    result = emr_response.json()
                    if result.get("success"):
                        resource_id = result.get("resource_id")
                        print(f"   ✅ Condition sent successfully!")
                        print(f"   Resource ID: {resource_id}")
                        print(f"\n   View in EMR Viewer:")
                        print(f"   http://localhost:8000/ui/emr_viewer.html")
                        print(f"\n   View FHIR JSON:")
                        print(f"   http://localhost:8090/fhir/Condition/{resource_id}")
                    else:
                        print(f"   ❌ Failed: {result.get('error')}")
                else:
                    print(f"   ❌ EMR send failed: {emr_response.status_code}")
            else:
                print(f"   ❌ FHIR generation failed: {fhir_response.status_code}")
                print(f"   Response: {fhir_response.text}")
        else:
            print(f"   ❌ Mapping failed: {map_response.status_code}")
            print(f"   Response: {map_response.text}")
    else:
        print("   No results found")
else:
    print(f"   ❌ Search failed: {search_response.status_code}")

print("\n" + "="*60)
