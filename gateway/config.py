"""Configuration centralisée de l'API Gateway"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Paramètres de configuration"""
    
    # API Gateway
    APP_NAME: str = "Smart City API Gateway"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    
    # Service REST - Mobilité
    MOBILITY_SERVICE_URL: str = os.getenv(
        "MOBILITY_SERVICE_URL", 
        "http://mobility-service:8000"
    )
    
    # Service SOAP - Qualité de l'air
    AIR_QUALITY_WSDL_URL: str = os.getenv(
        "AIR_QUALITY_WSDL_URL",
        "http://air-quality-soap-service:8000/?wsdl"
    )
    AIR_QUALITY_SERVICE_URL: str = os.getenv(
        "AIR_QUALITY_SERVICE_URL",
        "http://air-quality-soap-service:8000/"
    )
    
    # Service gRPC - Urgences
    EMERGENCY_GRPC_HOST: str = os.getenv(
        "EMERGENCY_GRPC_HOST",
        "emergency-grpc"
    )
    EMERGENCY_GRPC_PORT: int = int(os.getenv("EMERGENCY_GRPC_PORT", "50051"))
    
    # Service GraphQL - Événements urbains
    URBAN_EVENTS_GRAPHQL_URL: str = os.getenv(
        "URBAN_EVENTS_GRAPHQL_URL",
        "http://urban-events-graphql:8004/graphql"
    )
    
    # Timeouts (en secondes)
    REST_TIMEOUT: int = 10
    SOAP_TIMEOUT: int = 15
    GRPC_TIMEOUT: int = 10
    GRAPHQL_TIMEOUT: int = 10
    
    # Retry
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Validation des URLs au démarrage
def validate_config():
    """Valide la configuration au démarrage"""
    required_fields = [
        ("MOBILITY_SERVICE_URL", settings.MOBILITY_SERVICE_URL),
        ("AIR_QUALITY_WSDL_URL", settings.AIR_QUALITY_WSDL_URL),
        ("EMERGENCY_GRPC_HOST", settings.EMERGENCY_GRPC_HOST),
        ("URBAN_EVENTS_GRAPHQL_URL", settings.URBAN_EVENTS_GRAPHQL_URL),
    ]
    
    for field_name, field_value in required_fields:
        if not field_value:
            raise ValueError(f"Configuration manquante: {field_name}")
    
    return True