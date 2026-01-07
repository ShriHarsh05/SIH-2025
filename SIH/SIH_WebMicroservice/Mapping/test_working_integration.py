"""
Test the working Bahmni integration
"""

from emr_integration_working import BahmniIntegration

print("=" * 70)
print("🧪 Testing Working Bahmni Integration")
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
    tm_system="Ayurveda",
    tm_code="AY-FEVER-001",
    tm_term="Jwara (Fever disorder)"
)

print("\n" + "=" * 70)
if result.get("success"):
    print("✅ SUCCESS! Diagnosis sent to Bahmni!")
    print("=" * 70)
    print(f"\n📋 Details:")
    print(f"   Observation UUID: {result.get('observation_uuid')}")
    print(f"   Visit UUID: {result.get('visit_uuid')}")
    print(f"   Diagnosis: {result.get('diagnosis')}")
    
    print(f"\n🌐 View in Bahmni:")
    print(f"   1. Go to: http://localhost")
    print(f"   2. Login: superman / Admin123")
    print(f"   3. Click 'Clinical' → 'Search Patient'")
    print(f"   4. Search for patient (ABC200000 or Test Patient)")
    print(f"   5. Look in 'Diagnoses' section - you should see it!")
    
    print(f"\n✨ The diagnosis will appear in the Bahmni UI!")
else:
    print("❌ FAILED")
    print("=" * 70)
    print(f"Error: {result.get('error')}")
    print(f"\nTroubleshooting:")
    print(f"1. Make sure Bahmni is running")
    print(f"2. Check patient UUID is correct")
    print(f"3. Verify credentials")

print("\n" + "=" * 70)
print("Test complete!")
