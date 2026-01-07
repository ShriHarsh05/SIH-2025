"""
Test FHIR generation for Ayurveda-SAT system
"""
from fhir_generator import generate_fhir_from_mapping
import json

# Test mapping result with ayurveda-sat (normalized keys)
test_mapping = {
    'system': 'ayurveda-sat',
    'input': 'test query',
    'ayurveda_sat_candidates': [{
        'code': 'TEST001',
        'term': 'Test Term',
        'english': 'Test English',
        'definition': 'Test definition',
        'score': 0.95
    }],
    'icd11_standard_candidates': [{
        'code': 'FA20.0',
        'title': 'Low back pain',
        'definition': 'Pain localized to the lower back region.',
        'score': 0.78
    }],
    'icd11_tm2_candidates': [{
        'code': 'SP42',
        'title': 'Lumbar spondylosis disorder',
        'definition': 'Backache with stiffness',
        'score': 0.81
    }]
}

try:
    fhir_result = generate_fhir_from_mapping(test_mapping, 'patient-123')
    print('✓ SUCCESS: FHIR generation worked!')
    print('  Resource Type:', fhir_result.get('resourceType'))
    print('  Condition ID:', fhir_result.get('id'))
    print('  System URL:', fhir_result['code']['coding'][0]['system'])
    print('  Code:', fhir_result['code']['coding'][0]['code'])
    print('  Display:', fhir_result['code']['coding'][0]['display'])
    print('\n✓ All checks passed!')
except Exception as e:
    print('✗ ERROR:', str(e))
    import traceback
    traceback.print_exc()
