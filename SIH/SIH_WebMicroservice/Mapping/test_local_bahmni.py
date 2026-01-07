"""
Test script for Local Bahmni Integration
Run this after Bahmni containers are fully started (5-10 minutes)
"""

import time
import requests
import urllib3
from emr_integration import BahmniIntegration
from datetime import datetime

# Disable SSL warnings for local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 60)
print("🏥 Testing Local Bahmni Integration")
print("=" * 60)

# Check if Bahmni is accessible
print("\n1. Checking if Bahmni is accessible...")
print("   URL: http://localhost")

try:
    response = requests.get("http://localhost", timeout=10, verify=False)
    if response.status_code == 200:
        print("   ✅ Bahmni web interface is accessible")
    else:
        print(f"   ⚠️  Got status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to Bahmni")
    print("   💡 Make sure Bahmni containers are running:")
    print("      cd bahmni-docker/bahmni-lite")
    print("      docker compose ps")
    print("\n   ⏳ If containers are running, wait 5-10 minutes for initialization")
    exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Check OpenMRS API
print("\n2. Checking OpenMRS API...")
try:
    response = requests.get(
        "http://localhost/openmrs/ws/rest/v1/session",
        auth=("superman", "Admin123"),
        timeout=10,
        verify=False
    )
    if response.status_code == 200:
        print("   ✅ OpenMRS API is responding")
        session_data = response.json()
        print(f"   User: {session_data.get('user', {}).get('display', 'N/A')}")
    else:
        print(f"   ⚠️  API returned status: {response.status_code}")
        print("   💡 OpenMRS might still be initializing, wait a few more minutes")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   💡 OpenMRS is still starting up, please wait...")
    exit(1)

# Connect to Bahmni
print("\n3. Connecting to Local Bahmni...")
try:
    bahmni = BahmniIntegration(
        base_url="http://localhost",
        username="superman",
        password="Admin123"
    )
    print("   ✅ Connected successfully!")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    exit(1)

# Create test FHIR resource
print("\n4. Creating FHIR Condition resource...")

test_fhir = {
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
    "category": [{
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
            "code": "encounter-diagnosis",
            "display": "Encounter Diagnosis"
        }]
    }],
    "code": {
        "coding": [
            {
                "system": "http://hl7.org/fhir/sid/icd-11",
                "code": "SP42",
                "display": "Lumbar spondylosis disorder"
            }
        ],
        "text": "Siddha: SP42 - Lumbar spondylosis disorder (Traditional Medicine Mapping)"
    },
    "subject": {
        "reference": "Patient/1",
        "display": "Test Patient"
    },
    "recordedDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "note": [{
        "text": "Mapped from Traditional Medicine (Siddha) to ICD-11 using AI-powered hybrid retrieval system. Local Bahmni Integration Test."
    }]
}

print("   ✅ FHIR resource created")
print(f"   Code: {test_fhir['code']['coding'][0]['code']}")
print(f"   Display: {test_fhir['code']['coding'][0]['display']}")

# Send to Bahmni
print("\n5. Sending to Local Bahmni EMR...")
print("   This may take a moment...")

try:
    result = bahmni.send_fhir_condition(test_fhir)
    
    if "error" in result:
        print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        if result.get('status_code') == 401:
            print("   💡 Authentication issue - check credentials")
        elif result.get('status_code') == 404:
            print("   💡 FHIR endpoint not found - OpenMRS might still be initializing")
        else:
            print("   💡 Check Bahmni logs: docker compose logs openmrs-1")
    else:
        print("   ✅ Successfully sent to Bahmni!")
        print(f"   Resource ID: {result.get('id', 'N/A')}")
        print("\n6. View in Bahmni:")
        print("   1. Open: http://localhost")
        print("   2. Login: superman / Admin123")
        print("   3. Navigate to: Clinical → Patient Dashboard")
        print("   4. Select a patient to see conditions")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   💡 Make sure OpenMRS is fully initialized")

print("\n" + "=" * 60)
print("✅ Test Complete!")
print("=" * 60)

print("\n📊 Summary:")
print("- Bahmni Web: http://localhost")
print("- OpenMRS Admin: http://localhost/openmrs")
print("- FHIR API: http://localhost/openmrs/ws/fhir2/R4/")
print("- Credentials: superman / Admin123")

print("\n💡 Next Steps:")
print("1. If test failed, wait 5-10 minutes and try again")
print("2. Check container logs: docker compose logs -f")
print("3. Once working, integrate with your main application")
print("4. Update .env with: EMR_URL=http://localhost")

print("\n🎉 Your local Bahmni EMR is ready for integration!")
