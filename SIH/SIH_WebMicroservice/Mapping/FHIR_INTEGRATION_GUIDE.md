# FHIR Integration Guide for Bahmni EMR

## Overview
This system generates FHIR R4 Condition resources compatible with Bahmni EMR, including Traditional Medicine diagnoses and ICD-11 mappings.

## Features

### ✅ FHIR R4 Compliance
- Fully compliant with FHIR R4 specification
- Validated against HL7 FHIR StructureDefinition
- Compatible with Bahmni EMR and OpenMRS

### ✅ Comprehensive Coding
- **Traditional Medicine:** Siddha, Ayurveda, Unani codes
- **ICD-11 Standard:** WHO ICD-11 MMS codes
- **ICD-11 TM2:** Traditional Medicine Module 2 codes
- **Confidence Scores:** AI-generated mapping confidence

### ✅ Rich Metadata
- Original terminology preserved
- English translations included
- Full definitions embedded
- Mapping evidence with scores

## FHIR Condition Resource Structure

### Basic Structure
```json
{
  "resourceType": "Condition",
  "id": "uuid",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2024-01-01T00:00:00Z",
    "profile": ["http://hl7.org/fhir/StructureDefinition/Condition"]
  },
  "clinicalStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
      "code": "active"
    }]
  },
  "verificationStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
      "code": "confirmed"
    }]
  },
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-category",
      "code": "encounter-diagnosis"
    }]
  }],
  "code": {
    "coding": [
      {
        "system": "http://who.int/icd/tm2/ayurveda",
        "code": "SP42",
        "display": "Lumbar spondylosis disorder"
      },
      {
        "system": "http://id.who.int/icd/release/11/mms",
        "code": "FA20.0",
        "display": "Low back pain"
      },
      {
        "system": "http://id.who.int/icd/release/11/tm2",
        "code": "SP42",
        "display": "Lumbar spondylosis disorder (TM2)"
      }
    ]
  },
  "subject": {
    "reference": "Patient/patient-123"
  },
  "encounter": {
    "reference": "Encounter/encounter-456"
  },
  "recordedDate": "2024-01-01T00:00:00Z"
}
```

## Code Systems Used

### Traditional Medicine Systems
| System | URL | Example Code |
|--------|-----|--------------|
| Siddha | `http://who.int/icd/tm2/siddha` | SBB3 |
| Ayurveda | `http://who.int/icd/tm2/ayurveda` | SP42 |
| Unani | `http://who.int/icd/tm2/unani` | A-1 |

### ICD-11 Systems
| System | URL | Example Code |
|--------|-----|--------------|
| ICD-11 Standard | `http://id.who.int/icd/release/11/mms` | FA20.0 |
| ICD-11 TM2 | `http://id.who.int/icd/release/11/tm2` | SP42 |

## API Endpoints

### 1. Generate Single FHIR Condition

**Endpoint:** `POST /fhir/condition`

**Request Body:**
```json
{
  "mapping_result": {
    "system": "ayurveda",
    "ayurveda_candidates": [{
      "code": "SP42",
      "term": "pRuShTha-grahaH",
      "english": "Lumbar spondylosis disorder",
      "definition": "It is characterised by backache...",
      "score": 0.8542
    }],
    "icd11_standard_candidates": [{
      "code": "FA20.0",
      "title": "Low back pain",
      "definition": "Pain localized to the lower back...",
      "score": 0.7823
    }],
    "icd11_tm2_candidates": [{
      "code": "SP42",
      "title": "Lumbar spondylosis disorder (TM2)",
      "definition": "It is characterised by backache...",
      "score": 0.8123
    }]
  },
  "patient_id": "patient-123",
  "encounter_id": "encounter-456",
  "practitioner_id": "practitioner-789"
}
```

**Response:** FHIR Condition resource (see structure above)

### 2. Generate FHIR Bundle

**Endpoint:** `POST /fhir/bundle`

**Request Body:**
```json
{
  "mapping_results": [
    { /* mapping result 1 */ },
    { /* mapping result 2 */ }
  ],
  "patient_id": "patient-123",
  "encounter_id": "encounter-456",
  "practitioner_id": "practitioner-789"
}
```

**Response:** FHIR Bundle resource containing multiple Conditions

## Frontend Integration

### Export Button
The UI includes an "Export as FHIR JSON" button that:
1. Generates FHIR Condition from current mapping
2. Downloads JSON file
3. Displays formatted JSON in modal
4. Provides copy-to-clipboard functionality

### Usage Flow
```
1. User searches for symptoms
2. System returns TM candidates
3. User clicks candidate
4. System shows ICD mappings
5. User clicks "Export as FHIR JSON"
6. FHIR Condition is generated and downloaded
```

## Bahmni EMR Integration

### Import into Bahmni

#### Option 1: REST API
```bash
curl -X POST \
  http://bahmni-server/openmrs/ws/fhir2/R4/Condition \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Basic <credentials>' \
  -d @fhir-condition.json
```

#### Option 2: Bahmni Connect App
1. Export FHIR JSON from our system
2. Import via Bahmni Connect mobile app
3. Sync with Bahmni server

#### Option 3: Batch Upload
```bash
curl -X POST \
  http://bahmni-server/openmrs/ws/fhir2/R4 \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Basic <credentials>' \
  -d @fhir-bundle.json
```

### Bahmni Configuration

