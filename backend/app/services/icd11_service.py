"""
ICD-11 API service for diagnostic code lookup and cross-referencing.
"""

import os
import requests
from typing import Dict, Any, List, Optional
from functools import lru_cache
import time


class ICD11Service:
    """Service for interacting with WHO ICD-11 API."""
    
    def __init__(self):
        self.client_id = os.getenv("ICD11_CLIENT_ID")
        self.client_secret = os.getenv("ICD11_CLIENT_SECRET")
        self.base_url = "https://id.who.int/icd"
        self.token_url = "https://icdaccessmanagement.who.int/connect/token"
        self.access_token = None
        self.token_expiry = 0
        
    def _get_access_token(self) -> str:
        """Get or refresh OAuth2 access token."""
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
            
        response = requests.post(
            self.token_url,
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'icdapi_access',
                'grant_type': 'client_credentials'
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.token_expiry = time.time() + data['expires_in'] - 60  # 60s buffer
            return self.access_token
        else:
            raise Exception(f"Failed to get ICD-11 token: {response.status_code}")
    
    @lru_cache(maxsize=100)
    def search_mental_disorders(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search ICD-11 mental and behavioral disorders."""
        try:
            token = self._get_access_token()
            
            # Search in Chapter 06: Mental, behavioural or neurodevelopmental disorders
            response = requests.get(
                f"{self.base_url}/release/11/2024-01/mms/search",
                params={
                    'q': query,
                    'useFlexisearch': 'true',
                    'flatResults': 'true',
                    'chapterFilter': '06'  # Mental disorders chapter
                },
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json',
                    'API-Version': 'v2',
                    'Accept-Language': 'en'
                }
            )
            
            if response.status_code != 200:
                print(f"ICD-11 search error: {response.status_code}")
                return []
            
            results = response.json().get('destinationEntities', [])[:max_results]
            
            # Format results
            formatted = []
            for result in results:
                formatted.append({
                    'icd_code': result.get('theCode', ''),
                    'title': result.get('title', ''),
                    'url': result.get('id', ''),
                    'match_score': result.get('score', 0)
                })
            
            return formatted
            
        except Exception as e:
            print(f"ICD-11 search error: {e}")
            return []
    
    @lru_cache(maxsize=100)
    def get_entity_details(self, entity_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an ICD-11 entity."""
        try:
            token = self._get_access_token()
            
            response = requests.get(
                entity_url,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json',
                    'API-Version': 'v2',
                    'Accept-Language': 'en'
                }
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            return {
                'icd_code': data.get('code', ''),
                'title': data.get('title', {}).get('@value', ''),
                'definition': data.get('definition', {}).get('@value', ''),
                'diagnostic_criteria': data.get('diagnosticCriteria', {}).get('@value', ''),
                'inclusions': [inc.get('label', {}).get('@value', '') for inc in data.get('inclusion', [])],
                'exclusions': [exc.get('label', {}).get('@value', '') for exc in data.get('exclusion', [])],
            }
            
        except Exception as e:
            print(f"ICD-11 entity details error: {e}")
            return None


# Global instance
icd11_service = ICD11Service()
