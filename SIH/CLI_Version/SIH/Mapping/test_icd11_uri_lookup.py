#!/usr/bin/env python3
"""
Simple test script for ICD-11 Foundation URI lookup
Demonstrates looking up SR40 and printing the Foundation URI and numeric code
"""

import requests
import json

def lookup_icd11_code(code, use_tm2=True):
    """
    Look up an ICD-11 code and return Foundation URI and numeric code
    
    Args:
        code: ICD-11 code (e.g., "SR40")
        use_tm2: If True, search TM2 first (for traditional medicine codes)
    
    Returns:
        Dictionary with foundation_uri and numeric_code
    """
    print(f"\n{'='*70}")
    print(f"Looking up ICD-11 Code: {code}")
    print(f"{'='*70}\n")
    
    try:
        # Determine which endpoint to use
        # TM2 codes typically start with S (SR, SP, etc.)
        is_tm2_code = code.upper().startswith('S')
        
        if use_tm2 and is_tm2_code:
            # Try TM2 endpoint for traditional medicine codes
            url = f"https://id.who.int/icd/release/11/2024-01/tm2/{code}"
            source = "ICD-11 TM2 (Traditional Medicine)"
        else:
            # Use standard MMS endpoint
            url = f"https://id.who.int/icd/release/11/2024-01/mms/{code}"
            source = "ICD-11 MMS (Standard)"
        
        # Headers
        headers = {
            'Accept': 'application/json',
            'API-Version': 'v2',
            'Accept-Language': 'en'
        }
        
        print(f"🔍 Querying WHO ICD-11 API...")
        print(f"   Source: {source}")
        print(f"   URL: {url}\n")
        
        # Make request
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract information
            title = data.get('title', {})
            if isinstance(title, dict):
                title = title.get('@value', 'N/A')
            
            foundation_uri = data.get('foundationURI', data.get('@id', ''))
            
            # Extract numeric code from Foundation URI
            # Format: http://id.who.int/icd/entity/1531867635
            numeric_code = foundation_uri.split('/')[-1] if foundation_uri else 'N/A'
            
            # Get definition
            definition = data.get('definition', {})
            if isinstance(definition, dict):
                definition = definition.get('@value', 'N/A')
            
            # Print results
            print(f"✅ SUCCESS!\n")
            print(f"Source:         {source}")
            print(f"Code:           {code}")
            print(f"Title:          {title}")
            print(f"\n{'─'*70}")
            print(f"Foundation URI: {foundation_uri}")
            print(f"Numeric Code:   {numeric_code}")
            print(f"{'─'*70}\n")
            
            if definition and definition != 'N/A':
                # Truncate long definitions
                if len(definition) > 200:
                    definition = definition[:200] + "..."
                print(f"Definition:     {definition}\n")
            
            return {
                'code': code,
                'source': source,
                'title': title,
                'foundation_uri': foundation_uri,
                'numeric_code': numeric_code,
                'definition': definition
            }
        
        elif response.status_code == 404:
            # Try fallback to other endpoint
            if use_tm2 and is_tm2_code:
                print(f"⚠️  Not found in TM2, trying standard MMS...")
                return lookup_icd11_code(code, use_tm2=False)
            elif not is_tm2_code:
                print(f"⚠️  Not found in MMS, trying TM2...")
                # Try TM2 as fallback
                url_tm2 = f"https://id.who.int/icd/release/11/2024-01/tm2/{code}"
                response_tm2 = requests.get(url_tm2, headers=headers, timeout=10)
                if response_tm2.status_code == 200:
                    # Recursively call with TM2
                    return lookup_icd11_code(code, use_tm2=True)
            
            print(f"❌ Code '{code}' not found in ICD-11")
            return None
        
        elif response.status_code == 401:
            print(f"⚠️  Authentication required (rate limit may be lower)")
            print(f"   Consider registering at: https://icd.who.int/icdapi")
            return None
        
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
    
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out. Please check your internet connection.")
        return None
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error. Please check your internet connection.")
        return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_multiple_codes():
    """Test multiple ICD-11 TM2 codes"""
    test_codes = [
        "SR40",  # Lumbar spondylosis disorder (TM2)
        "SP42",  # Fever disorder (TM2)
        "SP43",  # Pain disorder (TM2)
    ]
    
    print("\n" + "="*70)
    print("ICD-11 TM2 Foundation URI Lookup - Test Script")
    print("="*70)
    print("Testing Traditional Medicine (TM2) codes")
    print("="*70)
    
    results = []
    
    for code in test_codes:
        result = lookup_icd11_code(code)
        if result:
            results.append(result)
        print()  # Blank line between results
    
    # Summary
    print("\n" + "="*70)
    print(f"Summary: Found {len(results)}/{len(test_codes)} codes")
    print("="*70)
    
    if results:
        print("\nQuick Reference:")
        for r in results:
            print(f"  {r['code']}: {r['numeric_code']}")
    
    print()
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Look up specific code from command line
        code = sys.argv[1]
        lookup_icd11_code(code)
    else:
        # Run tests with example codes
        test_multiple_codes()
