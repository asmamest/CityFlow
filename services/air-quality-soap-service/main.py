""" 
Air Quality SOAP Service - Main Entry Point
Serveur SOAP pour la qualité de l'air urbain (PostgreSQL)
"""
import os
import logging
from wsgiref.simple_server import make_server
from spyne import Application, rpc, ServiceBase
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from models.air_quality_models import (
    AirQualityResult, PollutantList, ZoneComparison,
    HistoricalSeries, HealthStatus
)
from services.air_quality_service import AirQualityServiceImpl
from utils.logger import setup_logger, get_request_logger
from spyne.model.primitive import Unicode, DateTime, Float

# Import des fonctions d'initialisation de la base de données
from database.connection import init_db, seed_data, engine

logger = setup_logger('main', 'logs/service.log')


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


def create_app():
    """Créer l'application WSGI SOAP"""
    application = Application(
        [AirQualitySOAPService],
        tns='http://smartcity.air-quality.soap',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )
    return WsgiApplication(application)


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
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ ERREUR lors de l'initialisation de la base de données")
        logger.error(f"❌ {str(e)}")
        logger.error("=" * 60)
        logger.error("⚠️  Vérifiez que PostgreSQL est démarré et accessible")
        logger.error("⚠️  Vérifiez DATABASE_URL dans les variables d'environnement")
        raise


if __name__ == '__main__':
    # Configuration du serveur
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    
    try:
        logger.info("")
        logger.info("=" * 60)
        logger.info("🚀 DÉMARRAGE DU SERVICE SOAP AIR QUALITY")
        logger.info("=" * 60)
        logger.info(f"📍 Host: {host}")
        logger.info(f"📍 Port: {port}")
        logger.info(f"📍 WSDL: http://{host}:{port}/?wsdl")
        logger.info("=" * 60)
        
        # Initialiser la base de données AVANT de démarrer le service
        initialize_database()
        
        # Créer l'instance du service (maintenant que la DB est prête)
        logger.info("🔧 Initialisation du service métier...")
        global service_impl
        service_impl = AirQualityServiceImpl()
        logger.info("✅ Service métier initialisé")
        
        # Créer l'application WSGI
        logger.info("🔧 Création de l'application WSGI...")
        wsgi_app = create_app()
        logger.info("✅ Application WSGI créée")
        
        # Créer le serveur
        logger.info("🔧 Création du serveur SOAP...")
        server = make_server(host, port, wsgi_app)
        logger.info("✅ Serveur SOAP créé")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ SERVEUR SOAP PRÊT ET EN ÉCOUTE")
        logger.info("=" * 60)
        logger.info(f"🌐 Le service est accessible sur http://{host}:{port}")
        logger.info(f"📄 Documentation WSDL: http://{host}:{port}/?wsdl")
        logger.info("=" * 60)
        logger.info("💡 Appuyez sur Ctrl+C pour arrêter le serveur")
        logger.info("")
        
        # Démarrer le serveur
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 60)
        logger.info("⏸️  Arrêt du serveur demandé (Ctrl+C)")
        logger.info("=" * 60)
        logger.info("👋 Au revoir!")
        
    except Exception as e:
        logger.error("")
        logger.error("=" * 60)
        logger.error("❌ ERREUR FATALE")
        logger.error("=" * 60)
        logger.error(f"Message: {str(e)}")
        logger.error("=" * 60)
        logger.error("", exc_info=True)
        raise