"""Router FastAPI pour le service Qualité de l'Air (SOAP)"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from  clients import AirQualitySoapClient
from  models.air_quality import (
    AQIRequest, AQIResult, Pollutant,
    CompareZonesRequest, HistoryRequest, FilterPollutantsRequest
)
from  utils import logger

router = APIRouter(prefix="/air", tags=["Qualité de l'Air"])

# Dependency pour le client SOAP
async def get_air_quality_client():
    return AirQualitySoapClient()

@router.get("/", summary="Page d'accueil du service Qualité de l'Air")
async def air_quality_home():
    """Informations sur le service Qualité de l'Air"""
    return {
        "service": "Qualité de l'Air",
        "version": "1.0.0",
        "protocol": "SOAP",
        "description": "Service de surveillance de la qualité de l'air",
        "endpoints": [
            "/air/aqi/{zone}",
            "/air/pollutants/{zone}",
            "/air/compare",
            "/air/history",
            "/air/filter"
        ]
    }

@router.get(
    "/aqi/{zone}",
    response_model=dict,
    summary="Indice de qualité de l'air (AQI)"
)
async def get_aqi(
    zone: str,
    client: AirQualitySoapClient = Depends(get_air_quality_client)
):
    """
    Récupère l'indice de qualité de l'air (AQI) pour une zone.
    
    - **zone**: Nom de la zone (ex: downtown, park, industrial)
    
    Catégories AQI:
    - Good (0-50)
    - Moderate (51-100)
    - Unhealthy for Sensitive Groups (101-150)
    - Unhealthy (151-200)
    - Very Unhealthy (201-300)
    - Hazardous (301-500)
    """
    logger.info(f"Gateway: Getting AQI for zone {zone}")
    result = await client.get_aqi(zone)
    return result

@router.get(
    "/pollutants/{zone}",
    response_model=List[dict],
    summary="Niveaux de polluants"
)
async def get_pollutants(
    zone: str,
    client: AirQualitySoapClient = Depends(get_air_quality_client)
):
    """
    Récupère les niveaux de tous les polluants pour une zone.
    
    - **zone**: Nom de la zone
    
    Polluants surveillés: PM2.5, PM10, O3, NO2, SO2, CO
    """
    logger.info(f"Gateway: Getting pollutants for zone {zone}")
    result = await client.get_pollutants(zone)
    return result

@router.post(
    "/compare",
    response_model=dict,
    summary="Comparer deux zones"
)
async def compare_zones(
    request: CompareZonesRequest,
    client: AirQualitySoapClient = Depends(get_air_quality_client)
):
    """
    Compare la qualité de l'air entre deux zones.
    
    - **zone_a**: Première zone à comparer
    - **zone_b**: Deuxième zone à comparer
    """
    logger.info(f"Gateway: Comparing zones {request.zone_a} vs {request.zone_b}")
    result = await client.compare_zones(request.zone_a, request.zone_b)
    return result

@router.post(
    "/history",
    response_model=List[dict],
    summary="Historique de la qualité de l'air"
)
async def get_history(
    request: HistoryRequest,
    client: AirQualitySoapClient = Depends(get_air_quality_client)
):
    """
    Récupère l'historique de la qualité de l'air pour une zone.
    
    - **zone**: Nom de la zone
    - **start_date**: Date de début (ISO format: YYYY-MM-DD)
    - **end_date**: Date de fin (ISO format: YYYY-MM-DD)
    - **granularity**: hourly, daily, weekly (défaut: daily)
    """
    logger.info(
        f"Gateway: Getting history for {request.zone} "
        f"from {request.start_date} to {request.end_date}"
    )
    result = await client.get_history(
        request.zone,
        request.start_date,
        request.end_date,
        request.granularity
    )
    return result

@router.post(
    "/filter",
    response_model=List[dict],
    summary="Filtrer les polluants par seuil"
)
async def filter_pollutants(
    request: FilterPollutantsRequest,
    client: AirQualitySoapClient = Depends(get_air_quality_client)
):
    """
    Filtre les polluants dépassant un seuil donné.
    
    - **zone**: Nom de la zone
    - **threshold**: Seuil de filtrage (valeur minimale)
    """
    logger.info(
        f"Gateway: Filtering pollutants for {request.zone} "
        f"with threshold {request.threshold}"
    )
    result = await client.filter_pollutants(request.zone, request.threshold)
    return result

@router.get(
    "/zones",
    summary="Liste des zones disponibles"
)
async def list_zones():
    """
    Liste toutes les zones pour lesquelles des données sont disponibles.
    
    Note: Cette liste est indicative et peut varier selon le service SOAP.
    """
    return {
        "zones": [
            {"id": "downtown", "name": "Centre-ville", "description": "Zone urbaine dense"},
            {"id": "park", "name": "Parc Central", "description": "Espace vert"},
            {"id": "industrial", "name": "Zone Industrielle", "description": "Secteur industriel"},
            {"id": "residential", "name": "Zone Résidentielle", "description": "Quartier résidentiel"},
            {"id": "suburban", "name": "Banlieue", "description": "Zone périurbaine"}
        ]
    }