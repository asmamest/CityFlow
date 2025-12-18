"""Modèles Pydantic pour l'API Gateway"""
from .mobility import *
from .air_quality import *
from .emergency import *
from .urban_events import *
from .smart_city import *

__all__ = [
    # Mobility
    "LigneCreate", "LigneUpdate", "LigneResponse",
    "HorairesResponse", "TraficResponse", "DisponibiliteResponse",
    
    # Air Quality
    "AQIRequest", "AQIResult", "Pollutant",
    "CompareZonesRequest", "HistoryRequest",
    
    # Emergency
    "CreateAlertRequest", "AlertResponse",
    "GetActiveAlertsRequest", "UpdateAlertStatusRequest",
    "AlertHistoryRequest", "AlertHistoryResponse",
    
    # Urban Events
    "Zone", "EventType", "Event",
    "CreateEventRequest", "UpdateEventRequest",
    
    # Smart City
    "PlanTripRequest", "PlanTripResponse", "TripAnalysis",
    "HealthCheckResponse"
]