"""
Test the new Observation-based integration
"""

from emr_integration_obs import BahmniIntegration

print("=" * 70)
print("🧪 Testing Observation-based Bahmni Integration")
print("=" * 70)

# Connect to Bahmni
print("\n1. Connecting to Bahmni...")
bahmni = BahmniIntegration(
    base_url="http://localhost",
    username="superman",
    password="Admin123"
)

# Send a test diagnosis
print("\n2. Sending test diagnosis...")
patient_uuid = "b4f7d426-7471-4e9d-a204-64441b18a147"

result = bahmni.send_diagnosis(
    patient_uuid=patient_uuid,
    icd11_code="CA40.Z",
    icd11_display="Malaria, unspecified",
    tm_system="ayurveda",
    tm_code="AY-FEVER-001",
    tm_term="Jwara (Fever disorder)"
)

if result.get("success"):
    print("\n✅ SUCCESS!")
    print(f"   Observation UUID: {result.get('observation_uuid')}")
    print(f"   Encounter UUID: {result.get('encounter_uuid')}")
    print(f"   Diagnosis: {result.get('diagnosis')}")
    
    print("\n🌐 View in Bahmni:")
    print("   1. Go to: http://localhost")
    print("   2. Login: superman / Admin123")
    print("   3. Search for patient")
    print("   4. Check 'Treatments' or 'Observations' section")
else:
    print(f"\n❌ Failed: {result.get('error')}")

print("\n✨ Test complete!")
