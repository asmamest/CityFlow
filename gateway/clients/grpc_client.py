"""Client gRPC pour le service Urgences"""
import grpc
from typing import Dict, Any, List, Optional
from  config import settings
from  utils import logger, handle_grpc_error, ServiceError

# Import des fichiers proto générés
try:
    from  protos import emergency_pb2, emergency_pb2_grpc
except ImportError:
    logger.error("Fichiers proto non trouvés. Exécutez la génération des stubs gRPC.")
    raise

class EmergencyGrpcClient:
    """Client gRPC pour interroger le service Urgences"""
    
    def __init__(self):
        self.host = settings.EMERGENCY_GRPC_HOST
        self.port = settings.EMERGENCY_GRPC_PORT
        self.timeout = settings.GRPC_TIMEOUT
        self.address = f"{self.host}:{self.port}"
        
        # Création du channel gRPC
        self.channel = grpc.aio.insecure_channel(self.address)
        self.stub = emergency_pb2_grpc.EmergencyAlertServiceStub(self.channel)
        
        logger.info(f"gRPC Client initialized: {self.address}")
    
    async def close(self):
        """Ferme le channel gRPC"""
        await self.channel.close()
    
    def _alert_to_dict(self, alert: emergency_pb2.AlertResponse) -> Dict[str, Any]:
        """Convertit un message gRPC AlertResponse en dictionnaire"""
        return {
            "alert_id": alert.alert_id,
            "type": emergency_pb2.AlertType.Name(alert.type),
            "description": alert.description,
            "location": {
                "latitude": alert.location.latitude,
                "longitude": alert.location.longitude,
                "address": alert.location.address,
                "city": alert.location.city,
                "zone": alert.location.zone
            },
            "priority": emergency_pb2.Priority.Name(alert.priority),
            "status": emergency_pb2.AlertStatus.Name(alert.status),
            "reporter_name": alert.reporter_name,
            "reporter_phone": alert.reporter_phone,
            "affected_people": alert.affected_people,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at,
            "assigned_team": alert.assigned_team,
            "notes": alert.notes
        }
    
    async def create_alert(
        self,
        alert_type: str,
        description: str,
        location: Dict[str, Any],
        priority: str,
        reporter_name: str,
        reporter_phone: str,
        affected_people: int = 0
    ) -> Dict[str, Any]:
        """Crée une nouvelle alerte"""
        try:
            logger.info(f"gRPC Request: CreateAlert(type={alert_type})")
            
            # Construction de la requête
            location_msg = emergency_pb2.Location(
                latitude=location.get("latitude", 0.0),
                longitude=location.get("longitude", 0.0),
                address=location.get("address", ""),
                city=location.get("city", ""),
                zone=location.get("zone", "")
            )
            
            request = emergency_pb2.AlertRequest(
                type=getattr(emergency_pb2.AlertType, alert_type),
                description=description,
                location=location_msg,
                priority=getattr(emergency_pb2.Priority, priority),
                reporter_name=reporter_name,
                reporter_phone=reporter_phone,
                affected_people=affected_people
            )
            
            response = await self.stub.CreateAlert(request, timeout=self.timeout)
            result = self._alert_to_dict(response)
            
            logger.info(f"gRPC Response: Alert created {response.alert_id}")
            return result
            
        except grpc.RpcError as e:
            logger.error(f"gRPC Error in CreateAlert: {e.details()}")
            raise handle_grpc_error(e, "emergency-grpc")
    
    async def get_active_alerts(
        self,
        zone: str,
        alert_type: Optional[str] = None,
        min_priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Récupère les alertes actives d'une zone"""
        try:
            logger.info(f"gRPC Request: GetActiveAlerts(zone={zone})")
            
            request = emergency_pb2.ZoneRequest(zone=zone)
            
            if alert_type:
                request.type = getattr(emergency_pb2.AlertType, alert_type)
            if min_priority:
                request.min_priority = getattr(emergency_pb2.Priority, min_priority)
            
            response = await self.stub.GetActiveAlerts(request, timeout=self.timeout)
            
            alerts = [self._alert_to_dict(alert) for alert in response.alerts]
            
            logger.info(f"gRPC Response: {len(alerts)} active alerts in {zone}")
            return alerts
            
        except grpc.RpcError as e:
            logger.error(f"gRPC Error in GetActiveAlerts: {e.details()}")
            raise handle_grpc_error(e, "emergency-grpc")
    
    async def update_alert_status(
        self,
        alert_id: str,
        new_status: str,
        assigned_team: str = "",
        notes: str = ""
    ) -> Dict[str, Any]:
        """Met à jour le statut d'une alerte"""
        try:
            logger.info(f"gRPC Request: UpdateAlertStatus(alert_id={alert_id})")
            
            request = emergency_pb2.StatusUpdateRequest(
                alert_id=alert_id,
                new_status=getattr(emergency_pb2.AlertStatus, new_status),
                assigned_team=assigned_team,
                notes=notes
            )
            
            response = await self.stub.UpdateAlertStatus(request, timeout=self.timeout)
            result = self._alert_to_dict(response)
            
            logger.info(f"gRPC Response: Alert {alert_id} updated")
            return result
            
        except grpc.RpcError as e:
            logger.error(f"gRPC Error in UpdateAlertStatus: {e.details()}")
            raise handle_grpc_error(e, "emergency-grpc")
    
    async def get_alert_history(
        self,
        zone: Optional[str] = None,
        alert_type: Optional[str] = None,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Récupère l'historique des alertes"""
        try:
            logger.info(f"gRPC Request: GetAlertHistory(zone={zone})")
            
            request = emergency_pb2.HistoryRequest(limit=limit)
            
            if zone:
                request.zone = zone
            if alert_type:
                request.type = getattr(emergency_pb2.AlertType, alert_type)
            if start_date:
                request.start_date = start_date
            if end_date:
                request.end_date = end_date
            
            response = await self.stub.GetAlertHistory(request, timeout=self.timeout)
            
            alerts = [self._alert_to_dict(alert) for alert in response.alerts]
            
            result = {
                "alerts": alerts,
                "total_count": response.total_count,
                "statistics": dict(response.statistics)
            }
            
            logger.info(f"gRPC Response: {len(alerts)} alerts in history")
            return result
            
        except grpc.RpcError as e:
            logger.error(f"gRPC Error in GetAlertHistory: {e.details()}")
            raise handle_grpc_error(e, "emergency-grpc")
    
    async def health_check(self) -> bool:
        """Vérifie la santé du service gRPC"""
        try:
            request = emergency_pb2.HealthCheckRequest()
            await self.stub.HealthCheck(request, timeout=5)
            return True
        except:
            return False