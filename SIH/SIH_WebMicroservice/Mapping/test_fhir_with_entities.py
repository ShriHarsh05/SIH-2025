"""Test FHIR generation with Entity IDs"""

import json
from fhir_generator import generate_fhir_from_mapping

# Example mapping result with ICD-11 codes
example_mapping = {
    "input": "Patient has severe headache and fever",
    "system": "siddha",
    "siddha_candidates": [{
        "code": "KHA",
        "term": "Vaḷi",
        "english": "Vali disorder",
        "definition": "Disorder related to Vali (wind element)",
        "score": 0.8542
    }],
    "icd11_standard_candidates": [{
        "code": "1A00",
        "title": "Cholera",
        "definition": "Cholera is an infection of the small intestine",
        "score": 0.7823
    }],
    "icd11_tm2_candidates": [{
        "code": "SK62",
        "title": "Blepharitis disorder (TM2)",
        "definition": "hard swelling and redness in eyelids",
        "score": 0.8123
    }]
}

print("Generating FHIR Condition with Entity IDs...")
print("="*70)

fhir_condition = generate_fhir_from_mapping(
    example_mapping,
    patient_id="b4f7d426-7471-4e9d-a204-64441b18a147"
)

print("\nFHIR Condition Resource:")
print(json.dumps(fhir_condition, indent=2))

# Check for Entity IDs
print("\n" + "="*70)
print("Checking for Entity IDs in codings:")
print("="*70)

for coding in fhir_condition['code']['coding']:
    system = coding.get('system', '')
    code = coding.get('code', '')
    display = coding.get('display', '')
    
    print(f"\nSystem: {system}")
    print(f"Code: {code}")
    print(f"Display: {display}")
    
    if 'extension' in coding:
        for ext in coding['extension']:
            if 'entity' in ext.get('url', ''):
                entity_id = ext.get('valueString', 'N/A')
                print(f"✓ Entity ID: {entity_id}")
