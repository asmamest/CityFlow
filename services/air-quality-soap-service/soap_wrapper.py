"""
Wrapper REST FastAPI pour le service SOAP Air Quality
Convertit les requêtes REST → SOAP et les réponses SOAP → JSON
"""
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
import logging

from soap_client import SOAPClient

# Configuration
SOAP_SERVICE_URL = os.getenv('SOAP_SERVICE_URL', 'http://localhost:8001')

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Air Quality REST API",
    description="API REST pour le service SOAP Air Quality - Conversion SOAP vers JSON",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Client SOAP
soap_client = SOAPClient(SOAP_SERVICE_URL)


@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "service": "Air Quality REST API",
        "version": "1.0.0",
        "description": "Wrapper REST pour le service SOAP Air Quality",
        "documentation": "/docs",
        "soap_service": SOAP_SERVICE_URL,
        "endpoints": {
            "aqi": "/api/aqi/{zone}",
            "pollutants": "/api/pollutants/{zone}",
            "compare": "/api/compare/{zoneA}/{zoneB}",
            "history": "/api/history/{zone}",
            "filter": "/api/filter/{zone}",
            "health": "/api/health"
        }
    }


@app.get("/api/aqi/{zone}")
def get_aqi(zone: str):
    """
    Récupérer l'AQI (Air Quality Index) pour une zone
    
    **Exemple de réponse:**
    ```json
    {
        "zone": "SUD",
        "aqi": 125,
        "category": "Unhealthy for Sensitive Groups",
        "timestamp": "2025-12-16T23:22:45.569165+00:00",
        "description": "Risque pour les personnes sensibles"
    }
    ```
    """
    try:
        logger.info(f"📥 GET /api/aqi/{zone}")
        result = soap_client.get_aqi(zone)
        logger.info(f"✅ Réponse: AQI={result['aqi']}")
        return result
    except Exception as e:
        logger.error(f"❌ Erreur get_aqi: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pollutants/{zone}")
def get_pollutants(zone: str):
    """
    Récupérer tous les polluants pour une zone
    
    **Exemple de réponse:**
    ```json
    {
        "zone": "SUD",
        "pollutants": [
            {
                "name": "PM2.5",
                "value": 85.7,
                "unit": "µg/m³",
                "timestamp": "2025-12-16T23:22:45.569165+00:00",
                "status": "ALERT"
            },
            ...
        ],
        "timestamp": "2025-12-16T23:22:45.569165+00:00"
    }
    ```
    """
    try:
        logger.info(f"📥 GET /api/pollutants/{zone}")
        result = soap_client.get_pollutants(zone)
        logger.info(f"✅ Réponse: {len(result['pollutants'])} polluants")
        return result
    except Exception as e:
        logger.error(f"❌ Erreur get_pollutants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compare/{zoneA}/{zoneB}")
def compare_zones(zoneA: str, zoneB: str):
    """
    Comparer la qualité de l'air entre deux zones
    
    **Exemple de réponse:**
    ```json
    {
        "zoneA": "NORD",
        "zoneB": "SUD",
        "aqiA": 45,
        "aqiB": 125,
        "cleanest_zone": "NORD",
        "difference": 80,
        "recommendations": "Différence significative. Privilégiez fortement NORD.",
        "timestamp": "2025-12-17T00:48:22.463219"
    }
    ```
    """
    try:
        logger.info(f"📥 GET /api/compare/{zoneA}/{zoneB}")
        result = soap_client.compare_zones(zoneA, zoneB)
        logger.info(f"✅ Réponse: {result['cleanest_zone']} est plus propre")
        return result
    except Exception as e:
        logger.error(f"❌ Erreur compare_zones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{zone}")
