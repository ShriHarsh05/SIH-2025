#!/usr/bin/env python3
"""
ICD-11 Foundation URI Lookup Script

This script looks up ICD-11 codes and retrieves their Foundation URI and numeric code
from the WHO ICD-11 API.

Example:
    Input: SR40
    Output: 
        - Foundation URI: http://id.who.int/icd/entity/1531867635
        - Numeric Code: 1531867635

Usage:
    python icd11_foundation_uri_lookup.py SR40
    python icd11_foundation_uri_lookup.py --interactive
    python icd11_foundation_uri_lookup.py --batch codes.txt
"""

import requests
import json
import sys
import os
from typing import Optional, Dict, Tuple
from pathlib import Path

# WHO ICD-11 API Configuration
ICD11_API_BASE = "https://id.who.int/icd"
ICD11_RELEASE = "release/11/2024-01"  # Latest release
ICD11_TM2_URI = f"{ICD11_API_BASE}/{ICD11_RELEASE}/tm2"  # Traditional Medicine 2
ICD11_MMS_URI = f"{ICD11_API_BASE}/{ICD11_RELEASE}/mms"  # Standard MMS (fallback)

# OAuth2 credentials (optional - for higher rate limits)
CLIENT_ID = "c34e2cc8-eecf-485c-8639-c395e38709b4_88050a3f-1d28-42f9-a3f5-4572ffdad685"
CLIENT_SECRET = "6XYdcBzbOyHDoNrpkuq7t/WpdbaC0r2Sr4nJMJpzfSo="

