"""
Extract Ayurveda, Unani, and ICD-10 datasets from namaste_data.json
"""
import json
import re
from pathlib import Path

# Input file
INPUT_FILE = Path(__file__).parent / "namaste_data.json"

# Output files
OUTPUT_AYURVEDA = Path(__file__).parent / "ayurveda_data.json"
OUTPUT_UNANI = Path(__file__).parent / "unani_data.json"
OUTPUT_ICD10 = Path(__file__).parent / "icd10_data.json"

def extract_systems():
    """Extract data by system type using regex pattern matching"""
    
    print("📖 Loading namaste_data.json...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} total entries")
    
    # Filter by system using regex for exact matching
    ayurveda_data = []
    unani_data = []
    icd10_data = []
    
    for entry in data:
        system = entry.get("system", "")
        
        # Use regex to match exact system names
        if re.match(r"^Ayurveda$", system, re.IGNORECASE):
            ayurveda_data.append(entry)
        elif re.match(r"^Unani$", system, re.IGNORECASE):
            unani_data.append(entry)
        elif re.match(r"^ICD-10$", system, re.IGNORECASE):
            icd10_data.append(entry)
    
    # Save Ayurveda data
    print(f"\n💾 Saving {len(ayurveda_data)} Ayurveda entries...")
    with open(OUTPUT_AYURVEDA, "w", encoding="utf-8") as f:
        json.dump(ayurveda_data, f, indent=2, ensure_ascii=False)
    
    # Save Unani data
    print(f"💾 Saving {len(unani_data)} Unani entries...")
    with open(OUTPUT_UNANI, "w", encoding="utf-8") as f:
        json.dump(unani_data, f, indent=2, ensure_ascii=False)
    
    # Save ICD-10 data
    print(f"💾 Saving {len(icd10_data)} ICD-10 entries...")
    with open(OUTPUT_ICD10, "w", encoding="utf-8") as f:
        json.dump(icd10_data, f, indent=2, ensure_ascii=False)
    
    print("\n✨ Extraction complete!")
    print(f"   - Ayurveda: {OUTPUT_AYURVEDA}")
    print(f"   - Unani: {OUTPUT_UNANI}")
    print(f"   - ICD-10: {OUTPUT_ICD10}")
    
    return {
        "ayurveda": len(ayurveda_data),
        "unani": len(unani_data),
        "icd10": len(icd10_data)
    }

if __name__ == "__main__":
    stats = extract_systems()
    print(f"\n📊 Summary:")
    print(f"   Ayurveda: {stats['ayurveda']} entries")
    print(f"   Unani: {stats['unani']} entries")
    print(f"   ICD-10: {stats['icd10']} entries")