def get_history(
    zone: str,
    start_date: str = Query(..., description="Date de début (ISO format: 2025-12-01T00:00:00)"),
    end_date: str = Query(..., description="Date de fin (ISO format: 2025-12-07T23:59:59)"),
    granularity: str = Query('daily', regex='^(hourly|daily)$', description="Granularité: hourly ou daily")
):
    """
    Récupérer l'historique des mesures pour une zone
    
    **Paramètres:**
    - **zone**: Identifiant de la zone (CENTRE, NORD, SUD, EST)
    - **start_date**: Date de début au format ISO (ex: 2025-12-01T00:00:00)
    - **end_date**: Date de fin au format ISO (ex: 2025-12-07T23:59:59)
    - **granularity**: hourly ou daily
    
    **Exemple:**
    ```
    GET /api/history/CENTRE?start_date=2025-12-01T00:00:00&end_date=2025-12-07T23:59:59&granularity=daily
    ```
    
    **Exemple de réponse:**
    ```json
    {
        "zone": "CENTRE",
        "start_date": "2025-12-01T00:00:00",
        "end_date": "2025-12-07T23:59:59",
        "granularity": "daily",
        "data_points": [
            {
                "timestamp": "2025-12-01T00:00:00",
                "aqi": 75,
                "pm25": 35.5,
                "pm10": 55.2,
                ...
            },
            ...
        ]
    }
    ```
    """
    try:
        logger.info(f"📥 GET /api/history/{zone}?start={start_date}&end={end_date}&gran={granularity}")
        result = soap_client.get_history(zone, start_date, end_date, granularity)
        logger.info(f"✅ Réponse: {len(result['data_points'])} points de données")
        return result
    except Exception as e:
        logger.error(f"❌ Erreur get_history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/filter/{zone}")
def filter_pollutants(
    zone: str,
    threshold: float = Query(..., description="Seuil de filtrage (ex: 35.0)")
):
    """
    Filtrer les polluants au-dessus d'un seuil
    
    **Paramètres:**
    - **zone**: Identifiant de la zone
    - **threshold**: Seuil de filtrage (seuls les polluants > threshold sont retournés)
    
    **Exemple:**
    ```
    GET /api/filter/SUD?threshold=35
    ```
    
    **Exemple de réponse:**
    ```json
    {
        "zone": "SUD",
        "threshold": 35.0,
        "pollutants": [
            {
                "name": "PM2.5",
                "value": 85.7,
                "unit": "µg/m³",
                "timestamp": "2025-12-16T23:22:45.569165+00:00",
                "status": "ALERT"
            },
            ...
        ],
        "timestamp": "2025-12-17T00:19:21.048820"
    }
    ```
    """
    try:
        logger.info(f"📥 GET /api/filter/{zone}?threshold={threshold}")
        result = soap_client.filter_pollutants(zone, threshold)
        logger.info(f"✅ Réponse: {len(result['pollutants'])} polluants au-dessus du seuil")
        return result
    except Exception as e:
        logger.error(f"❌ Erreur filter_pollutants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health_check():
    """
    Vérifier l'état de santé du service SOAP
    
    **Exemple de réponse:**
    ```json
    {
        "status": "UP",
        "version": "1.0.0",
        "uptime_seconds": 3600,
        "database_status": "UP",
        "last_check": "2025-12-17T00:48:22.463219"
    }
    ```
    """
    try:
        logger.info(f"📥 GET /api/health")
        result = soap_client.health_check()
        logger.info(f"✅ Health: {result['status']}")
        return result
    except Exception as e:
        logger.error(f"❌ Erreur health_check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/zones")
def list_zones():
    """
    Lister toutes les zones disponibles
    
    **Exemple de réponse:**
    ```json
    {
        "zones": ["CENTRE", "NORD", "SUD", "EST"],
        "count": 4
    }
    ```
    """
    zones = ["CENTRE", "NORD", "SUD", "EST"]
    return {
        "zones": zones,
        "count": len(zones)
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire d'erreurs HTTP personnalisé"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Gestionnaire d'erreurs général"""
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Erreur interne du serveur",
            "details": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('REST_API_PORT', 8002))
    
    logger.info("=" * 60)
    logger.info("🚀 Démarrage du Wrapper REST FastAPI")
    logger.info("=" * 60)
    logger.info(f"📍 Port: {port}")
    logger.info(f"📍 Documentation: http://localhost:{port}/docs")
    logger.info(f"📍 Service SOAP: {SOAP_SERVICE_URL}")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )