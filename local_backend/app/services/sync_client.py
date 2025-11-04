"""
Sync client for communicating with Render backend
"""
import os
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SyncClient:
    """Client for syncing with Render backend"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize sync client
        
        Args:
            base_url: Render backend URL (default from env)
        """
        self.base_url = base_url or os.getenv(
            "RENDER_BACKEND_URL",
            "https://clarity-sync.onrender.com"
        )
        self.timeout = 30.0
    
    async def push_notebooks(
        self,
        user_id: str,
        notebooks: List[Dict[str, Any]],
        access_token: str,
        last_sync: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Push notebooks to cloud
        
        Args:
            user_id: Auth0 user ID
            notebooks: List of notebook data
            access_token: JWT access token
            last_sync: Last sync timestamp
            
        Returns:
            Response with sync status
        """
        url = f"{self.base_url}/api/sync"
        
        payload = {
            "user_id": user_id,
            "notebooks": notebooks,
            "last_sync": last_sync.isoformat() if last_sync else None
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Synced {result.get('synced_count', 0)} notebooks for user {user_id}")
                return result
        
        except httpx.HTTPError as e:
            logger.error(f"Sync push failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "synced_count": 0,
                "conflicts": []
            }
    
    async def pull_notebooks(
        self,
        user_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Pull notebooks from cloud
        
        Args:
            user_id: Auth0 user ID
            access_token: JWT access token
            
        Returns:
            Response with notebooks and last sync time
        """
        url = f"{self.base_url}/api/sync"
        params = {"user_id": user_id}
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Pulled {len(result.get('notebooks', []))} notebooks for user {user_id}")
                return result
        
        except httpx.HTTPError as e:
            logger.error(f"Sync pull failed: {e}")
            return {
                "notebooks": [],
                "last_sync": None
            }


# Global instance
sync_client = SyncClient()
