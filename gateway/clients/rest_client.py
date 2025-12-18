"""Client REST pour le service Mobilité"""
import httpx
from typing import Dict, Any, Optional, List
from  config import settings
from  utils import logger, handle_rest_error, ServiceError

class MobilityRestClient:
    """Client REST pour interroger le service Mobilité"""
    
    def __init__(self):
        self.base_url = settings.MOBILITY_SERVICE_URL
        self.timeout = settings.REST_TIMEOUT
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True
        )
    
    async def close(self):
        """Ferme le client HTTP"""
        await self.client.aclose()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Effectue une requête HTTP générique"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"REST Request: {method} {url}")
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"REST Response: {response.status_code}")
            return data
            
        except Exception as e:
            logger.error(f"REST Error: {str(e)}")
            raise handle_rest_error(e, "mobility-service")
    
    async def get_horaires(self, ligne: str) -> Dict[str, Any]:
        """Récupère les horaires d'une ligne"""
        return await self._make_request("GET", f"/horaires/{ligne}")
    
    async def get_trafic(self) -> Dict[str, Any]:
        """Récupère l'état du trafic"""
        return await self._make_request("GET", "/trafic")
    
    async def get_disponibilite(self) -> Dict[str, Any]:
        """Récupère la disponibilité des véhicules"""
        return await self._make_request("GET", "/disponibilite")
    
    async def get_lignes(self) -> List[Dict[str, Any]]:
        """Liste toutes les lignes"""
        return await self._make_request("GET", "/lignes")
    
    async def get_ligne(self, ligne_id: str) -> Dict[str, Any]:
        """Récupère une ligne par ID"""
        return await self._make_request("GET", f"/lignes/{ligne_id}")
    
    async def create_ligne(self, ligne_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle ligne"""
        return await self._make_request(
            "POST",
            "/lignes",
            json=ligne_data
        )
    
    async def update_ligne(
        self,
        ligne_id: str,
        ligne_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Met à jour une ligne"""
        return await self._make_request(
            "PUT",
            f"/lignes/{ligne_id}",
            json=ligne_data
        )
    
    async def delete_ligne(self, ligne_id: str) -> Dict[str, Any]:
        """Supprime une ligne"""
        return await self._make_request("DELETE", f"/lignes/{ligne_id}")
    
    async def health_check(self) -> bool:
        """Vérifie la santé du service"""
        try:
            await self._make_request("GET", "/health")
            return True
        except:
            return False