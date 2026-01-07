"""
Test script for ICD-11 to FHIR CodeSystem Pipeline
"""

import json
from icd11_fhir_pipeline import ICD11FHIRPipeline

# WHO ICD-11 API credentials
CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='

def test_pipeline():
    """Test the ICD-11 to FHIR pipeline with multiple codes"""
    
    print("="*70)
    print("ICD-11 to FHIR CodeSystem Pipeline - Test Suite")
    print("="*70)
    
    # Initialize pipeline
    pipeline = ICD11FHIRPipeline(CLIENT_ID, CLIENT_SECRET)
    
    # Test cases
    test_codes = [
        "1A00",  # Cholera
        "1A01",  # Another infectious disease
        "2560",  # From your example
        "FA20.0" # Low back pain
    ]
    
    results = []
    
    for code in test_codes:
        print(f"\n{'='*70}")
        print(f"Testing ICD-11 Code: {code}")
        print('='*70)
        
        try:
            # Process the code
            result = pipeline.process_code(code)
            
            # Display the result
            print("\n✓ SUCCESS - FHIR CodeSystem Generated:")
            print(json.dumps(result, indent=2))
            
            # Extract key information
            concept = result['concept'][0]
            entity_id = concept['extension'][0]['valueString']
            
            print(f"\n📋 Summary:")
            print(f"   Code:       {concept['code']}")
            print(f"   Disease:    {concept['display']}")
            print(f"   Entity ID:  {entity_id}")
            
            results.append({
                'code': code,
                'status': 'success',
                'result': result
            })
            
        except ValueError as e:
            print(f"\n✗ NOT FOUND: {e}")
            results.append({
                'code': code,
                'status': 'not_found',
                'error': str(e)
            })
            
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            results.append({
                'code': code,
                'status': 'error',
                'error': str(e)
            })
    
    # Summary
    print(f"\n{'='*70}")
    print("Test Summary")
    print('='*70)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    
    print(f"\nTotal Tests: {total_count}")
    print(f"Successful:  {success_count}")
    print(f"Failed:      {total_count - success_count}")
    
    print(f"\n{'='*70}")
    print("Pipeline testing complete!")
    print('='*70)
    
    return results


def test_api_integration():
    """Test the API endpoint integration"""
    
    print("\n" + "="*70)
    print("Testing API Integration")
    print("="*70)
    
    import requests
    
    # Test POST endpoint
    print("\n1. Testing POST /icd11/to-fhir")
    try:
        response = requests.post(
            "http://localhost:8000/icd11/to-fhir",
            json={"code": "1A00"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   (Make sure the server is running: uvicorn api.server:app --reload)")
    
    # Test GET endpoint
    print("\n2. Testing GET /icd11/to-fhir/1A00")
    try:
        response = requests.get("http://localhost:8000/icd11/to-fhir/1A00")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   (Make sure the server is running: uvicorn api.server:app --reload)")


if __name__ == "__main__":
    # Test the pipeline directly
    results = test_pipeline()
    
    # Test API integration (optional - requires server to be running)
    print("\n\nWould you like to test the API endpoints?")
    print("(Make sure the server is running first)")
    response = input("Test API? (y/n): ").strip().lower()
    
    if response == 'y':
        test_api_integration()
