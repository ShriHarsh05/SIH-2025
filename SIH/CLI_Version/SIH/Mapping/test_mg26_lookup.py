#!/usr/bin/env python3
"""
Test script specifically for looking up MG26 code
"""

import requests
import json

def lookup_mg26_comprehensive():
    """Comprehensive lookup for MG26 using multiple strategies"""
    
    code = "MG26"
    
    print("\n" + "="*70)
    print(f"Comprehensive Lookup for ICD-11 Code: {code}")
    print("="*70 + "\n")
    
    headers = {
        'Accept': 'application/json',
        'API-Version': 'v2',
        'Accept-Language': 'en'
    }
    
    # Strategy 1: Direct MMS lookup
    print("Strategy 1: Direct MMS lookup")
    print("-" * 70)
    try:
        url = f"https://id.who.int/icd/release/11/2024-01/mms/{code}"
        print(f"URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            foundation_uri = data.get('foundationURI', '')
            numeric_code = foundation_uri.split('/')[-1] if foundation_uri else ''
            
            print(f"✅ SUCCESS!")
            print(f"Foundation URI: {foundation_uri}")
            print(f"Numeric Code: {numeric_code}")
            return
        else:
            print(f"❌ Not found via direct lookup")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")
    
    # Strategy 2: MMS Search by code
    print("Strategy 2: MMS Search by code")
    print("-" * 70)
    try:
        url = f"https://id.who.int/icd/release/11/2024-01/mms/search"
        params = {'q': code, 'flatResults': 'true', 'useFlexisearch': 'true'}
        print(f"URL: {url}")
        print(f"Params: {params}")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'destinationEntities' in data and len(data['destinationEntities']) > 0:
                print(f"Found {len(data['destinationEntities'])} results")
                
                for i, entity in enumerate(data['destinationEntities'][:3], 1):
                    entity_code = entity.get('theCode', '')
                    title = entity.get('title', '')
                    foundation_uri = entity.get('id', '')
                    numeric_code = foundation_uri.split('/')[-1] if foundation_uri else ''
                    
                    print(f"\nResult {i}:")
                    print(f"  Code: {entity_code}")
                    print(f"  Title: {title}")
                    print(f"  Foundation URI: {foundation_uri}")
                    print(f"  Numeric Code: {numeric_code}")
                    
                    if entity_code == code:
                        print(f"\n✅ EXACT MATCH FOUND!")
                        return
            else:
                print(f"❌ No results found")
        else:
            print(f"❌ Search failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")
    
    # Strategy 3: Search by title from local data
    print("Strategy 3: Search by title from local data")
    print("-" * 70)
    try:
        # Load local data
        with open('data/icd11_standard.json', 'r', encoding='utf-8') as f:
            local_data = json.load(f)
        
        # Find MG26 in local data
        local_entry = None
        for item in local_data:
            if item.get('code', '').upper() == code.upper():
                local_entry = item
                break
        
        if local_entry:
            title = local_entry.get('title', '')
            print(f"Found in local data:")
            print(f"  Code: {code}")
            print(f"  Title: {title}")
            print(f"  Definition: {local_entry.get('definition', '')[:100]}...")
            
            # Now search WHO API by title
            print(f"\nSearching WHO API by title: '{title}'")
            url = f"https://id.who.int/icd/release/11/2024-01/mms/search"
            params = {'q': title, 'flatResults': 'true', 'useFlexisearch': 'true'}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'destinationEntities' in data and len(data['destinationEntities']) > 0:
                    entity = data['destinationEntities'][0]
                    foundation_uri = entity.get('id', '')
                    numeric_code = foundation_uri.split('/')[-1] if foundation_uri else ''
                    
                    print(f"\n✅ FOUND VIA TITLE SEARCH!")
                    print(f"Foundation URI: {foundation_uri}")
                    print(f"Numeric Code: {numeric_code}")
                    print(f"Matched Title: {entity.get('title', '')}")
                    return
                else:
                    print(f"❌ No results from title search")
            else:
                print(f"❌ Title search failed: {response.status_code}")
        else:
            print(f"❌ Code not found in local data")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")
    
    # Strategy 4: Try TM2
    print("Strategy 4: Try TM2 endpoint")
    print("-" * 70)
    try:
        url = f"https://id.who.int/icd/release/11/2024-01/tm2/{code}"
        print(f"URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            foundation_uri = data.get('foundationURI', '')
            numeric_code = foundation_uri.split('/')[-1] if foundation_uri else ''
            
            print(f"✅ FOUND IN TM2!")
            print(f"Foundation URI: {foundation_uri}")
            print(f"Numeric Code: {numeric_code}")
            return
        else:
            print(f"❌ Not found in TM2")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("All strategies exhausted. Code may not be in WHO API.")
    print("="*70 + "\n")


if __name__ == "__main__":
    lookup_mg26_comprehensive()
