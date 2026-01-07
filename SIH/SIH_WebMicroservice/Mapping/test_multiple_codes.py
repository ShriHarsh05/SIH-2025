"""Test multiple ICD-11 codes"""

from icd11_fhir_pipeline import ICD11FHIRPipeline
import json

CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='

pipeline = ICD11FHIRPipeline(CLIENT_ID, CLIENT_SECRET)

test_codes = ["1A00", "2560", "FA20.0", "1A01"]

for code in test_codes:
    print(f"\n{'='*60}")
    print(f"Testing: {code}")
    print('='*60)
    try:
        result = pipeline.process_code(code)
        concept = result['concept'][0]
        print(f"✓ Code: {concept['code']}")
        print(f"✓ Disease: {concept['display']}")
        print(f"✓ Entity ID: {concept['extension'][0]['valueString']}")
    except Exception as e:
        print(f"✗ Error: {e}")
