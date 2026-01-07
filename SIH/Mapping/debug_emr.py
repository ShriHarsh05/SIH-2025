"""
Debug EMR - Check what's actually in Bahmni
"""

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BAHMNI_URL = "http://localhost"
USERNAME = "superman"
PASSWORD = "Admin123"

print("🔍 Debugging Bahmni EMR\n")

# Test 1: Check if we can access FHIR API
print("1. Testing FHIR API access...")
response = requests.get(
    f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/metadata",
    auth=(USERNAME, PASSWORD),
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ FHIR API is accessible")
else:
    print(f"   ❌ Error: {response.text[:200]}")

# Test 2: Check Condition endpoint with different parameters
print("\n2. Checking Condition endpoint...")
response = requests.get(
    f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Condition?_summary=count",
    auth=(USERNAME, PASSWORD),
    headers={'Accept': 'application/fhir+json'},
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Total: {data.get('total', 0)}")
    print(f"   Response: {json.dumps(data, indent=2)[:500]}")

# Test 3: Check for Patient 1
print("\n3. Checking Patient 1...")
response = requests.get(
    f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Patient/1",
    auth=(USERNAME, PASSWORD),
    headers={'Accept': 'application/fhir+json'},
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    patient = response.json()
    print(f"   ✅ Patient exists: {patient.get('name', [{}])[0].get('text', 'N/A')}")
elif response.status_code == 404:
    print("   ⚠️  Patient 1 not found - this might be why conditions aren't showing")
else:
    print(f"   Error: {response.text[:200]}")

# Test 4: List all patients
print("\n4. Listing all patients...")
response = requests.get(
    f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Patient?_summary=count",
    auth=(USERNAME, PASSWORD),
    headers={'Accept': 'application/fhir+json'},
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    total = data.get('total', 0)
    print(f"   Total patients: {total}")
    
    if total > 0:
        # Get first few patients
        response2 = requests.get(
            f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Patient?_count=5",
            auth=(USERNAME, PASSWORD),
            headers={'Accept': 'application/fhir+json'},
            verify=False
        )
        if response2.status_code == 200:
            bundle = response2.json()
            entries = bundle.get('entry', [])
            print(f"\n   First {len(entries)} patients:")
            for entry in entries:
                resource = entry.get('resource', {})
                patient_id = resource.get('id', 'N/A')
                names = resource.get('name', [{}])
                name = names[0].get('text', 'N/A') if names else 'N/A'
                print(f"   - ID: {patient_id}, Name: {name}")

# Test 5: Try to get conditions for any patient
print("\n5. Checking conditions for all patients...")
response = requests.get(
    f"{BAHMNI_URL}/openmrs/ws/fhir2/R4/Condition",
    auth=(USERNAME, PASSWORD),
    headers={'Accept': 'application/fhir+json'},
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    total = data.get('total', 0)
    print(f"   Total conditions: {total}")
    
    if total > 0:
        entries = data.get('entry', [])
        print(f"\n   Conditions found:")
        for entry in entries:
            resource = entry.get('resource', {})
            condition_id = resource.get('id', 'N/A')
            code = resource.get('code', {})
            text = code.get('text', 'N/A')
            print(f"   - ID: {condition_id}")
            print(f"     Text: {text}")
            print(f"     Patient: {resource.get('subject', {}).get('reference', 'N/A')}")

print("\n" + "="*60)
print("💡 Recommendations:")
print("="*60)

# Check if patient exists
if response.status_code == 404:
    print("1. Patient 1 doesn't exist. Create a patient first:")
    print("   - Go to http://localhost")
    print("   - Click 'Advanced' to bypass SSL warning")
    print("   - Login: superman / Admin123")
    print("   - Go to Registration → Create New Patient")
    print("   - Note the Patient ID")
    print("   - Update your code to use that Patient ID")
else:
    print("1. Try sending a condition again from your web interface")
    print("2. Check the browser console for any errors")
    print("3. Verify the FHIR Condition was created successfully")

print("\n✨ Debug complete!")
