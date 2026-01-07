# Traditional Medicine to ICD-11 Mapping System

A comprehensive system for mapping Traditional Medicine (Siddha, Ayurveda, Unani) diagnoses to ICD-11 codes with FHIR R4 integration for Electronic Medical Records (EMR).

## Overview

This system enables healthcare practitioners to:
- Search and select Traditional Medicine diagnoses
- Automatically map to ICD-11 Standard and ICD-11 TM2 codes
- Generate FHIR R4 Condition resources with WHO Entity IDs
- Send diagnoses to HAPI FHIR EMR systems
- View and manage patient conditions

## Features

- **Multi-System Support**: Siddha, Ayurveda, and Unani medicine systems
- **Hybrid Search**: BM25 + semantic search using sentence transformers
- **ICD-11 Mapping**: Automatic mapping to both Standard (MMS) and TM2 modules
- **Entity ID Integration**: Fetches WHO ICD-11 Entity IDs via OAuth2 API
- **FHIR R4 Compliant**: Generates valid FHIR Condition resources
- **EMR Integration**: Direct integration with HAPI FHIR servers
- **Web Interface**: User-friendly UI for searching and mapping
- **EMR Viewer**: View all stored conditions with detailed information

## Architecture

```
User Input (Symptoms/Diagnosis)
    ↓
Traditional Medicine Search (BM25 + Semantic)
    ↓
ICD-11 Mapping (Standard + TM2)
    ↓
Entity ID Lookup (WHO API)
    ↓
FHIR Condition Generation
    ↓
HAPI FHIR Storage
    ↓
EMR Viewer Display
```

## Quick Start

### Prerequisites

- Python 3.8+
- HAPI FHIR Server (Docker recommended)
- WHO ICD-11 API credentials (included)

### Installation

1. **Install dependencies:**
   ```bash
   cd SIH/Mapping
   pip install -r requirements.txt
   ```

2. **Build search indexes:**
   ```bash
   python build_indexes/build_indexes_icd.py
   ```

3. **Start HAPI FHIR Server:**
   ```bash
   # Using Docker
   docker run -p 8090:8080 hapiproject/hapi:latest
   ```

4. **Start API Server:**
   ```bash
   uvicorn api.server:app --reload
   ```
   Or double-click: `start_server.bat` (Windows) / `start_server.sh` (Linux/Mac)

5. **Open Web Interface:**
   ```
   http://localhost:8000/ui/index.html
   ```

### Usage

1. **Login:**
   - Email: `demo@example.com`
   - Password: `demo123`

2. **Search for Diagnosis:**
   - Select Traditional Medicine system (Siddha/Ayurveda/Unani)
   - Enter symptoms or diagnosis name
   - Select from suggested candidates

3. **Map to ICD-11:**
   - Click on a Traditional Medicine code
   - System automatically maps to ICD-11 Standard and TM2
   - Select desired ICD-11 codes

4. **Send to EMR:**
   - Click "Send to Bahmni EMR"
   - View success confirmation with Resource ID
   - Access EMR Viewer to see stored conditions

## Project Structure

```
SIH/Mapping/
├── api/                      # FastAPI backend
│   ├── server.py            # Main API server
│   ├── auth_simple.py       # Authentication
│   └── autocomplete.py      # Search autocomplete
├── ui/                       # Web interface
│   ├── index.html           # Main search interface
│   ├── emr_viewer.html      # EMR condition viewer
│   ├── script.js            # Frontend logic
│   └── style.css            # Styling
├── data/                     # Medical terminology data
│   ├── icd11_standard.json  # ICD-11 Standard codes
│   ├── icd11_tm2.json       # ICD-11 TM2 codes
│   ├── siddha_data.json     # Siddha diagnoses
│   ├── ayurveda_data.json   # Ayurveda diagnoses
│   └── unani_data.json      # Unani diagnoses
├── indexes/                  # Pre-built search indexes
├── build_indexes/           # Index building scripts
│   ├── build_indexes_icd.py
│   └── mapper.py            # ICD mapping logic
├── search.py                # Siddha search
├── search_ayurveda.py       # Ayurveda search
├── search_unani.py          # Unani search
├── search_icd.py            # ICD-11 Standard search
├── search_icd_tm2.py        # ICD-11 TM2 search
├── fhir_generator.py        # FHIR resource generation
├── icd11_fhir_pipeline.py   # WHO API integration
├── emr_integration_hapi.py  # HAPI FHIR integration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Endpoints

### Search & Mapping
- `POST /map` - Full mapping pipeline
- `POST /map/siddha-code` - Map specific Siddha code to ICD-11
- `POST /map/ayurveda-code` - Map specific Ayurveda code to ICD-11
- `POST /map/unani-code` - Map specific Unani code to ICD-11

### FHIR Generation
- `POST /fhir/condition` - Generate FHIR Condition resource
- `POST /fhir/bundle` - Generate FHIR Bundle

### EMR Integration
- `POST /emr/send` - Send FHIR Condition to EMR

### ICD-11 Entity IDs
- `POST /icd11/to-fhir` - Get Entity ID for ICD-11 code
- `GET /icd11/to-fhir/{code}` - Get Entity ID (GET method)

## Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```env
# WHO ICD-11 API Credentials
ICD11_CLIENT_ID=your_client_id
ICD11_CLIENT_SECRET=your_client_secret

