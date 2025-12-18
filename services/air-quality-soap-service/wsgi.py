"""
WSGI Entry Point pour Gunicorn
"""
import os
import logging
from spyne import Application
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from models.air_quality_models import (
    AirQualityResult, PollutantList, ZoneComparison,
    HistoricalSeries, HealthStatus
)
from services.air_quality_service import AirQualityServiceImpl
from utils.logger import setup_logger, get_request_logger
from spyne.model.primitive import Unicode, DateTime, Float
from spyne import rpc, ServiceBase

# Import des fonctions d'initialisation de la base de données
from database.connection import init_db, seed_data, engine

logger = setup_logger('wsgi', 'logs/service.log')

# Initialiser la base de données au démarrage
def initialize_database():
    """Initialiser la base de données PostgreSQL"""
    try:
        logger.info("=" * 60)
        logger.info("🔧 Initialisation de la base de données PostgreSQL")
        logger.info("=" * 60)
        
        # Créer les tables si elles n'existent pas
        init_db()
        logger.info("✅ Tables PostgreSQL créées/vérifiées")
        
        # Insérer les données initiales si la base est vide
        seed_data()
        logger.info("✅ Données initiales vérifiées/insérées")
        
        # Vérifier la connexion
        with engine.connect() as conn:
            logger.info("✅ Connexion PostgreSQL établie avec succès")
        
        logger.info("=" * 60)
        logger.info("🎉 Base de données prête")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ ERREUR lors de l'initialisation de la base de données")
        logger.error(f"❌ {str(e)}")
        logger.error("=" * 60)
        logger.error("⚠️  Vérifiez que PostgreSQL est démarré et accessible")
        logger.error("⚠️  Vérifiez DATABASE_URL dans les variables d'environnement")
        return False

# Initialiser la base de données
logger.info("🚀 Démarrage de l'application WSGI")
if not initialize_database():
    logger.error("❌ Impossible de démarrer sans base de données")
    raise RuntimeError("Database initialization failed")

# Créer l'instance du service (GLOBAL pour être accessible dans la classe)
service_impl = AirQualityServiceImpl()
logger.info("✅ Service métier initialisé")


class AirQualitySOAPService(ServiceBase):
    """Service SOAP Qualité de l'Air"""
    
    @rpc(Unicode, _returns=AirQualityResult)
    def GetAQI(ctx, zone):
        req_logger = get_request_logger('GetAQI', {'zone': zone})
        req_logger.info(f"📥 Requête GetAQI pour zone: {zone}")
        try:
            result = service_impl.get_aqi(zone)
            req_logger.info(f"✅ Réponse GetAQI: AQI={result.aqi}, category={result.category}")
            return result
        except Exception as e:
            req_logger.error(f"❌ Erreur GetAQI: {str(e)}")
            raise
    
    @rpc(Unicode, _returns=PollutantList)
    def GetPollutants(ctx, zone):
        req_logger = get_request_logger('GetPollutants', {'zone': zone})
        req_logger.info(f"📥 Requête GetPollutants pour zone: {zone}")
        try:
            result = service_impl.get_pollutants(zone)
            req_logger.info(f"✅ Réponse GetPollutants: {len(result.pollutants)} polluants")
            return result
        except Exception as e:
            req_logger.error(f"❌ Erreur GetPollutants: {str(e)}")
            raise
    
    @rpc(Unicode, Unicode, _returns=ZoneComparison)
    def CompareZones(ctx, zoneA, zoneB):
        req_logger = get_request_logger('CompareZones', {'zoneA': zoneA, 'zoneB': zoneB})
        req_logger.info(f"📥 Requête CompareZones: {zoneA} vs {zoneB}")
        try:
            result = service_impl.compare_zones(zoneA, zoneB)
            req_logger.info(f"✅ Réponse CompareZones: zone la plus propre = {result.cleanest_zone}")
            return result
        except Exception as e:
            req_logger.error(f"❌ Erreur CompareZones: {str(e)}")
            raise
    
    @rpc(Unicode, DateTime, DateTime, Unicode, _returns=HistoricalSeries)
    def GetHistory(ctx, zone, startDate, endDate, granularity):
        req_logger = get_request_logger('GetHistory', {
            'zone': zone, 'startDate': str(startDate),
            'endDate': str(endDate), 'granularity': granularity
        })
        req_logger.info(f"📥 Requête GetHistory: zone={zone}, granularity={granularity}")
        try:
            result = service_impl.get_history(zone, startDate, endDate, granularity)
            req_logger.info(f"✅ Réponse GetHistory: {len(result.data_points)} points de données")
            return result
        except Exception as e:
            req_logger.error(f"❌ Erreur GetHistory: {str(e)}")
            raise
    
    @rpc(Unicode, Float, _returns=PollutantList)
    def FilterPollutants(ctx, zone, threshold):
        req_logger = get_request_logger('FilterPollutants', {'zone': zone, 'threshold': threshold})
        req_logger.info(f"📥 Requête FilterPollutants: zone={zone}, seuil={threshold}")
        try:
            result = service_impl.filter_pollutants(zone, threshold)
            req_logger.info(f"✅ Réponse FilterPollutants: {len(result.pollutants)} polluants au-dessus du seuil")
            return result
        except Exception as e:
            req_logger.error(f"❌ Erreur FilterPollutants: {str(e)}")
            raise
    
    @rpc(_returns=HealthStatus)
    def HealthCheck(ctx):
        req_logger = get_request_logger('HealthCheck', {})
        req_logger.info("📥 Requête HealthCheck")
        try:
            result = service_impl.health_check()
            req_logger.info(f"✅ Réponse HealthCheck: status={result.status}, db={result.database_status}")
            return result
        except Exception as e:
            req_logger.error(f"❌ Erreur HealthCheck: {str(e)}")
            raise


# Créer l'application WSGI (VARIABLE GLOBALE pour Gunicorn)
application = Application(
    [AirQualitySOAPService],
    tns='http://smartcity.air-quality.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

app = WsgiApplication(application)

logger.info("=" * 60)
logger.info("✅ Application WSGI prête pour Gunicorn")
logger.info("=" * 60)