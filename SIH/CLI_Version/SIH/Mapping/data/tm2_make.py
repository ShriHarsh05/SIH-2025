import json

def split_icd_json(input_file, tm_output_file, standard_output_file):
    try:
        # 1. Load the original JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Successfully loaded {len(data)} entries from '{input_file}'.")

        tm_entries = []
        standard_entries = []

        # 2. Iterate through data
        for entry in data:
            # FIX: Use 'or ""' to ensure we never get None (which causes the crash)
            title = entry.get('title') or ""
            definition = entry.get('definition') or ""
            
            is_tm = False
            
            # Check for (TM2) in EITHER title OR definition
            if '(TM2)' in title or '(TM2)' in definition:
                is_tm = True
            
            # Categorize the entry
            if is_tm:
                tm_entries.append(entry)
            else:
                standard_entries.append(entry)

        # 3. Save the TM entries
        with open(tm_output_file, 'w', encoding='utf-8') as f:
            json.dump(tm_entries, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(tm_entries)} TM entries to '{tm_output_file}'.")

        # 4. Save the standard entries
        with open(standard_output_file, 'w', encoding='utf-8') as f:
            json.dump(standard_entries, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(standard_entries)} standard entries to '{standard_output_file}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Configuration ---
input_filename = r'C:\Users\Lenovo\Documents\SIH\Mapping\data\icd11_cleaned.json'
tm_filename = 'icd11_tm_codes.json'    
rest_filename = 'icd11_standard.json'  

if __name__ == "__main__":
    split_icd_json(input_filename, tm_filename, rest_filename)