class ICD11Lookup:
    """ICD-11 Foundation URI Lookup"""
    
    def __init__(self):
        self.access_token = None
        self.session = requests.Session()
        
        # Try to get OAuth token if credentials provided
        if CLIENT_ID and CLIENT_SECRET:
            self._get_access_token()
    
    def _get_access_token(self) -> bool:
        """Get OAuth2 access token from WHO"""
        try:
            token_url = "https://icdaccessmanagement.who.int/connect/token"
            
            payload = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'scope': 'icdapi_access',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, data=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json',
                    'API-Version': 'v2',
                    'Accept-Language': 'en'
                })
                return True
            else:
                print(f"⚠️  OAuth token request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️  Could not get OAuth token: {e}")
            return False
    
    def lookup_code(self, code: str, use_tm2: bool = True) -> Optional[Dict]:
        """
        Look up an ICD-11 code and retrieve its Foundation URI
        
        Args:
            code: ICD-11 code (e.g., "SR40", "1A00")
            use_tm2: If True, search TM2 first (for traditional medicine codes)
        
        Returns:
            Dictionary with Foundation URI and numeric code, or None if not found
        """
        try:
            # Clean the code
            code = code.strip().upper()
            
            # Set headers
            headers = {
                'Accept': 'application/json',
                'API-Version': 'v2',
                'Accept-Language': 'en'
            }
            
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            # Determine which endpoint to use based on code pattern
            # TM2 codes typically start with S (SR, SP, etc.)
            is_tm2_code = code.startswith('S')
            
            if use_tm2 and is_tm2_code:
                # Try TM2 first for traditional medicine codes
                result = self._lookup_in_tm2(code, headers)
                if result:
                    return result
                
                # Fallback to MMS if not found in TM2
                print(f"⚠️  Not found in TM2, trying standard MMS...")
                return self._lookup_in_mms(code, headers)
            else:
                # Try MMS first for standard codes
                result = self._lookup_in_mms(code, headers)
                if result:
                    return result
                
                # Fallback to TM2
                print(f"⚠️  Not found in MMS, trying TM2...")
                return self._lookup_in_tm2(code, headers)
                
        except requests.exceptions.Timeout:
            print(f"⚠️  Request timed out")
            return None
        except Exception as e:
            print(f"❌ Error looking up code: {e}")
            return None
    
    def _lookup_in_tm2(self, code: str, headers: Dict) -> Optional[Dict]:
        """Look up code in ICD-11 TM2 (Traditional Medicine)"""
        try:
            # Try direct lookup first
            entity_url = f"{ICD11_TM2_URI}/{code}"
            
            response = requests.get(entity_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                entity = response.json()
                foundation_uri = entity.get('foundationURI', entity.get('@id', ''))
                numeric_code = self._extract_numeric_code(foundation_uri)
                
                title = entity.get('title', {})
                if isinstance(title, dict):
                    title = title.get('@value', '')
                
                definition = entity.get('definition', {})
                if isinstance(definition, dict):
                    definition = definition.get('@value', '')
                
                return {
                    'code': code,
                    'title': title,
                    'foundation_uri': foundation_uri,
                    'numeric_code': numeric_code,
                    'tm2_uri': entity.get('@id', ''),
                    'source': 'ICD-11 TM2',
                    'definition': definition
                }
            
            # Try search if direct lookup fails
            search_url = f"{ICD11_TM2_URI}/search"
            params = {
                'q': code,
                'flatResults': 'true',
                'useFlexisearch': 'false'
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'destinationEntities' in data:
                    for entity in data['destinationEntities']:
                        entity_code = entity.get('theCode', '')
                        
                        if entity_code == code:
                            foundation_uri = entity.get('id', '')
                            numeric_code = self._extract_numeric_code(foundation_uri)
                            
                            return {
                                'code': code,
                                'title': entity.get('title', ''),
                                'foundation_uri': foundation_uri,
                                'numeric_code': numeric_code,
                                'tm2_uri': entity.get('stemId', ''),
                                'source': 'ICD-11 TM2',
                                'chapter': entity.get('chapter', ''),
                                'definition': entity.get('definition', '')
                            }
            
            return None
            
        except Exception as e:
            return None
    
    def _lookup_in_mms(self, code: str, headers: Dict) -> Optional[Dict]:
        """Look up code in ICD-11 MMS (Standard)"""
        try:
            # Try direct lookup first
            entity_url = f"{ICD11_MMS_URI}/{code}"
            
            response = requests.get(entity_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                entity = response.json()
                foundation_uri = entity.get('foundationURI', entity.get('@id', ''))
                numeric_code = self._extract_numeric_code(foundation_uri)
                
                title = entity.get('title', {})
                if isinstance(title, dict):
                    title = title.get('@value', '')
                
                definition = entity.get('definition', {})
                if isinstance(definition, dict):
                    definition = definition.get('@value', '')
                
                return {
                    'code': code,
                    'title': title,
                    'foundation_uri': foundation_uri,
                    'numeric_code': numeric_code,
                    'mms_uri': entity.get('@id', ''),
                    'source': 'ICD-11 MMS',
                    'definition': definition
                }
            
            # Try search if direct lookup fails
            print(f"   Direct lookup failed, trying search...")
            search_url = f"{ICD11_MMS_URI}/search"
            params = {
                'q': code,
                'flatResults': 'true',
                'useFlexisearch': 'true'  # Enable flexible search
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'destinationEntities' in data:
                    # First try exact match
                    for entity in data['destinationEntities']:
                        entity_code = entity.get('theCode', '')
                        
                        if entity_code == code:
                            foundation_uri = entity.get('id', '')
                            numeric_code = self._extract_numeric_code(foundation_uri)
                            
                            return {
                                'code': code,
                                'title': entity.get('title', ''),
                                'foundation_uri': foundation_uri,
                                'numeric_code': numeric_code,
                                'mms_uri': entity.get('stemId', ''),
                                'source': 'ICD-11 MMS (Search)',
                                'chapter': entity.get('chapter', ''),
                                'definition': entity.get('definition', '')
                            }
                    
                    # If no exact match, check if code appears in any result
                    for entity in data['destinationEntities']:
                        entity_code = entity.get('theCode', '')
                        
                        # Check if code is a substring or similar
                        if code.upper() in entity_code.upper():
                            foundation_uri = entity.get('id', '')
                            numeric_code = self._extract_numeric_code(foundation_uri)
                            
                            print(f"   Found similar code: {entity_code}")
                            
                            return {
                                'code': entity_code,
                                'original_query': code,
                                'title': entity.get('title', ''),
                                'foundation_uri': foundation_uri,
                                'numeric_code': numeric_code,
                                'mms_uri': entity.get('stemId', ''),
                                'source': 'ICD-11 MMS (Fuzzy Match)',
                                'chapter': entity.get('chapter', ''),
                                'definition': entity.get('definition', '')
                            }
            
            return None
            
        except Exception as e:
            return None
    

    
    def _extract_numeric_code(self, uri: str) -> str:
        """Extract numeric code from Foundation URI"""
        if not uri:
            return ""
        
        # URI format: http://id.who.int/icd/entity/1531867635
        parts = uri.rstrip('/').split('/')
        if parts:
            return parts[-1]
        return ""
    
    def lookup_from_local_data(self, code: str) -> Optional[Dict]:
        """
        Fallback: Look up code in local ICD-11 data files
        If found, try to get Foundation URI from WHO API using the title
        """
        try:
            local_result = None
            
            # Try ICD-11 Standard
            standard_path = Path(__file__).parent / "data" / "icd11_standard.json"
            if standard_path.exists():
                with open(standard_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for item in data:
                    if item.get('code', '').upper() == code.upper():
                        local_result = {
                            'code': code,
                            'title': item.get('title', ''),
                            'definition': item.get('definition', ''),
                            'source': 'local_data'
                        }
                        break
            
            # Try ICD-11 TM2
            if not local_result:
                tm2_path = Path(__file__).parent / "data" / "icd_tm2.json"
                if tm2_path.exists():
                    with open(tm2_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    for item in data:
                        if item.get('tm2_code', '').upper() == code.upper():
                            local_result = {
                                'code': code,
                                'title': item.get('english', ''),
                                'definition': item.get('description', ''),
                                'source': 'local_tm2_data'
                            }
                            break
            
            # If found in local data, try to get Foundation URI from WHO API
            if local_result and local_result.get('title'):
                print(f"   Found in local data, searching WHO API by title...")
                foundation_result = self._search_by_title(local_result['title'])
                
                if foundation_result:
                    # Merge local data with WHO API result
                    local_result.update({
                        'foundation_uri': foundation_result.get('foundation_uri'),
                        'numeric_code': foundation_result.get('numeric_code'),
                        'source': 'local_data + WHO API'
                    })
                    return local_result
                else:
                    local_result['note'] = 'Foundation URI not available - WHO API search failed'
                    return local_result
            
            return local_result
            
        except Exception as e:
            print(f"⚠️  Error reading local data: {e}")
            return None
    
    def _search_by_title(self, title: str) -> Optional[Dict]:
        """Search WHO API by title to find Foundation URI"""
        try:
            headers = {
                'Accept': 'application/json',
                'API-Version': 'v2',
                'Accept-Language': 'en'
            }
            
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            # Search in MMS
            search_url = f"{ICD11_MMS_URI}/search"
            params = {
                'q': title,
                'flatResults': 'true',
                'useFlexisearch': 'true'
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'destinationEntities' in data and len(data['destinationEntities']) > 0:
                    # Take the first result (best match)
                    entity = data['destinationEntities'][0]
                    foundation_uri = entity.get('id', '')
                    numeric_code = self._extract_numeric_code(foundation_uri)
                    
                    if foundation_uri:
                        return {
                            'foundation_uri': foundation_uri,
                            'numeric_code': numeric_code
                        }
            
            return None
            
        except Exception as e:
            return None


def print_result(result: Dict):
    """Pretty print the lookup result"""
    if not result:
        print("❌ Code not found")
        return
    
    print("\n" + "=" * 70)
    print(f"ICD-11 Code: {result['code']}")
    print("=" * 70)
    
    if result.get('source'):
        print(f"Source: {result['source']}")
    
    if result.get('title'):
        print(f"Title: {result['title']}")
    
    if result.get('foundation_uri'):
        print(f"\n✅ Foundation URI: {result['foundation_uri']}")
    
    if result.get('numeric_code'):
        print(f"✅ Numeric Code: {result['numeric_code']}")
    
    if result.get('tm2_uri'):
        print(f"\nTM2 URI: {result['tm2_uri']}")
    
    if result.get('mms_uri'):
        print(f"\nMMS URI: {result['mms_uri']}")
    
    if result.get('chapter'):
        print(f"Chapter: {result['chapter']}")
    
    if result.get('definition'):
        definition = result['definition']
        if len(definition) > 200:
            definition = definition[:200] + "..."
        print(f"\nDefinition: {definition}")
    
    if result.get('note'):
        print(f"\n⚠️  Note: {result['note']}")
    
    print("=" * 70 + "\n")


def interactive_mode():
    """Interactive mode for looking up codes"""
    lookup = ICD11Lookup()
    
    print("\n" + "=" * 70)
    print("ICD-11 Foundation URI Lookup - Interactive Mode")
    print("=" * 70)
    print("\nEnter ICD-11 codes to look up their Foundation URIs")
    print("Type 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            code = input("Enter ICD-11 code (e.g., SR40): ").strip()
            
            if code.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not code:
                continue
            
            print(f"\n🔍 Looking up code: {code}...")
            
            # Try API lookup first
            result = lookup.lookup_code(code)
            
            # Fallback to local data
            if not result:
                print("⚠️  Not found in WHO API, checking local data...")
                result = lookup.lookup_from_local_data(code)
            
            print_result(result)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


def batch_mode(file_path: str):
    """Batch mode for looking up multiple codes from a file"""
    lookup = ICD11Lookup()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            codes = [line.strip() for line in f if line.strip()]
        
        print(f"\n🔍 Looking up {len(codes)} codes from {file_path}...\n")
        
        results = []
        for i, code in enumerate(codes, 1):
            print(f"[{i}/{len(codes)}] Looking up: {code}")
            
            result = lookup.lookup_code(code)
            if not result:
                result = lookup.lookup_from_local_data(code)
            
            if result:
                results.append(result)
                print(f"  ✅ Found: {result.get('title', 'N/A')}")
            else:
                print(f"  ❌ Not found")
        
        # Save results to JSON
        output_file = file_path.replace('.txt', '_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to: {output_file}")
        print(f"Found {len(results)}/{len(codes)} codes\n")
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python icd11_foundation_uri_lookup.py <code>")
        print("  python icd11_foundation_uri_lookup.py --interactive")
        print("  python icd11_foundation_uri_lookup.py --batch <file.txt>")
        print("\nExamples:")
        print("  python icd11_foundation_uri_lookup.py SR40")
        print("  python icd11_foundation_uri_lookup.py 1A00")
        print("  python icd11_foundation_uri_lookup.py --interactive")
        sys.exit(1)
    
    if sys.argv[1] in ['--interactive', '-i']:
        interactive_mode()
    elif sys.argv[1] in ['--batch', '-b']:
        if len(sys.argv) < 3:
            print("❌ Please provide a file path for batch mode")
            sys.exit(1)
        batch_mode(sys.argv[2])
    else:
        # Single code lookup
        code = sys.argv[1]
        lookup = ICD11Lookup()
        
        print(f"\n🔍 Looking up code: {code}...")
        
        result = lookup.lookup_code(code)
        
        if not result:
            print("⚠️  Not found in WHO API, checking local data...")
            result = lookup.lookup_from_local_data(code)
        
        print_result(result)


if __name__ == "__main__":
    main()
