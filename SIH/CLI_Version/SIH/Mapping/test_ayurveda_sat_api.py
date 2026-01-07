#!/usr/bin/env python3
"""
Test script for Ayurveda-SAT API endpoint
"""

import requests
import json

API_URL = "http://127.0.0.1:8000"

def test_ayurveda_sat_mapping():
    """Test the Ayurveda-SAT to ICD mapping endpoint"""
    
    print("=" * 70)
    print("TESTING AYURVEDA-SAT API ENDPOINT")
    print("=" * 70)
    
    # Test data
    test_code = "SAT-C.1"
    test_term = "vyAdhiH"
    
    print(f"\nTest Input:")
    print(f"  Code: {test_code}")
    print(f"  Term: {test_term}")
    
    # Make API request
    print(f"\nCalling API: POST {API_URL}/map/ayurveda-sat-code")
    
    try:
        response = requests.post(
            f"{API_URL}/map/ayurveda-sat-code",
            json={"code": test_code, "term": test_term},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "=" * 70)
            print("API RESPONSE")
            print("=" * 70)
            
            # Print full response
            print(json.dumps(data, indent=2))
            
            # Check for required keys
            print("\n" + "=" * 70)
            print("VALIDATION")
            print("=" * 70)
            
            required_keys = [
                "input",
                "system",
                "ayurveda_sat_candidates",
                "icd11_standard_candidates",
                "icd11_tm2_candidates"
            ]
            
            for key in required_keys:
                if key in data:
                    count = len(data[key]) if isinstance(data[key], list) else "N/A"
                    print(f"✓ {key}: {count if count != 'N/A' else 'present'}")
                else:
                    print(f"✗ {key}: MISSING!")
            
            # Check if ICD candidates are empty
            print("\n" + "=" * 70)
            print("ICD CANDIDATES CHECK")
            print("=" * 70)
            
            icd_std_count = len(data.get("icd11_standard_candidates", []))
            icd_tm2_count = len(data.get("icd11_tm2_candidates", []))
            
            print(f"ICD-11 Standard: {icd_std_count} candidates")
            print(f"ICD-11 TM2: {icd_tm2_count} candidates")
            
            if icd_std_count == 0:
                print("\n⚠ WARNING: No ICD-11 Standard candidates returned!")
            if icd_tm2_count == 0:
                print("\n⚠ WARNING: No ICD-11 TM2 candidates returned!")
            
            if icd_std_count > 0 and icd_tm2_count > 0:
                print("\n✓ SUCCESS: Both ICD candidate lists have results!")
                
                # Show sample ICD codes
                print("\n" + "=" * 70)
                print("SAMPLE ICD CODES")
                print("=" * 70)
                
                print("\nICD-11 Standard (first 3):")
                for i, candidate in enumerate(data["icd11_standard_candidates"][:3], 1):
                    print(f"  {i}. {candidate.get('code')} - {candidate.get('title')}")
                
                print("\nICD-11 TM2 (first 3):")
                for i, candidate in enumerate(data["icd11_tm2_candidates"][:3], 1):
                    print(f"  {i}. {candidate.get('code')} - {candidate.get('title')}")
            
        else:
            print(f"\n✗ ERROR: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to API server")
        print("Make sure the server is running: python api/server.py")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_ayurveda_sat_mapping()
