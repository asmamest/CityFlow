"""Client SOAP pour le service Qualité de l'Air"""
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
from  config import settings
from  utils import logger, handle_soap_error, ServiceError

class AirQualitySoapClient:
    """Client SOAP pour interroger le service Qualité de l'Air"""
    
    def __init__(self):
        self.wsdl_url = settings.AIR_QUALITY_WSDL_URL
        self.service_url = settings.AIR_QUALITY_SERVICE_URL
        self.timeout = settings.SOAP_TIMEOUT
        
        # Configuration du transport avec timeout
        session = Session()
        session.timeout = self.timeout
        transport = Transport(session=session)
        
        # Configuration Zeep
        zeep_settings = Settings(
            strict=False,
            xml_huge_tree=True,
            xsd_ignore_sequence_order=True
        )
        
        try:
            self.client = Client(
                wsdl=self.wsdl_url,
                settings=zeep_settings,
                transport=transport
            )
            self.service = self.client.service
            logger.info(f"SOAP Client initialized with WSDL: {self.wsdl_url}")
        except Exception as e:
            logger.error(f"Failed to initialize SOAP client: {str(e)}")
            raise ServiceError(
                service="air-quality-soap-service",
                message=f"Impossible d'initialiser le client SOAP: {str(e)}",
                status_code=503
            )
    
    def _serialize_response(self, response: Any) -> Dict[str, Any]:
        """Convertit une réponse SOAP en dictionnaire JSON"""
        if hasattr(response, '__dict__'):
            result = {}
            for key, value in response.__dict__.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif hasattr(value, '__dict__'):
                    result[key] = self._serialize_response(value)
                elif isinstance(value, list):
                    result[key] = [
                        self._serialize_response(item) if hasattr(item, '__dict__') else item
                        for item in value
                    ]
                else:
                    result[key] = value
            return result
        return response
    
    async def get_aqi(self, zone: str) -> Dict[str, Any]:
        """Obtient l'indice de qualité de l'air pour une zone"""
        try:
            logger.info(f"SOAP Request: GetAQI(zone={zone})")
            response = self.service.GetAQI(zone=zone)
            result = self._serialize_response(response)
            logger.info(f"SOAP Response: AQI for {zone}")
            return result
        except Exception as e:
            logger.error(f"SOAP Error in GetAQI: {str(e)}")
            raise handle_soap_error(e, "air-quality-soap-service")
    
    async def get_pollutants(self, zone: str) -> List[Dict[str, Any]]:
        """Obtient les niveaux de polluants pour une zone"""
        try:
            logger.info(f"SOAP Request: GetPollutants(zone={zone})")
            response = self.service.GetPollutants(zone=zone)
            
            if isinstance(response, list):
                result = [self._serialize_response(item) for item in response]
            else:
                result = [self._serialize_response(response)]
            
            logger.info(f"SOAP Response: Pollutants for {zone}")
            return result
        except Exception as e:
            logger.error(f"SOAP Error in GetPollutants: {str(e)}")
            raise handle_soap_error(e, "air-quality-soap-service")
    
    async def compare_zones(self, zone_a: str, zone_b: str) -> Dict[str, Any]:
        """Compare la qualité de l'air entre deux zones"""
        try:
            logger.info(f"SOAP Request: CompareZones({zone_a}, {zone_b})")
            response = self.service.CompareZones(zoneA=zone_a, zoneB=zone_b)
            result = self._serialize_response(response)
            logger.info(f"SOAP Response: Comparison {zone_a} vs {zone_b}")
            return result
        except Exception as e:
            logger.error(f"SOAP Error in CompareZones: {str(e)}")
            raise handle_soap_error(e, "air-quality-soap-service")
    
    async def get_history(
        self,
        zone: str,
        start_date: str,
        end_date: str,
        granularity: str = "daily"
    ) -> List[Dict[str, Any]]:
        """Obtient l'historique de la qualité de l'air"""
        try:
            logger.info(
                f"SOAP Request: GetHistory(zone={zone}, "
                f"start={start_date}, end={end_date})"
            )
            response = self.service.GetHistory(
                zone=zone,
                startDate=start_date,
                endDate=end_date,
                granularity=granularity
            )
            
            if isinstance(response, list):
                result = [self._serialize_response(item) for item in response]
            else:
                result = [self._serialize_response(response)]
            
            logger.info(f"SOAP Response: History for {zone}")
            return result
        except Exception as e:
            logger.error(f"SOAP Error in GetHistory: {str(e)}")
            raise handle_soap_error(e, "air-quality-soap-service")
    
    async def filter_pollutants(
        self,
        zone: str,
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Filtre les polluants au-dessus d'un seuil"""
        try:
            logger.info(
                f"SOAP Request: FilterPollutants(zone={zone}, threshold={threshold})"
            )
            response = self.service.FilterPollutants(
                zone=zone,
                threshold=threshold
            )
            
            if isinstance(response, list):
                result = [self._serialize_response(item) for item in response]
            else:
                result = [self._serialize_response(response)]
            
            logger.info(f"SOAP Response: Filtered pollutants for {zone}")
            return result
        except Exception as e:
            logger.error(f"SOAP Error in FilterPollutants: {str(e)}")
            raise handle_soap_error(e, "air-quality-soap-service")
    
    async def health_check(self) -> bool:
        """Vérifie la santé du service SOAP"""
        try:
            self.service.HealthCheck()
            return True
        except:
            return False