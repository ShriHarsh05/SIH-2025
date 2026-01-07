"""
ICD-11 to FHIR CodeSystem Pipeline
Takes an ICD-11 code and returns a FHIR-compliant CodeSystem JSON with Entity ID
"""

import requests
import json
from typing import Dict, Optional
from urllib.parse import quote


class ICD11FHIRPipeline:
    """Pipeline to convert ICD-11 codes to FHIR CodeSystem format"""
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the pipeline with WHO ICD-11 API credentials
        
        Args:
            client_id: WHO API client ID
            client_secret: WHO API client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://icdaccessmanagement.who.int/connect/token"
        self.search_url = "https://id.who.int/icd/release/11/2024-01/mms/search"
        self.access_token = None
    
    def get_access_token(self) -> str:
        """
        Get OAuth2 access token from WHO ICD-11 API
        
        Returns:
            Access token string
        """
        if self.access_token:
            return self.access_token
        
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'icdapi_access',
            'grant_type': 'client_credentials'
        }
        
        response = requests.post(self.token_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        return self.access_token
    
    def search_icd11_code(self, code: str) -> Optional[Dict]:
        """
        Search ICD-11 API for a specific code
        
        Args:
            code: ICD-11 code (e.g., "1A00")
        
        Returns:
            Dictionary with code, title, and entity_id or None if not found
        """
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'API-Version': 'v2',
            'Accept-Language': 'en'
        }
        
        # Primary strategy: Use codeinfo endpoint for exact code lookup
        lookup_url = f"https://id.who.int/icd/release/11/2024-01/mms/codeinfo/{code}"
        try:
            lookup_response = requests.get(lookup_url, headers=headers)
            if lookup_response.status_code == 200:
                codeinfo_data = lookup_response.json()
                
                # Get the stemId (entity URL)
                stem_id = codeinfo_data.get('stemId', '')
                icd_code = codeinfo_data.get('code', code)
                
                if stem_id:
                    # Fetch the full entity details
                    entity_response = requests.get(stem_id, headers=headers)
                    if entity_response.status_code == 200:
                        entity_data = entity_response.json()
                        
                        # Extract title
                        title_obj = entity_data.get('title', {})
                        if isinstance(title_obj, dict):
                            disease_name = title_obj.get('@value', 'Unknown Disease')
                        else:
                            disease_name = str(title_obj) if title_obj else 'Unknown Disease'
                        
                        # Extract entity ID from stemId
                        entity_id = stem_id.split('/')[-1]
                        
                        return {
                            'code': icd_code,
                            'display': disease_name,
                            'entity_id': entity_id,
                            'entity_url': stem_id
                        }
        except Exception as e:
            # If codeinfo fails, try search as fallback
            pass
        
        # Fallback strategy: Use search API
        params = {'q': code, 'useFlexisearch': 'false', 'flatResults': 'true'}
        response = requests.get(self.search_url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        destination_entities = data.get('destinationEntities', [])
        
        if destination_entities:
            # Filter for exact code match
            for entity in destination_entities:
                if entity.get('theCode') == code:
                    # Extract required fields
                    icd_code = entity.get('theCode', code)
                    title_obj = entity.get('title', {})
                    if isinstance(title_obj, dict):
                        disease_name = title_obj.get('@value', 'Unknown Disease')
                    else:
                        disease_name = str(title_obj) if title_obj else 'Unknown Disease'
                    entity_url = entity.get('id', '')
                    
                    # Extract Entity ID from URL
                    entity_id = entity_url.split('/')[-1] if entity_url else ''
                    
                    return {
                        'code': icd_code,
                        'display': disease_name,
                        'entity_id': entity_id,
                        'entity_url': entity_url
                    }
        
        return None
    
    def build_fhir_codesystem(self, icd_data: Dict) -> Dict:
        """
        Build FHIR-compliant CodeSystem JSON
        
        Args:
            icd_data: Dictionary with code, display, and entity_id
        
        Returns:
            FHIR CodeSystem resource
        """
        return {
            "resourceType": "CodeSystem",
            "status": "active",
            "content": "complete",
            "concept": [
                {
                    "code": icd_data['code'],
                    "display": icd_data['display'],
                    "extension": [
                        {
                            "url": "http://id.who.int/icd/entity",
                            "valueString": icd_data['entity_id']
                        }
                    ]
                }
            ]
        }
    
    def process_code(self, code: str) -> Dict:
        """
        Main pipeline: Convert ICD-11 code to FHIR CodeSystem
        
        Args:
            code: ICD-11 code (e.g., "1A00")
        
        Returns:
            FHIR CodeSystem JSON
        
        Raises:
            ValueError: If code not found or API error
        """
        # Step 1: Search ICD-11 API
        icd_data = self.search_icd11_code(code)
        
        if not icd_data:
            raise ValueError(f"ICD-11 code '{code}' not found")
        
        # Step 2: Build FHIR CodeSystem
        fhir_json = self.build_fhir_codesystem(icd_data)
        
        return fhir_json


# Convenience function for direct use
def icd11_to_fhir(
    code: str,
    client_id: str,
    client_secret: str
) -> Dict:
    """
    Convert ICD-11 code to FHIR CodeSystem JSON
    
    Args:
        code: ICD-11 code (e.g., "1A00")
        client_id: WHO API client ID
        client_secret: WHO API client secret
    
    Returns:
        FHIR CodeSystem JSON
    
    Example:
        >>> result = icd11_to_fhir("1A00", client_id, client_secret)
        >>> print(json.dumps(result, indent=2))
    """
    pipeline = ICD11FHIRPipeline(client_id, client_secret)
    return pipeline.process_code(code)


# Example usage and testing
if __name__ == "__main__":
    # WHO ICD-11 API credentials
    CLIENT_ID = '0443b40a-5125-4241-b31b-b92c93122f54_a43ba522-ea21-497a-a7d0-27bc684143fe'
    CLIENT_SECRET = 'DaGFcl18CyayKT9jE4Ol31H7P5RQy/Y7GrVcbqvm2QA='
    
    # Initialize pipeline
    pipeline = ICD11FHIRPipeline(CLIENT_ID, CLIENT_SECRET)
    
    # Test with example code
    test_codes = ["1A00", "1A01", "2560"]
    
    for code in test_codes:
        try:
            print(f"\n{'='*60}")
            print(f"Processing ICD-11 Code: {code}")
            print('='*60)
            
            result = pipeline.process_code(code)
            
            print("\nFHIR CodeSystem JSON:")
            print(json.dumps(result, indent=2))
            
            # Extract and display key information
            concept = result['concept'][0]
            entity_id = concept['extension'][0]['valueString']
            
            print(f"\n✓ Code: {concept['code']}")
            print(f"✓ Disease: {concept['display']}")
            print(f"✓ Entity ID: {entity_id}")
            
        except Exception as e:
            print(f"\n✗ Error processing code '{code}': {e}")
    
    print(f"\n{'='*60}")
    print("Pipeline testing complete!")
    print('='*60)
