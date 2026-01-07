"""
View FHIR Conditions in Bahmni EMR
Fetches and displays all conditions stored in the EMR
"""

import requests
import json
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Bahmni Configuration
BAHMNI_URL = "http://localhost"
USERNAME = "superman"
PASSWORD = "Admin123"

print("=" * 80)
print("🏥 Bahmni EMR - View Conditions")
print("=" * 80)

# Authenticate
print("\n1. Authenticating with Bahmni...")
session = requests.Session()
auth_response = session.get(
    f"{BAHMNI_URL}/openmrs/ws/rest/v1/session",
    auth=(USERNAME, PASSWORD),
    verify=False
)

if auth_response.status_code == 200:
    print("   ✅ Authenticated successfully")
    user_data = auth_response.json()
    print(f"   User: {user_data.get('user', {}).get('display', 'N/A')}")
else:
    print(f"   ❌ Authentication failed: {auth_response.status_code}")
    exit(1)

# Fetch all conditions
print("\n2. Fetching FHIR Conditions...")
fhir_url = f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Condition"

response = session.get(
    fhir_url,
    auth=(USERNAME, PASSWORD),
    headers={'Accept': 'application/fhir+json'},
    verify=False
)

if response.status_code == 200:
    bundle = response.json()
    total = bundle.get('total', 0)
    print(f"   ✅ Found {total} condition(s)")
    
    if total > 0:
        print("\n" + "=" * 80)
        print("📋 CONDITIONS IN EMR")
        print("=" * 80)
        
        entries = bundle.get('entry', [])
        for idx, entry in enumerate(entries, 1):
            resource = entry.get('resource', {})
            
            print(f"\n{'─' * 80}")
            print(f"Condition #{idx}")
            print(f"{'─' * 80}")
            
            # Resource ID
            resource_id = resource.get('id', 'N/A')
            print(f"🆔 Resource ID: {resource_id}")
            
            # Patient
            subject = resource.get('subject', {})
            patient_ref = subject.get('reference', 'N/A')
            patient_display = subject.get('display', 'N/A')
            print(f"👤 Patient: {patient_display} ({patient_ref})")
            
            # Clinical Status
            clinical_status = resource.get('clinicalStatus', {})
            clinical_coding = clinical_status.get('coding', [{}])[0]
            clinical_code = clinical_coding.get('code', 'N/A')
            print(f"📊 Clinical Status: {clinical_code}")
            
            # Verification Status
            verification_status = resource.get('verificationStatus', {})
            verification_coding = verification_status.get('coding', [{}])[0]
            verification_code = verification_coding.get('code', 'N/A')
            print(f"✓ Verification Status: {verification_code}")
            
            # Codes (ICD-11, Traditional Medicine)
            code = resource.get('code', {})
            codings = code.get('coding', [])
            
            if codings:
                print(f"\n💊 Diagnosis Codes:")
                for coding in codings:
                    system = coding.get('system', 'N/A')
                    code_value = coding.get('code', 'N/A')
                    display = coding.get('display', 'N/A')
                    
                    # Identify the system
                    if 'icd-11' in system.lower():
                        system_name = "ICD-11"
                    elif 'traditional-medicine' in system.lower():
                        system_name = "Traditional Medicine"
                    else:
                        system_name = system
                    
                    print(f"   • {system_name}: {code_value}")
                    print(f"     Display: {display}")
            
            # Text description
            code_text = code.get('text', '')
            if code_text:
                print(f"\n📝 Description: {code_text}")
            
            # Recorded Date
            recorded_date = resource.get('recordedDate', 'N/A')
            if recorded_date != 'N/A':
                try:
                    dt = datetime.fromisoformat(recorded_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"📅 Recorded: {formatted_date}")
                except:
                    print(f"📅 Recorded: {recorded_date}")
            
            # Notes
            notes = resource.get('note', [])
            if notes:
                print(f"\n📌 Notes:")
                for note in notes:
                    note_text = note.get('text', '')
                    if note_text:
                        print(f"   {note_text}")
            
            # Full JSON (optional)
            print(f"\n🔍 View full JSON:")
            print(f"   {BAHMNI_URL}/openmrs/ws/fhir2/R4/Condition/{resource_id}")
        
        print("\n" + "=" * 80)
        print(f"✅ Total Conditions: {total}")
        print("=" * 80)
    else:
        print("\n⚠️  No conditions found in the EMR")
        print("   Try sending a condition from your web interface first")
else:
    print(f"   ❌ Failed to fetch conditions: {response.status_code}")
    print(f"   Error: {response.text}")

# Summary
print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print(f"Bahmni URL: {BAHMNI_URL}")
print(f"FHIR API: {fhir_url}")
print(f"Total Conditions: {total if response.status_code == 200 else 'N/A'}")

print("\n💡 To view in Bahmni Web Interface:")
print("   1. Open: http://localhost")
print("   2. Login: superman / Admin123")
print("   3. Go to: Clinical → Patient Dashboard")
print("   4. Select a patient to view their conditions")

print("\n🔗 Direct FHIR API Access:")
print(f"   GET {fhir_url}")
print(f"   Authorization: Basic (superman / Admin123)")

print("\n✨ Done!")
