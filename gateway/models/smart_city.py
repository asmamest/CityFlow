"""Modèles Pydantic pour le workflow Smart City"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PlanTripRequest(BaseModel):
    """Requête pour planifier un trajet"""
    zone_depart: str = Field(..., description="Zone de départ", example="downtown")
    zone_arrivee: str = Field(..., description="Zone d'arrivée", example="industrial")
    heure_depart: str = Field(
        ...,
        description="Heure de départ souhaitée (HH:MM)",
        pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
        example="14:30"
    )
    preferences: Optional[List[str]] = Field(
        default=["metro", "bus"],
        description="Types de transport préférés"
    )

class AirQualityInfo(BaseModel):
    """Informations sur la qualité de l'air"""
    zone: str
    aqi: int
    category: str
    description: str
    timestamp: str
    recommendation: str

class TransportInfo(BaseModel):
    """Informations sur les transports"""
    ligne: str
    type_transport: str
    etat_trafic: str
    disponibilite: str
    horaires_prochain_passage: List[str]

class AlertInfo(BaseModel):
    """Informations sur les alertes d'urgence"""
    alert_id: str
    type: str
    description: str
    priority: str
    zone: str
    created_at: str

class EventInfo(BaseModel):
    """Informations sur les événements urbains"""
    event_id: str
    name: str
    description: str
    priority: str
    status: str
    zone: str
    date: str

class RouteRecommendation(BaseModel):
    """Recommandation d'itinéraire"""
    type: str = Field(..., description="direct, alternatif")
    description: str
    raison: Optional[str] = None
    lignes_suggerees: List[str]
    duree_estimee: str

class TripAnalysis(BaseModel):
    """Analyse complète du trajet"""
    zone_depart: str
    zone_arrivee: str
    heure_demandee: str
    
    # Qualité de l'air
    air_quality_depart: AirQualityInfo
    air_quality_arrivee: AirQualityInfo
    air_quality_comparison: str
    
    # Transports disponibles
    transports_disponibles: List[TransportInfo]
    
    # Alertes d'urgence
    alertes_actives: List[AlertInfo]
    niveau_alerte_global: str
    
    # Événements urbains
    evenements_impactants: List[EventInfo]
    
    # Recommandations
    recommandation_principale: RouteRecommendation
    recommandations_alternatives: List[RouteRecommendation]
    
    # Synthèse
    conseil_principal: str
    niveau_confort: str  # excellent, bon, moyen, difficile
    timestamp: str

class PlanTripResponse(BaseModel):
    """Réponse complète du planning de trajet"""
    success: bool
    message: str
    analysis: Optional[TripAnalysis] = None
    warnings: List[str] = []
    processing_time_ms: float

class HealthCheckResponse(BaseModel):
    """Réponse du health check"""
    status: str
    services: Dict[str, bool]
    timestamp: str
    version: str