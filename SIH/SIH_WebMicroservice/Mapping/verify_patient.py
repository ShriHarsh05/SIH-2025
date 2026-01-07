"""
Verify Patient ABC200000 exists in Bahmni
"""

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BAHMNI_URL = "http://localhost"
USERNAME = "superman"
PASSWORD = "Admin123"
PATIENT_ID = "ABC200000"

print("=" * 70)
print("🔍 Verifying Patient in Bahmni")
print("=" * 70)

# Check if patient exists
print(f"\n1. Checking if Patient '{PATIENT_ID}' exists...")
response = requests.get(
    f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Patient/{PATIENT_ID}",
    auth=(USERNAME, PASSWORD),
    headers={'Accept': 'application/fhir+json'},
    verify=False
)

if response.status_code == 200:
    patient = response.json()
    print(f"   ✅ Patient found!")
    
    # Extract patient details
    names = patient.get('name', [{}])
    name_text = names[0].get('text', 'N/A') if names else 'N/A'
    
    gender = patient.get('gender', 'N/A')
    birth_date = patient.get('birthDate', 'N/A')
    
    print(f"\n   📋 Patient Details:")
    print(f"   - ID: {PATIENT_ID}")
    print(f"   - Name: {name_text}")
    print(f"   - Gender: {gender}")
    print(f"   - Birth Date: {birth_date}")
    
    # Check for existing conditions
    print(f"\n2. Checking existing conditions for this patient...")
    cond_response = requests.get(
        f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Condition?patient={PATIENT_ID}",
        auth=(USERNAME, PASSWORD),
        headers={'Accept': 'application/fhir+json'},
        verify=False
    )
    
    if cond_response.status_code == 200:
        bundle = cond_response.json()
        total = bundle.get('total', 0)
        print(f"   ✅ Found {total} condition(s) for this patient")
        
        if total > 0:
            entries = bundle.get('entry', [])
            print(f"\n   📋 Existing Conditions:")
            for idx, entry in enumerate(entries, 1):
                resource = entry.get('resource', {})
                condition_id = resource.get('id', 'N/A')
                code = resource.get('code', {})
                text = code.get('text', 'N/A')
                codings = code.get('coding', [])
                
                print(f"\n   Condition #{idx}:")
                print(f"   - Resource ID: {condition_id}")
                print(f"   - Description: {text}")
                
                if codings:
                    print(f"   - Codes:")
                    for coding in codings:
                        system = coding.get('system', 'N/A')
                        code_val = coding.get('code', 'N/A')
                        display = coding.get('display', 'N/A')
                        print(f"     • {code_val}: {display}")
    
    print("\n" + "=" * 70)
    print("✅ READY TO SEND CONDITIONS")
    print("=" * 70)
    print(f"\nYour application is configured correctly!")
    print(f"Patient ID '{PATIENT_ID}' exists in Bahmni.")
    print(f"\nNext steps:")
    print(f"1. Go to http://localhost:8000")
    print(f"2. Login with demo@example.com / demo123")
    print(f"3. Map a traditional medicine term to ICD-11")
    print(f"4. Click 'Send to Bahmni EMR'")
    print(f"5. The condition will be saved to patient {PATIENT_ID}")
    print(f"\nTo view in Bahmni:")
    print(f"1. Go to http://localhost")
    print(f"2. Login with superman / Admin123")
    print(f"3. Search for patient: {PATIENT_ID}")
    print(f"4. View their conditions in the patient dashboard")
    
elif response.status_code == 404:
    print(f"   ❌ Patient '{PATIENT_ID}' not found!")
    print(f"\n   💡 Please create this patient in Bahmni:")
    print(f"   1. Go to http://localhost")
    print(f"   2. Login: superman / Admin123")
    print(f"   3. Click 'Registration' → 'Create New'")
    print(f"   4. Use Patient ID: {PATIENT_ID}")
    print(f"   5. Fill in other details and save")
else:
    print(f"   ❌ Error: {response.status_code}")
    print(f"   {response.text[:200]}")

print("\n✨ Verification complete!")
