"""
Debug script to test WHO ICD-11 API
"""

import requests
import json

CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='

print("Step 1: Getting OAuth2 token...")
token_url = "https://icdaccessmanagement.who.int/connect/token"
payload = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'scope': 'icdapi_access',
    'grant_type': 'client_credentials'
}

try:
    response = requests.post(token_url, data=payload, timeout=10)
    print(f"Token response status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        print(f"✓ Token obtained: {access_token[:50]}...")
        
        print("\nStep 2: Searching for ICD-11 code '1A00'...")
        search_url = "https://id.who.int/icd/release/11/2024-01/mms/search"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'API-Version': 'v2',
            'Accept-Language': 'en'
        }
        
        params = {'q': '1A00'}
        
        search_response = requests.get(search_url, headers=headers, params=params, timeout=10)
        print(f"Search response status: {search_response.status_code}")
        print(f"\nSearch response body:")
        print(json.dumps(search_response.json(), indent=2))
        
        print("\nStep 3: Trying codeinfo lookup for '1A00'...")
        codeinfo_url = "https://id.who.int/icd/release/11/2024-01/mms/codeinfo/1A00"
        
        codeinfo_response = requests.get(codeinfo_url, headers=headers, timeout=10)
        print(f"Codeinfo response status: {codeinfo_response.status_code}")
        codeinfo_data = codeinfo_response.json()
        print(f"\nCodeinfo response body:")
        print(json.dumps(codeinfo_data, indent=2))
        
        stem_id = codeinfo_data.get('stemId')
        if stem_id:
            print(f"\nStep 4: Fetching entity details from stemId: {stem_id}")
            entity_response = requests.get(stem_id, headers=headers, timeout=10)
            print(f"Entity response status: {entity_response.status_code}")
            print(f"\nEntity response body (first 500 chars):")
            entity_text = json.dumps(entity_response.json(), indent=2)
            print(entity_text[:500] + "...")
        
    else:
        print(f"✗ Token request failed: {response.text}")
        
except Exception as e:
    print(f"✗ Error: {e}")
