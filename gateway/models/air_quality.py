"""Modèles Pydantic pour le service Qualité de l'Air"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AQIRequest(BaseModel):
    """Requête pour obtenir l'AQI d'une zone"""
    zone: str = Field(..., description="Nom de la zone", example="downtown")

class AQIResult(BaseModel):
    """Résultat de l'indice de qualité de l'air"""
    zone: str
    aqi: int = Field(..., description="Air Quality Index (0-500)")
    category: str = Field(..., description="Catégorie: Good, Moderate, Unhealthy, etc.")
    timestamp: str
    description: str

class Pollutant(BaseModel):
    """Données d'un polluant"""
    name: str = Field(..., description="Nom du polluant (PM2.5, PM10, O3, etc.)")
    value: float = Field(..., description="Valeur mesurée")
    unit: str = Field(..., description="Unité de mesure (µg/m³, ppm)")
    timestamp: str
    status: str = Field(..., description="Status: normal, warning, danger")

class PollutantsRequest(BaseModel):
    """Requête pour obtenir les polluants"""
    zone: str = Field(..., description="Nom de la zone")

class CompareZonesRequest(BaseModel):
    """Requête pour comparer deux zones"""
    zone_a: str = Field(..., description="Première zone")
    zone_b: str = Field(..., description="Deuxième zone")

class ZoneComparison(BaseModel):
    """Résultat de comparaison entre deux zones"""
    zone_a: str
    zone_b: str
    aqi_zone_a: int
    aqi_zone_b: int
    difference: int
    better_zone: str
    timestamp: str

class HistoryRequest(BaseModel):
    """Requête pour l'historique"""
    zone: str = Field(..., description="Nom de la zone")
    start_date: str = Field(..., description="Date de début (ISO format)")
    end_date: str = Field(..., description="Date de fin (ISO format)")
    granularity: str = Field(default="daily", description="Granularité: hourly, daily, weekly")

class HistoricalData(BaseModel):
    """Données historiques"""
    timestamp: str
    aqi: int
    category: str

class FilterPollutantsRequest(BaseModel):
    """Requête pour filtrer les polluants"""
    zone: str = Field(..., description="Nom de la zone")
    threshold: float = Field(..., description="Seuil de filtrage", ge=0)