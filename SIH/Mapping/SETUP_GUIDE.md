# Setup Guide - Multi-System Traditional Medicine Mapping

## What Was Done

### 1. Data Extraction ✅
- Created `extract_systems.py` to extract Ayurveda, Unani, and ICD-10 from namaste_data.json
- Generated 3 new JSON files:
  - `ayurveda_data.json` (2,910 entries)
  - `unani_data.json` (2,522 entries)
  - `icd10_data.json` (11,145 entries)

### 2. Build Indexes Scripts ✅
- Created `build_indexes_ayurveda.py` - Builds BM25, TF-IDF, and embeddings for Ayurveda
- Created `build_indexes_unani.py` - Builds BM25, TF-IDF, and embeddings for Unani
- Ayurveda indexes already built ✅
- Unani indexes need to be built (see step 3 below)

### 3. Search Modules ✅
- Created `search_ayurveda.py` - Search pipeline for Ayurveda system
- Created `search_unani.py` - Search pipeline for Unani system
- Both use the same 3-stage retrieval: BM25 → TF-IDF → Semantic

### 4. Frontend Updates ✅
- Added dropdown selector in `index.html` to choose between Siddha/Ayurveda/Unani
- Updated `script.js` to handle system selection dynamically
- Updated `script.css` with styling for the dropdown
- All labels update based on selected system

### 5. Backend API Updates ✅
- Updated `server.py` to support all 3 systems
- Updated `autocomplete.py` to provide autocomplete for all 3 systems
- Added endpoints for each system's diagnose and mapping functions

## Next Steps

### Step 1: Build Unani Indexes
Run this in your myenv environment:
```bash
cd Mapping/build_indexes
python build_indexes_unani.py
```

### Step 2: Test the System
Start the API server:
```bash
cd Mapping
uvicorn api.server:app --reload
```

### Step 3: Open the Frontend
Open `Mapping/ui/index.html` in your browser

### Step 4: Test Each System
1. Select "Ayurveda" from dropdown
2. Try searching for symptoms like "knee pain"
3. Select "Unani" from dropdown
4. Try searching for symptoms like "headache"
5. Select "Siddha" from dropdown
6. Verify it still works as before

## File Structure

```
Mapping/
├── data/
│   ├── ayurveda_data.json          ✅ NEW
│   ├── unani_data.json             ✅ NEW
│   ├── icd10_data.json             ✅ NEW
│   ├── extract_systems.py          ✅ NEW
│   └── namaste_data.json
├── build_indexes/
│   ├── build_indexes_ayurveda.py   ✅ NEW
│   └── build_indexes_unani.py      ✅ NEW
├── indexes/
│   ├── bm25_ayurveda.pkl           ✅ GENERATED
│   ├── tfidf_ayurveda.pkl          ✅ GENERATED
│   ├── embeddings_ayurveda.npy     ✅ GENERATED
│   └── (unani indexes - to be generated)
├── search_ayurveda.py              ✅ NEW
├── search_unani.py                 ✅ NEW
├── api/
│   ├── server.py                   ✅ UPDATED
│   └── autocomplete.py             ✅ UPDATED
└── ui/
    ├── index.html                  ✅ UPDATED
    ├── script.js                   ✅ UPDATED
    └── script.css                  ✅ UPDATED
```

## API Endpoints

### Autocomplete
- GET `/siddha/autocomplete?q={query}`
- GET `/ayurveda/autocomplete?q={query}`
- GET `/unani/autocomplete?q={query}`

### Diagnosis
- POST `/siddha/diagnose` - body: `{"symptoms": "..."}`
- POST `/ayurveda/diagnose` - body: `{"symptoms": "..."}`
- POST `/unani/diagnose` - body: `{"symptoms": "..."}`

### Mapping
- POST `/map` - body: `{"query": "...", "system": "siddha|ayurveda|unani"}`
- POST `/map/siddha-code` - body: `{"code": "...", "term": "..."}`
- POST `/map/ayurveda-code` - body: `{"code": "...", "term": "..."}`
- POST `/map/unani-code` - body: `{"code": "...", "term": "..."}`

## Features

✅ Dropdown selector for system selection
✅ Dynamic label updates based on selected system
✅ Autocomplete for all 3 systems
✅ Symptom-based diagnosis for all 3 systems
✅ Full mapping pipeline to ICD-11 and ICD-11 TM2
✅ Same hybrid retrieval approach (BM25 → TF-IDF → Semantic)

## Notes

- All systems use the same embedding model: `pritamdeka/S-PubMedBert-MS-MARCO`
- The workflow remains consistent across all systems
- Frontend automatically adapts to the selected system
- No code changes needed when switching between systems