Add to `clinical_config.json`:
```json
{
  "diagnosisStatus": "Confirmed",
  "codingSystems": [
    {
      "name": "ICD-11",
      "url": "http://id.who.int/icd/release/11/mms"
    },
    {
      "name": "ICD-11 TM2",
      "url": "http://id.who.int/icd/release/11/tm2"
    },
    {
      "name": "Ayurveda",
      "url": "http://who.int/icd/tm2/ayurveda"
    },
    {
      "name": "Siddha",
      "url": "http://who.int/icd/tm2/siddha"
    },
    {
      "name": "Unani",
      "url": "http://who.int/icd/tm2/unani"
    }
  ]
}
```

## Python Usage

### Generate FHIR from Mapping Result

```python
from fhir_generator import generate_fhir_from_mapping
from build_indexes.mapper import map_to_icd

# Get mapping result
mapping_result = map_to_icd("joint pain", system="ayurveda")

# Generate FHIR Condition
fhir_condition = generate_fhir_from_mapping(
    mapping_result=mapping_result,
    patient_id="patient-123",
    encounter_id="encounter-456",
    practitioner_id="practitioner-789"
)

# Save to file
import json
with open("condition.json", "w") as f:
    json.dump(fhir_condition, f, indent=2)
```

### Generate FHIR Bundle

```python
from fhir_generator import generate_fhir_bundle_from_mappings

# Multiple mapping results
mapping_results = [
    map_to_icd("headache", system="ayurveda"),
    map_to_icd("fever", system="ayurveda")
]

# Generate bundle
fhir_bundle = generate_fhir_bundle_from_mappings(
    mapping_results=mapping_results,
    patient_id="patient-123",
    encounter_id="encounter-456"
)

# Save to file
with open("bundle.json", "w") as f:
    json.dump(fhir_bundle, f, indent=2)
```

## FHIR Resource Elements

### Clinical Status
- `active`: Condition is currently active
- `recurrence`: Condition has recurred
- `relapse`: Condition has relapsed
- `inactive`: Condition is no longer active
- `remission`: Condition is in remission
- `resolved`: Condition has been resolved

### Verification Status
- `unconfirmed`: Not yet confirmed
- `provisional`: Provisional diagnosis
- `differential`: One of a set of potential diagnoses
- `confirmed`: Confirmed diagnosis (default)
- `refuted`: Diagnosis has been refuted
- `entered-in-error`: Entered in error

### Category
- `encounter-diagnosis`: Diagnosis made during encounter
- `problem-list-item`: Item on problem list

## Confidence Scores

Mapping confidence scores are included as extensions:
```json
{
  "extension": [{
    "url": "http://example.org/fhir/StructureDefinition/mapping-confidence",
    "valueDecimal": 0.8542
  }]
}
```

**Score Interpretation:**
- `0.9 - 1.0`: Excellent match
- `0.8 - 0.9`: Good match
- `0.7 - 0.8`: Fair match
- `< 0.7`: Review recommended

## Evidence Element

The evidence element contains ICD mappings with confidence:
```json
{
  "evidence": [
    {
      "code": [{
        "coding": [{
          "system": "http://id.who.int/icd/release/11/mms",
          "code": "FA20.0",
          "display": "Low back pain"
        }],
        "text": "ICD-11 Standard mapping (confidence: 0.7823)"
      }]
    }
  ]
}
```

## Notes Element

Definitions are stored in the notes element:
```json
{
  "note": [
    {
      "text": "Traditional Medicine Definition: It is characterised by..."
    },
    {
      "text": "ICD-11 Standard Definition: Pain localized to..."
    },
    {
      "text": "ICD-11 TM2 Definition: It is characterised by..."
    }
  ]
}
```

## Validation

### FHIR Validator
Validate generated resources:
```bash
java -jar validator_cli.jar condition.json -version 4.0
```

### Online Validation
- https://www.hl7.org/fhir/validator/
- Upload generated JSON for validation

## Testing

### Test FHIR Generation
```bash
cd Mapping
python fhir_generator.py
```

### Test API Endpoint
```bash
curl -X POST http://localhost:8000/fhir/condition \
  -H "Content-Type: application/json" \
  -d @test_mapping.json
```

## Troubleshooting

### Issue: Invalid FHIR Resource
**Solution:** Ensure all required fields are present:
- resourceType
- id
- code
- subject

### Issue: Bahmni Import Fails
**Solution:** Check:
- Patient ID exists in Bahmni
- Encounter ID is valid
- Code systems are configured

### Issue: Missing Confidence Scores
**Solution:** Ensure mapping result includes score field

## Best Practices

### 1. Patient Identification
- Use consistent patient IDs across systems
- Validate patient exists before generating FHIR

### 2. Encounter Context
- Always link to encounter when available
- Maintains clinical context

### 3. Code System URLs
- Use official WHO URLs for ICD-11
- Maintain consistent TM system URLs

### 4. Confidence Thresholds
- Set minimum confidence for auto-import
- Flag low-confidence mappings for review

### 5. Batch Processing
- Use bundles for multiple conditions
- Reduces API calls to Bahmni

## Future Enhancements

- [ ] FHIR Observation resources for symptoms
- [ ] FHIR Procedure resources for treatments
- [ ] FHIR MedicationRequest for prescriptions
- [ ] FHIR DiagnosticReport for test results
- [ ] Real-time sync with Bahmni
- [ ] FHIR Questionnaire for symptom collection

## References

- [FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [FHIR Condition Resource](https://hl7.org/fhir/R4/condition.html)
- [Bahmni Documentation](https://bahmni.atlassian.net/wiki/spaces/BAH/overview)
- [ICD-11 Coding Tool](https://icd.who.int/browse11)
- [WHO Traditional Medicine Module](https://www.who.int/standards/classifications/other-classifications/international-classification-of-traditional-medicine)
