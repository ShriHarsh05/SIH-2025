#!/usr/bin/env python3
"""
Convert ayu-sat-table-c.csv to JSON format
Output format: term, system, code, definition (short + long)
"""

import csv
import json
from pathlib import Path

def convert_ayusat_csv_to_json(csv_file, output_file):
    """
    Convert Ayurveda SAT CSV to JSON format
    
    Args:
        csv_file: Path to input CSV file
        output_file: Path to output JSON file
    """
    
    print("=" * 70)
    print("CONVERTING AYURVEDA SAT CSV TO JSON")
    print("=" * 70)
    
    print(f"\nInput file: {csv_file}")
    print(f"Output file: {output_file}")
    
    # Read CSV file
    data = []
    skipped = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        print("\nProcessing CSV rows...")
        
        for row in reader:
            # Extract fields
            word = row.get('Word', '').strip()
            code = row.get('Code', '').strip()
            short_def = row.get('Short Defination', '').strip()
            long_def = row.get('Long Defination', '').strip()
            
            # Skip rows without word or code
            if not word or not code:
                skipped += 1
                continue
            
            # Combine short and long definitions
            definition_parts = []
            if short_def:
                definition_parts.append(short_def)
            if long_def:
                definition_parts.append(long_def)
            
            # Join with ". " if both exist, otherwise use what's available
            if len(definition_parts) == 2:
                definition = f"{definition_parts[0]}. {definition_parts[1]}"
            elif len(definition_parts) == 1:
                definition = definition_parts[0]
            else:
                definition = ""
            
            # Create JSON entry
            entry = {
                "term": word,
                "system": "Ayurveda-SAT",
                "code": code,
                "definition": definition
            }
            
            data.append(entry)
    
    print(f"✓ Processed {len(data)} entries")
    if skipped > 0:
        print(f"⚠ Skipped {skipped} rows (missing word or code)")
    
    # Write JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ JSON file created: {output_file}")
    
    # Display sample entries
    print("\n" + "=" * 70)
    print("SAMPLE ENTRIES (first 3)")
    print("=" * 70)
    
    for i, entry in enumerate(data[:3], 1):
        print(f"\n{i}. Term: {entry['term']}")
        print(f"   System: {entry['system']}")
        print(f"   Code: {entry['code']}")
        print(f"   Definition: {entry['definition'][:100]}..." if len(entry['definition']) > 100 else f"   Definition: {entry['definition']}")
    
    # Statistics
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Total entries: {len(data)}")
    print(f"Entries with definitions: {sum(1 for e in data if e['definition'])}")
    print(f"Entries without definitions: {sum(1 for e in data if not e['definition'])}")
    
    # Count entries by code prefix
    code_prefixes = {}
    for entry in data:
        prefix = entry['code'].split('.')[0] if '.' in entry['code'] else entry['code']
        code_prefixes[prefix] = code_prefixes.get(prefix, 0) + 1
    
    print(f"\nEntries by code prefix:")
    for prefix, count in sorted(code_prefixes.items()):
        print(f"  {prefix}: {count}")
    
    print("\n" + "=" * 70)
    print("CONVERSION COMPLETE")
    print("=" * 70)
    
    return data

def main():
    """Main entry point"""
    
    # File paths
    base_dir = Path(__file__).parent
    csv_file = base_dir / "ayu-sat-table-c.csv"
    output_file = base_dir / "ayurveda_sat_data.json"
    
    # Check if CSV file exists
    if not csv_file.exists():
        print(f"✗ Error: CSV file not found: {csv_file}")
        return
    
    # Convert
    try:
        data = convert_ayusat_csv_to_json(csv_file, output_file)
        print(f"\n✓ Successfully converted {len(data)} entries")
        print(f"✓ Output saved to: {output_file}")
    except Exception as e:
        print(f"\n✗ Error during conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
