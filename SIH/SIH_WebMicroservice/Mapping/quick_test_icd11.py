"""Quick test of ICD-11 pipeline"""

from icd11_fhir_pipeline import ICD11FHIRPipeline
import json

CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='

pipeline = ICD11FHIRPipeline(CLIENT_ID, CLIENT_SECRET)

print("Testing ICD-11 code: 1A00")
result = pipeline.process_code("1A00")
print(json.dumps(result, indent=2))
