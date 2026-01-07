"""Test SK62 Entity ID lookup"""

from icd11_fhir_pipeline import ICD11FHIRPipeline

CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='

pipeline = ICD11FHIRPipeline(CLIENT_ID, CLIENT_SECRET)

print("Testing SK62 lookup...")
try:
    result = pipeline.search_icd11_code("SK62")
    if result:
        print(f"✓ Found: {result}")
    else:
        print("✗ Not found in WHO API")
except Exception as e:
    print(f"✗ Error: {e}")
