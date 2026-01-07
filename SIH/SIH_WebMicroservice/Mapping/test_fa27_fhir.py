"""Test FHIR generation with FA27.2"""

import json
from fhir_generator import generate_fhir_from_mapping

# Example mapping result with FA27.2
example_mapping = {
    "input": "Patient has joint pain",
    "system": "ayurveda",
    "ayurveda_candidates": [{
        "code": "SP42",
        "term": "pRuShTha-grahaH",
        "english": "Lumbar spondylosis disorder",
        "definition": "Backache with stiffness",
        "score": 0.8542
    }],
    "icd11_standard_candidates": [{
        "code": "FA27.2",
        "title": "Palindromic rheumatism",
        "definition": "Palindromic rheumatism definition",
        "score": 0.8937
    }],
    "icd11_tm2_candidates": []
}

print("Generating FHIR Condition with FA27.2...")
print("="*70)

fhir_condition = generate_fhir_from_mapping(
    example_mapping,
    patient_id="test-patient"
)

print("\nChecking FA27.2 coding:")
for coding in fhir_condition['code']['coding']:
    if coding.get('code') == 'FA27.2':
        print(json.dumps(coding, indent=2))
        
        # Check for Entity ID
        has_entity = False
        if 'extension' in coding:
            for ext in coding['extension']:
                if 'entity' in ext.get('url', ''):
                    print(f"\n✓ Entity ID found: {ext.get('valueString')}")
                    has_entity = True
        
        if not has_entity:
            print("\n✗ Entity ID NOT found in extensions")
