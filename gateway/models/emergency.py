"""Modèles Pydantic pour le service Urgences"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class AlertType(str, Enum):
    """Types d'alertes d'urgence"""
    ACCIDENT = "ACCIDENT"
    FIRE = "FIRE"
    AMBULANCE_REQUEST = "AMBULANCE_REQUEST"
    MEDICAL_EMERGENCY = "MEDICAL_EMERGENCY"
    NATURAL_DISASTER = "NATURAL_DISASTER"
    SECURITY_THREAT = "SECURITY_THREAT"
    PUBLIC_HEALTH = "PUBLIC_HEALTH"

class Priority(str, Enum):
    """Niveaux de priorité"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, Enum):
    """Statuts des alertes"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"

class Location(BaseModel):
    """Localisation géographique"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str
    city: str
    zone: str

class CreateAlertRequest(BaseModel):
    """Requête pour créer une alerte"""
    type: AlertType
    description: str = Field(..., min_length=10, max_length=1000)
    location: Location
    priority: Priority
    reporter_name: str = Field(..., min_length=2)
    reporter_phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    affected_people: int = Field(default=0, ge=0)

class AlertResponse(BaseModel):
    """Réponse contenant une alerte"""
    alert_id: str
    type: str
    description: str
    location: Location
    priority: str
    status: str
    reporter_name: str
    reporter_phone: str
    affected_people: int
    created_at: str
    updated_at: str
    assigned_team: Optional[str] = None
    notes: Optional[str] = None

class GetActiveAlertsRequest(BaseModel):
    """Requête pour obtenir les alertes actives"""
    zone: str
    alert_type: Optional[AlertType] = None
    min_priority: Optional[Priority] = None

class UpdateAlertStatusRequest(BaseModel):
    """Requête pour mettre à jour le statut"""
    alert_id: str
    new_status: AlertStatus
    assigned_team: Optional[str] = None
    notes: Optional[str] = None

class AlertHistoryRequest(BaseModel):
    """Requête pour l'historique des alertes"""
    zone: Optional[str] = None
    alert_type: Optional[AlertType] = None
    start_date: Optional[int] = Field(None, description="Timestamp Unix")
    end_date: Optional[int] = Field(None, description="Timestamp Unix")
    limit: int = Field(default=100, ge=1, le=1000)

class AlertHistoryResponse(BaseModel):
    """Réponse d'historique avec statistiques"""
    alerts: List[AlertResponse]
    total_count: int
    statistics: Dict[str, int]