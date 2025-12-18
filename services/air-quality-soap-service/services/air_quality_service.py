"""
Service métier Air Quality (version PostgreSQL)
"""
import time
from datetime import datetime, timedelta
from spyne import Fault

from models.air_quality_models import (
    AirQualityResult, PollutantList, ZoneComparison,
    HistoricalSeries, HealthStatus, Pollutant, DataPoint
)
from repositories.data_repository import DataRepository
from utils.logger import setup_logger

logger = setup_logger('service', 'logs/service.log')

START_TIME = time.time()
SERVICE_VERSION = "1.0.0"


class AirQualityServiceImpl:
    
    def __init__(self):
        self.repository = DataRepository()
        logger.info("🚀 Service Air Quality initialisé (PostgreSQL)")
    
    def get_aqi(self, zone: str) -> AirQualityResult:
        """
        Récupérer l'AQI (Air Quality Index) pour une zone
        
        Args:
            zone: Identifiant de la zone (ex: 'CENTRE', 'NORD')
            
        Returns:
            AirQualityResult avec zone, aqi, category, timestamp, description
        """
        if not zone or zone.strip() == "":
            raise Fault(faultcode="Client", faultstring="Zone vide ou invalide")
        
        try:
            data = self.repository.get_current_data(zone)
            if not data:
                raise Fault(faultcode="Server", faultstring=f"Zone '{zone}' introuvable")
            
            aqi = data.get('aqi', 0)
            category = self._get_aqi_category(aqi)
            
            result = AirQualityResult()
            result.zone = zone
            result.aqi = aqi
            result.category = category
            result.timestamp = data.get('timestamp', datetime.now())
            result.description = self._get_aqi_description(category)
            
            logger.info(f"✅ get_aqi({zone}): AQI={aqi}, category={category}")
            return result
        except Fault:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur get_aqi({zone}): {str(e)}")
            raise Fault(faultcode="Server", faultstring=str(e))
    
    def get_pollutants(self, zone: str) -> PollutantList:
        """
        Récupérer la liste de tous les polluants pour une zone
        
        Args:
            zone: Identifiant de la zone
            
        Returns:
            PollutantList avec zone, pollutants[], timestamp
        """
        if not zone or zone.strip() == "":
            raise Fault(faultcode="Client", faultstring="Zone vide ou invalide")
        
        try:
            data = self.repository.get_current_data(zone)
            if not data:
                raise Fault(faultcode="Server", faultstring=f"Zone '{zone}' introuvable")
            
            timestamp = data.get('timestamp', datetime.now())
            pollutants = []
            
            # Mapping des noms de polluants depuis la base vers les noms d'affichage
            pollutant_mapping = [
                ('PM2.5', 'pm25'),
                ('PM10', 'pm10'),
                ('NO2', 'no2'),
                ('CO2', 'co2'),
                ('O3', 'o3'),
                ('SO2', 'so2')
            ]
            
            for display_name, key in pollutant_mapping:
                if key in data:
                    p = Pollutant()
                    p.name = display_name
                    p.value = float(data[key])
                    
                    # Utiliser l'unité depuis la base si disponible, sinon valeur par défaut
                    p.unit = data.get(f'{key}_unit', self._get_default_unit(key))
                    p.timestamp = timestamp
                    
                    # Utiliser le status depuis la base si disponible, sinon calculer
                    p.status = data.get(f'{key}_status', self._get_pollutant_status(data[key], key))
                    
                    pollutants.append(p)
            
            result = PollutantList()
            result.zone = zone
            result.pollutants = pollutants
            result.timestamp = timestamp
            
            logger.info(f"✅ get_pollutants({zone}): {len(pollutants)} polluants")
            return result
        except Fault:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur get_pollutants({zone}): {str(e)}")
            raise Fault(faultcode="Server", faultstring=str(e))
    
    def compare_zones(self, zoneA: str, zoneB: str) -> ZoneComparison:
        """
        Comparer la qualité de l'air entre deux zones
        
        Args:
            zoneA: Première zone
            zoneB: Deuxième zone
            
        Returns:
            ZoneComparison avec les AQI des deux zones et recommandations
        """
        if not zoneA or not zoneB:
            raise Fault(faultcode="Client", faultstring="Zones vides ou invalides")
        
        if zoneA.strip() == "" or zoneB.strip() == "":
            raise Fault(faultcode="Client", faultstring="Zones vides ou invalides")
        
        try:
            dataA = self.repository.get_current_data(zoneA)
            dataB = self.repository.get_current_data(zoneB)
            
            if not dataA:
                raise Fault(faultcode="Server", faultstring=f"Zone '{zoneA}' introuvable")
            if not dataB:
                raise Fault(faultcode="Server", faultstring=f"Zone '{zoneB}' introuvable")
            
            aqiA = dataA.get('aqi', 0)
            aqiB = dataB.get('aqi', 0)
            
            result = ZoneComparison()
            result.zoneA = zoneA
            result.zoneB = zoneB
            result.aqiA = aqiA
            result.aqiB = aqiB
            result.cleanest_zone = zoneA if aqiA < aqiB else zoneB
            result.difference = abs(aqiA - aqiB)
            result.recommendations = self._get_recommendations(aqiA, aqiB, zoneA, zoneB)
            result.timestamp = datetime.now()
            
            logger.info(f"✅ compare_zones({zoneA}, {zoneB}): diff={result.difference}, best={result.cleanest_zone}")
            return result
        except Fault:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur compare_zones({zoneA}, {zoneB}): {str(e)}")
            raise Fault(faultcode="Server", faultstring=str(e))
    
    def get_history(self, zone: str, start_date, end_date, granularity: str) -> HistoricalSeries:
        """
        Récupérer l'historique des mesures pour une zone
        
        Args:
            zone: Identifiant de la zone
            start_date: Date de début
            end_date: Date de fin
            granularity: 'hourly' ou 'daily'
            
        Returns:
            HistoricalSeries avec la liste des DataPoint
        """
        if not zone or zone.strip() == "":
            raise Fault(faultcode="Client", faultstring="Zone vide ou invalide")
        
        if granularity not in ['hourly', 'daily']:
            raise Fault(faultcode="Client", faultstring="Granularité invalide (hourly/daily uniquement)")
        
        if start_date >= end_date:
            raise Fault(faultcode="Client", faultstring="Date de début doit être < date de fin")
        
        try:
            history = self.repository.get_historical_data(zone, start_date, end_date, granularity)
            
            if not history:
                logger.warning(f"⚠️ Aucune donnée historique pour zone '{zone}'")
            
            data_points = []
            for entry in history:
                dp = DataPoint()
                dp.timestamp = entry.get('timestamp', datetime.now())
                dp.aqi = entry.get('aqi', 0)
                dp.pm25 = entry.get('pm25')
                dp.pm10 = entry.get('pm10')
                dp.no2 = entry.get('no2')
                dp.co2 = entry.get('co2')
                dp.o3 = entry.get('o3')
                dp.so2 = entry.get('so2')
                data_points.append(dp)
            
            result = HistoricalSeries()
            result.zone = zone
            result.start_date = start_date
            result.end_date = end_date
            result.granularity = granularity
            result.data_points = data_points
            
            logger.info(f"✅ get_history({zone}): {len(data_points)} points de {start_date} à {end_date}")
            return result
        except Fault:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur get_history({zone}): {str(e)}")
            raise Fault(faultcode="Server", faultstring=str(e))
    
    def filter_pollutants(self, zone: str, threshold: float) -> PollutantList:
        """
        Filtrer les polluants supérieurs à un seuil
        
        Args:
            zone: Identifiant de la zone
            threshold: Seuil de filtrage
            
        Returns:
            PollutantList avec seulement les polluants > threshold
        """
        if not zone or zone.strip() == "":
            raise Fault(faultcode="Client", faultstring="Zone vide ou invalide")
        
        if threshold < 0:
            raise Fault(faultcode="Client", faultstring="Seuil négatif invalide")
        
        try:
            all_pollutants = self.get_pollutants(zone)
            filtered = [p for p in all_pollutants.pollutants if p.value > threshold]
            
            result = PollutantList()
            result.zone = zone
            result.pollutants = filtered
            result.timestamp = datetime.now()
            
            logger.info(f"✅ filter_pollutants({zone}, threshold={threshold}): {len(filtered)}/{len(all_pollutants.pollutants)} polluants")
            return result
        except Fault:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur filter_pollutants({zone}): {str(e)}")
            raise Fault(faultcode="Server", faultstring=str(e))
    
    def health_check(self) -> HealthStatus:
        """
        Vérifier l'état de santé du service et de la base de données
        
        Returns:
            HealthStatus avec status, version, uptime, database_status
        """
        try:
            db_status = "UP" if self.repository.check_health() else "DOWN"
            
            result = HealthStatus()
            result.status = "UP" if db_status == "UP" else "DEGRADED"
            result.version = SERVICE_VERSION
            result.uptime_seconds = int(time.time() - START_TIME)
            result.database_status = db_status
            result.last_check = datetime.now()
            
            logger.info(f"✅ health_check: status={result.status}, db={db_status}, uptime={result.uptime_seconds}s")
            return result
        except Exception as e:
            logger.error(f"❌ Erreur health_check: {str(e)}")
            raise Fault(faultcode="Server", faultstring=str(e))
    
    # ============ Méthodes utilitaires privées ============
    
    def _get_aqi_category(self, aqi: int) -> str:
        """Déterminer la catégorie AQI selon la valeur"""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def _get_aqi_description(self, category: str) -> str:
        """Obtenir une description textuelle de la catégorie AQI"""
        descriptions = {
            "Good": "La qualité de l'air est satisfaisante",
            "Moderate": "Qualité acceptable pour la plupart des personnes",
            "Unhealthy for Sensitive Groups": "Risque pour les personnes sensibles",
            "Unhealthy": "Risque pour toute la population",
            "Very Unhealthy": "Avertissement de santé",
            "Hazardous": "Alerte sanitaire"
        }
        return descriptions.get(category, "Inconnu")
    
    def _get_pollutant_status(self, value: float, pollutant_type: str) -> str:
        """
        Déterminer le status d'un polluant selon sa valeur
        (Utilisé comme fallback si le status n'est pas dans la base)
        """
        thresholds = {
            'pm25': 35.0,
            'pm10': 50.0,
            'no2': 100.0,
            'co2': 1000.0,
            'o3': 70.0,
            'so2': 75.0
        }
        threshold = thresholds.get(pollutant_type, 50.0)
        
        if value <= threshold:
            return "OK"
        elif value <= threshold * 1.5:
            return "ALERT"
        else:
            return "CRITICAL"
    
    def _get_default_unit(self, pollutant: str) -> str:
        """
        Obtenir l'unité par défaut d'un polluant
        (Utilisé comme fallback si l'unité n'est pas dans la base)
        """
        units = {
            'pm25': 'µg/m³',
            'pm10': 'µg/m³',
            'no2': 'µg/m³',
            'co2': 'ppm',
            'o3': 'µg/m³',
            'so2': 'µg/m³'
        }
        return units.get(pollutant, 'unit')
    
    def _get_recommendations(self, aqiA: int, aqiB: int, zoneA: str, zoneB: str) -> str:
        """Générer des recommandations basées sur la comparaison des AQI"""
        diff = abs(aqiA - aqiB)
        better = zoneA if aqiA < aqiB else zoneB
        
        if diff < 20:
            return f"Différence mineure. Les deux zones ont une qualité similaire."
        elif diff < 50:
            return f"Préférez {better} pour les activités extérieures."
        else:
            return f"Différence significative. Privilégiez fortement {better}."