"""Debug code lookup"""

import requests
import json

CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='

# Get token
token_url = "https://icdaccessmanagement.who.int/connect/token"
payload = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'scope': 'icdapi_access',
    'grant_type': 'client_credentials'
}

response = requests.post(token_url, data=payload)
token_data = response.json()
access_token = token_data['access_token']

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json',
    'API-Version': 'v2',
    'Accept-Language': 'en'
}

# Test code
code = "1A00"

print(f"Looking up code: {code}")
print("="*60)

# Get codeinfo
codeinfo_url = f"https://id.who.int/icd/release/11/2024-01/mms/codeinfo/{code}"
codeinfo_response = requests.get(codeinfo_url, headers=headers)
codeinfo_data = codeinfo_response.json()

print("\nCodeinfo response:")
print(json.dumps(codeinfo_data, indent=2))

print(f"\nExtracted code from codeinfo: {codeinfo_data.get('code')}")
print(f"Extracted stemId: {codeinfo_data.get('stemId')}")

# Get entity
stem_id = codeinfo_data.get('stemId')
entity_response = requests.get(stem_id, headers=headers)
entity_data = entity_response.json()

print("\nEntity response (key fields):")
print(f"  @id: {entity_data.get('@id')}")
print(f"  code: {entity_data.get('code')}")
print(f"  title: {entity_data.get('title')}")
print(f"  source: {entity_data.get('source')}")
