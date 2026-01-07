# ICD-11 to FHIR CodeSystem Pipeline

## Overview

This pipeline converts ICD-11 codes to FHIR-compliant CodeSystem JSON format with Entity IDs from the WHO ICD-11 API.

## Pipeline Flow

```
Input: ICD-11 Code (e.g., "1A00")
    ↓
Step 1: Authenticate with WHO ICD-11 API (OAuth2)
    ↓
Step 2: Search for code via WHO API
    ↓
Step 3: Extract code, disease name, and Entity ID
    ↓
Step 4: Build FHIR CodeSystem JSON
    ↓
Output: FHIR-compliant CodeSystem resource
```

## Input/Output Example

### Input
```
ICD-11 Code: "1A00"
```

### Output
```json
{
  "resourceType": "CodeSystem",
  "status": "active",
  "content": "complete",
  "concept": [
    {
      "code": "1A00",
      "display": "Cholera",
      "extension": [
        {
          "url": "http://id.who.int/icd/entity",
          "valueString": "257068234"
        }
      ]
    }
  ]
}
```

## API Endpoints

### 1. POST /icd11/to-fhir

Convert ICD-11 code to FHIR CodeSystem (POST method)

**Request:**
```bash
curl -X POST http://localhost:8000/icd11/to-fhir \
  -H "Content-Type: application/json" \
  -d '{"code": "1A00"}'
```

**Response:**
```json
{
  "resourceType": "CodeSystem",
  "status": "active",
  "content": "complete",
  "concept": [
    {
      "code": "1A00",
      "display": "Cholera",
      "extension": [
        {
          "url": "http://id.who.int/icd/entity",
          "valueString": "257068234"
        }
      ]
    }
  ]
}
```

### 2. GET /icd11/to-fhir/{code}

Convert ICD-11 code to FHIR CodeSystem (GET method)

**Request:**
```bash
curl http://localhost:8000/icd11/to-fhir/1A00
```

**Response:** Same as POST method

## Python Usage

### Direct Pipeline Usage

```python
from icd11_fhir_pipeline import ICD11FHIRPipeline

# Initialize with WHO credentials
CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'

pipeline = ICD11FHIRPipeline(CLIENT_ID, CLIENT_SECRET)

# Process a code
result = pipeline.process_code("1A00")

print(result)
# Output: FHIR CodeSystem JSON
```

### Convenience Function

```python
from icd11_fhir_pipeline import icd11_to_fhir

result = icd11_to_fhir(
    code="1A00",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

## Testing

### Run Test Suite

```bash
cd SIH/Mapping
python test_icd11_pipeline.py
```

This will test multiple ICD-11 codes and display results.

### Test with Server Running

1. Start the server:
```bash
uvicorn api.server:app --reload
```

2. Test POST endpoint:
```bash
curl -X POST http://localhost:8000/icd11/to-fhir \
  -H "Content-Type: application/json" \
  -d '{"code": "1A00"}'
```

3. Test GET endpoint:
```bash
curl http://localhost:8000/icd11/to-fhir/1A00
```

## WHO ICD-11 API Details

### Authentication
- **Token URL:** `https://icdaccessmanagement.who.int/connect/token`
- **Grant Type:** `client_credentials`
- **Scope:** `icdapi_access`

### Search Endpoint
- **URL:** `https://id.who.int/icd/release/11/2024-01/mms/search`
- **Method:** GET
- **Parameters:** `q` (search query)

### Response Structure
```json
{
  "destinationEntities": [
    {
      "id": "http://id.who.int/icd/entity/257068234",
      "theCode": "1A00",
      "title": {
        "@value": "Cholera"
      }
    }
  ]
}
```

## FHIR CodeSystem Structure

The output follows HL7 FHIR R4 CodeSystem specification:

- **resourceType:** Always "CodeSystem"
- **status:** "active" (indicates the CodeSystem is ready for use)
- **content:** "complete" (all concepts are included)
- **concept:** Array of concept definitions
  - **code:** ICD-11 code
  - **display:** Disease name
  - **extension:** Custom extension for Entity ID
    - **url:** `http://id.who.int/icd/entity`
    - **valueString:** Entity ID (numeric identifier)

## Error Handling

### Code Not Found
```json
{
  "error": "ICD-11 code 'INVALID' not found",
  "code": "INVALID",
  "message": "ICD-11 code not found or invalid"
}
```

### API Error
```json
{
  "error": "Connection timeout",
  "code": "1A00",
  "message": "Error processing ICD-11 code"
}
```

## Integration with Existing System

The pipeline is integrated into your FastAPI server at `api/server.py`:

1. **Import:** `from icd11_fhir_pipeline import ICD11FHIRPipeline`
2. **Initialize:** Pipeline initialized on server startup with WHO credentials
3. **Endpoints:** Two endpoints added (POST and GET)
4. **Health Check:** Updated to include ICD-11 pipeline status

## Credentials

WHO ICD-11 API credentials are configured in:
- `icd11_fhir_pipeline.py` (for standalone use)
- `api/server.py` (for API integration)

```python
CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='
```

## Use Cases

1. **Validate ICD-11 Codes:** Verify that a code exists in WHO database
2. **Get Disease Names:** Retrieve official disease names for codes
3. **Extract Entity IDs:** Get WHO Entity IDs for further API queries
4. **FHIR Integration:** Generate FHIR-compliant resources for EMR systems
5. **Code Lookup:** Quick lookup of ICD-11 code details

## Performance

- **Token Caching:** OAuth2 token is cached to avoid repeated authentication
- **Response Time:** Typically 200-500ms per code lookup
- **Rate Limits:** Subject to WHO API rate limits (check WHO documentation)

## Next Steps

1. **Batch Processing:** Add endpoint to process multiple codes at once
2. **Caching:** Implement Redis cache for frequently accessed codes
3. **Extended Data:** Add more ICD-11 fields (synonyms, parent codes, etc.)
4. **UI Integration:** Add ICD-11 lookup to the web interface

## Support

For issues or questions:
1. Check WHO ICD-11 API documentation: https://icd.who.int/icdapi
2. Verify credentials are valid
3. Check server logs for detailed error messages
4. Test with known valid codes (e.g., "1A00", "1A01")