# HAPI FHIR Server
HAPI_FHIR_URL=http://localhost:8090/fhir

# Patient ID (for testing)
DEFAULT_PATIENT_ID=b4f7d426-7471-4e9d-a204-64441b18a147
```

### Authentication

The system uses simple JWT authentication. Default credentials:
- Email: `demo@example.com`
- Password: `demo123`

For production, update credentials in `api/auth_simple.py`.

## FHIR Resource Structure

Generated FHIR Condition resources include:

```json
{
  "resourceType": "Condition",
  "clinicalStatus": {"coding": [{"code": "active"}]},
  "verificationStatus": {"coding": [{"code": "confirmed"}]},
  "code": {
    "coding": [
      {
        "system": "http://hl7.org/fhir/sid/icd-11/mms",
        "code": "FA27.2",
        "display": "Palindromic rheumatism",
        "extension": [{
          "url": "http://id.who.int/icd/entity",
          "valueString": "494875651"
        }]
      },
      {
        "system": "http://terminology.traditional-medicine.org/siddha",
        "code": "KHA",
        "display": "Vaḷi"
      }
    ],
    "text": "Symptoms: joint pain | Diagnosis: Vaḷi | ICD-11: FA27.2"
  },
  "subject": {"reference": "Patient/b4f7d426-7471-4e9d-a204-64441b18a147"}
}
```

## Troubleshooting

### Common Issues

**1. Connection Refused**
- Ensure API server is running: `uvicorn api.server:app --reload`
- Check port 8000 is not in use

**2. HAPI FHIR Not Found**
- Start HAPI FHIR server on port 8090
- Verify: `curl http://localhost:8090/fhir/metadata`

**3. Search Returns No Results**
- Build indexes: `python build_indexes/build_indexes_icd.py`
- Check data files exist in `data/` directory

**4. Entity ID Lookup Fails**
- Verify WHO API credentials in `.env`
- Check internet connection
- WHO API may be rate-limited

### Diagnostic Tools

Run system diagnostic:
```bash
python diagnose_emr.py
```

View EMR conditions:
```bash
python view_emr_conditions.py
```

## Development

### Running Tests

```bash
# Test ICD-11 pipeline
python test_icd11_pipeline.py

# Test FHIR generation
python test_fhir_with_entities.py

# Test EMR integration
python test_hapi_integration.py
```

### Adding New Traditional Medicine Systems

1. Add data file: `data/newsystem_data.json`
2. Create search module: `search_newsystem.py`
3. Update `api/server.py` with new endpoints
4. Add UI option in `ui/index.html`

## Technical Details

### Search Algorithm

1. **BM25 Ranking**: Fast keyword-based search
2. **Semantic Search**: Sentence transformer embeddings (all-MiniLM-L6-v2)
3. **Hybrid Scoring**: Combines both approaches for optimal results

### ICD-11 Integration

- **Standard Module (MMS)**: Foundation codes for mortality/morbidity
- **TM2 Module**: Traditional Medicine specific codes
- **Entity IDs**: Unique WHO identifiers for each concept
- **OAuth2 Authentication**: Secure API access

### FHIR Compliance

- FHIR R4 specification
- HL7 terminology standards
- Bahmni EMR compatible
- HAPI FHIR server tested

## License

[Add your license here]

## Contributors

[Add contributors here]

## Support

For issues and questions:
- Check `docs/TROUBLESHOOTING.md`
- Review API documentation: `http://localhost:8000/docs`
- Run diagnostic: `python diagnose_emr.py`

## Acknowledgments

- WHO ICD-11 API
- HAPI FHIR Project
- Bahmni EMR
- Traditional Medicine terminology sources
