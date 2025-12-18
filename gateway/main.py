"""
🏙️ SMART CITY API GATEWAY
Application FastAPI principale - Orchestration de microservices multi-protocoles
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from config import settings, validate_config
from utils import (
    logger,
    ServiceError,
    service_error_handler,
    http_exception_handler,
    general_exception_handler
)
from routers import (
    mobility_router,
    air_quality_router,
    emergency_router,
    urban_events_router,
    smart_city_router
)

# ============================================================
# LIFECYCLE EVENTS
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 Starting Smart City API Gateway")
    logger.info("=" * 60)
    
    try:
        validate_config()
        logger.info("✅ Configuration validated")
        logger.info(f"📡 Mobility Service: {settings.MOBILITY_SERVICE_URL}")
        logger.info(f"🌫️ Air Quality Service: {settings.AIR_QUALITY_WSDL_URL}")
        logger.info(f"🚨 Emergency Service: {settings.EMERGENCY_GRPC_HOST}:{settings.EMERGENCY_GRPC_PORT}")
        logger.info(f"📅 Urban Events Service: {settings.URBAN_EVENTS_GRAPHQL_URL}")
    except Exception as e:
        logger.error(f"❌ Configuration error: {str(e)}")
        raise
    
    logger.info("=" * 60)
    logger.info(f"✨ Gateway is ready on port {settings.PORT}")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 Shutting down Smart City API Gateway")
    logger.info("=" * 60)

# ============================================================
# APPLICATION FASTAPI
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## 🏙️ Smart City API Gateway
    
    Gateway unifiée pour l'orchestration de microservices multi-protocoles.
    
    ### 🎯 Services intégrés:
    
    * **🚗 Mobilité** (REST) - Gestion des transports en commun
    * **🌫️ Qualité de l'Air** (SOAP) - Surveillance environnementale
    * **🚨 Urgences** (gRPC) - Alertes et interventions d'urgence
    * **📅 Événements Urbains** (GraphQL) - Gestion des événements de la ville
    
    ### 🔗 Workflow intelligent:
    
    * **`POST /smart-city/plan-trip`** - Planification de trajet avec analyse multi-services
    
    ### 📚 Documentation:
    
    * Swagger UI: `/docs`
    * ReDoc: `/redoc`
    * OpenAPI Schema: `/openapi.json`
    
    ---
    
    Développé avec ❤️ pour une ville plus intelligente
    """,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# ============================================================
# MIDDLEWARE
# ============================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes HTTP"""
    start_time = time.time()
    
    # Log de la requête
    logger.info(f"📥 {request.method} {request.url.path}")
    
    # Traitement de la requête
    response = await call_next(request)
    
    # Log de la réponse
    duration = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration * 1000:.2f}ms"
    )
    
    return response

# ============================================================
# EXCEPTION HANDLERS
# ============================================================

app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ============================================================
# ROUTES PRINCIPALES
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """Page d'accueil de l'API Gateway"""
    return {
        "message": "🏙️ Welcome to Smart City API Gateway",
        "version": settings.APP_VERSION,
        "status": "operational",
        "services": {
            "mobility": {
                "protocol": "REST",
                "base_path": "/mobility",
                "description": "Service de gestion des transports en commun"
            },
            "air_quality": {
                "protocol": "SOAP",
                "base_path": "/air",
                "description": "Service de surveillance de la qualité de l'air"
            },
            "emergency": {
                "protocol": "gRPC",
                "base_path": "/emergency",
                "description": "Service de gestion des alertes d'urgence"
            },
            "urban_events": {
                "protocol": "GraphQL",
                "base_path": "/urban",
                "description": "Service de gestion des événements urbains"
            },
            "smart_city": {
                "protocol": "Orchestration",
                "base_path": "/smart-city",
                "description": "Workflows métier intelligents"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

@app.get("/health", tags=["Health"])
async def gateway_health():
    """Health check de la Gateway (sans vérifier les services)"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }

@app.get("/info", tags=["Info"])
async def gateway_info():
    """Informations détaillées sur la Gateway"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug_mode": settings.DEBUG,
        "configuration": {
            "mobility_service": settings.MOBILITY_SERVICE_URL,
            "air_quality_service": settings.AIR_QUALITY_WSDL_URL,
            "emergency_service": f"{settings.EMERGENCY_GRPC_HOST}:{settings.EMERGENCY_GRPC_PORT}",
            "urban_events_service": settings.URBAN_EVENTS_GRAPHQL_URL
        },
        "timeouts": {
            "rest": f"{settings.REST_TIMEOUT}s",
            "soap": f"{settings.SOAP_TIMEOUT}s",
            "grpc": f"{settings.GRPC_TIMEOUT}s",
            "graphql": f"{settings.GRAPHQL_TIMEOUT}s"
        }
    }

# ============================================================
# INCLUSION DES ROUTERS
# ============================================================

app.include_router(mobility_router)
app.include_router(air_quality_router)
app.include_router(emergency_router)
app.include_router(urban_events_router)
app.include_router(smart_city_router)

# ============================================================
# POINT D'ENTRÉE
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )