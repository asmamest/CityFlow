"""Routers FastAPI pour l'API Gateway"""
from .mobility import router as mobility_router
from .air_quality import router as air_quality_router
from .emergency import router as emergency_router
from .urban_events import router as urban_events_router
from .smart_city import router as smart_city_router

__all__ = [
    "mobility_router",
    "air_quality_router",
    "emergency_router",
    "urban_events_router",
    "smart_city_router"
]