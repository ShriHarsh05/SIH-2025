# Ayurveda SAT CSV to JSON Conversion

## Overview
This document describes the conversion of the Ayurveda SAT (Standardized Ayurveda Terminology) CSV file to JSON format for integration with the TM-ICD Mapping System.

## Source File
- **Input:** `ayu-sat-table-c.csv`
- **Format:** CSV with columns: Sr No., t_id, Code, parent_id, Word, Short Defination, Long Defination, reference
- **Entries:** 176 Ayurveda SAT terms

## Conversion Script
- **Script:** `convert_ayusat_csv_to_json.py`
- **Language:** Python 3
- **Dependencies:** Standard library only (csv, json, pathlib)

## Output File
- **Output:** `ayurveda_sat_data.json`
- **Format:** JSON array of objects
- **Entries:** 176 terms

## JSON Structure

Each entry in the JSON file has the following structure:

```json
{
  "term": "vyAdhiH",
  "system": "Ayurveda-SAT",
  "code": "SAT-C.1",
  "definition": "disease/ syndrome. the term signifies disease or ailment which brings about grief or pain to the individual; the word meaning implies an abnormal state of distress or pain, wherein the mind resolves to counteract the disturbances in the body to bring a healthy state. vyadhi brings about distress to physical and mental wellbeing of individual"
}
```

### Fields

| Field | Description | Source |
|-------|-------------|--------|
| `term` | Ayurveda SAT term | CSV column: "Word" |
| `system` | System identifier | Fixed value: "Ayurveda-SAT" |
| `code` | SAT code | CSV column: "Code" |
| `definition` | Combined definition | CSV columns: "Short Defination" + "Long Defination" |

## Definition Combination Logic

The `definition` field is created by combining the short and long definitions:

1. **Both exist:** `"{short_definition}. {long_definition}"`
2. **Only short:** `"{short_definition}"`
3. **Only long:** `"{long_definition}"`
4. **Neither:** `""` (empty string)

### Example
```
Short: "disease/ syndrome"
Long: "the term signifies disease or ailment which brings about grief..."

Result: "disease/ syndrome. the term signifies disease or ailment which brings about grief..."
```

## Usage

### Running the Conversion Script

```bash
# Navigate to data directory
cd Mapping/data

# Run the script
python convert_ayusat_csv_to_json.py
```

### Output
```
======================================================================
CONVERTING AYURVEDA SAT CSV TO JSON
======================================================================

Input file: ayu-sat-table-c.csv
Output file: ayurveda_sat_data.json

Processing CSV rows...
✓ Processed 176 entries

✓ JSON file created: ayurveda_sat_data.json

======================================================================
STATISTICS
======================================================================
Total entries: 176
Entries with definitions: 175
Entries without definitions: 1

Entries by code prefix:
  SAT-C: 176

======================================================================
CONVERSION COMPLETE
======================================================================
```

## Statistics

- **Total entries:** 176
- **Entries with definitions:** 175 (99.4%)
- **Entries without definitions:** 1 (0.6%)
- **Code prefix:** All entries use "SAT-C" prefix

## Code Structure

The SAT codes follow a hierarchical structure:

- `SAT-C` - Root level
- `SAT-C.1` - First level
- `SAT-C.1.1` - Second level
- `SAT-C.1.1.1` - Third level

Example hierarchy:
```
SAT-C (vyAdhi viniScaya/ nidAna)
├── SAT-C.1 (vyAdhiH)
│   ├── SAT-C.2 (vyAdhiparyAyaH)
│   │   ├── SAT-C.3 (AmayaH)
│   │   ├── SAT-C.4 (gadaH)
│   │   └── ...
```

## Integration with TM-ICD Mapping System

### Next Steps

1. **Create Build Indexes Script**
   - Create `build_indexes/build_indexes_ayurveda_sat.py`
   - Build BM25, TF-IDF, and embedding indexes
   - Store metadata (codes, terms, definitions)

2. **Create Search Module**
   - Create `search_ayurveda_sat.py`
   - Implement hybrid search (BM25 → TF-IDF → Semantic)
   - Return candidates with definitions

3. **Update CLI Application**
   - Add "Ayurveda-SAT" to system selection menu
   - Update search routing
   - Display SAT terms with definitions

4. **Update Database Schema**
   - Support "Ayurveda-SAT" as a system type
   - Store SAT codes and definitions

5. **Update FHIR Generator**
   - Add SAT code system URL
   - Include SAT codes in FHIR output

### Example Integration

```python
# In cli_app.py
systems = {
    '1': 'siddha',
    '2': 'ayurveda',
    '3': 'unani',
    '4': 'ayurveda-sat'  # New option
}

# In search routing
if self.current_system == 'ayurveda-sat':
    result = search_ayurveda_sat(query)
```

## Data Quality

### Strengths
- Comprehensive coverage of Ayurveda terminology
- Hierarchical code structure
- Detailed definitions (short + long)
- Standardized format

### Considerations
- 1 entry without definition (root node)
- Some definitions contain special characters (e.g., "?ma")
- Terms use transliterated Sanskrit (diacritical marks)

## File Locations

```
Mapping/
├── data/
│   ├── ayu-sat-table-c.csv              # Source CSV
│   ├── ayurveda_sat_data.json           # Generated JSON
│   ├── convert_ayusat_csv_to_json.py    # Conversion script
│   └── AYUSAT_CONVERSION_README.md      # This file
```

## Maintenance

### Re-running Conversion

If the source CSV is updated:

```bash
cd Mapping/data
python convert_ayusat_csv_to_json.py
```

The script will overwrite the existing JSON file.

### Validation

To validate the JSON file:

```python
import json

with open('ayurveda_sat_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
print(f"Total entries: {len(data)}")
print(f"Sample entry: {data[0]}")
```

## References

- **Source:** Ayurveda SAT (Standardized Ayurveda Terminology)
- **Format:** Table C - Disease/Syndrome Classification
- **Encoding:** UTF-8
- **Language:** Sanskrit (transliterated) with English definitions

## Version History

- **v1.0** (2024-12-09) - Initial conversion
  - Converted 176 entries from CSV to JSON
  - Combined short and long definitions
  - Added system identifier "Ayurveda-SAT"

## Contact

For questions or issues with the conversion, refer to the main project documentation.
