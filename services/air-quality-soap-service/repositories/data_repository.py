"""
Repository pour accès aux données PostgreSQL
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func

from database.connection import SessionLocal
from database.models import ZoneModel, AirQualityMeasurementModel, PollutantModel
from utils.logger import setup_logger

logger = setup_logger('repository', 'logs/service.log')


class DataRepository:
    """Repository pour gérer l'accès aux données de qualité de l'air depuis PostgreSQL"""
    
    def __init__(self):
        """Initialisation du repository"""
        logger.info("📦 Initialisation DataRepository (PostgreSQL)")
    
    def _get_db_session(self) -> Session:
        """Créer une nouvelle session de base de données"""
        return SessionLocal()
    
    def get_current_data(self, zone: str) -> Optional[Dict]:
        """
        Obtenir les données actuelles pour une zone donnée
        
        Args:
            zone: Identifiant de la zone (ex: 'CENTRE', 'NORD', etc.)
            
        Returns:
            Dict contenant aqi, status, timestamp et tous les polluants formatés
            Format attendu par le service:
            {
                'aqi': 75,
                'status': 'MODERATE',
                'timestamp': datetime,
                'pm25': 35.5,
                'pm10': 55.2,
                'no2': 42.1,
                'co2': 420.0,
                'o3': 68.3,
                'so2': 12.5
            }
        """
        db = self._get_db_session()
        try:
            # Vérifier si la zone existe
            zone_obj = db.query(ZoneModel).filter(ZoneModel.id == zone).first()
            if not zone_obj:
                logger.warning(f"⚠️ Zone '{zone}' introuvable dans la base")
                return None
            
            # Récupérer la mesure la plus récente pour cette zone avec ses polluants
            measurement = (
                db.query(AirQualityMeasurementModel)
                .options(joinedload(AirQualityMeasurementModel.pollutants))
                .filter(AirQualityMeasurementModel.zone_id == zone)
                .order_by(desc(AirQualityMeasurementModel.timestamp))
                .first()
            )
            
            if not measurement:
                logger.warning(f"⚠️ Aucune mesure trouvée pour zone '{zone}'")
                return None
            
            # Construire le dictionnaire de données
            data = {
                'aqi': measurement.aqi,
                'status': measurement.status,
                'timestamp': measurement.timestamp,
                'zone_name': zone_obj.name,
                'zone_description': zone_obj.description
            }
            
            # Ajouter chaque polluant au dictionnaire
            # Le service s'attend à des clés comme 'pm25', 'pm10', 'no2', etc.
            for pollutant in measurement.pollutants:
                # Normaliser le nom du polluant (PM2.5 -> pm25, NO2 -> no2)
                pollutant_key = pollutant.nom.lower().replace('.', '').replace(' ', '')
                data[pollutant_key] = pollutant.valeur
                
                # Stocker également l'unité et le status si besoin
                data[f'{pollutant_key}_unit'] = pollutant.unite
                data[f'{pollutant_key}_status'] = pollutant.status
            
            logger.info(f"✅ Données récupérées pour zone '{zone}' (AQI: {measurement.aqi}, {len(measurement.pollutants)} polluants)")
            return data
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération données zone '{zone}': {e}")
            return None
        finally:
            db.close()
    
    def get_all_pollutants(self, zone: str) -> Optional[List[Dict]]:
        """
        Récupérer tous les polluants pour une zone donnée (format liste)
        Utilisé par get_pollutants() dans le service
        
        Args:
            zone: Identifiant de la zone
            
        Returns:
            Liste de dictionnaires avec name, value, unit, status, timestamp
        """
        db = self._get_db_session()
        try:
            # Récupérer la mesure la plus récente avec ses polluants
            measurement = (
                db.query(AirQualityMeasurementModel)
                .options(joinedload(AirQualityMeasurementModel.pollutants))
                .filter(AirQualityMeasurementModel.zone_id == zone)
                .order_by(desc(AirQualityMeasurementModel.timestamp))
                .first()
            )
            
            if not measurement:
                logger.warning(f"⚠️ Aucune mesure pour zone '{zone}'")
                return None
            
            # Construire la liste des polluants
            result = []
            for p in measurement.pollutants:
                result.append({
                    'name': p.nom,
                    'value': p.valeur,
                    'unit': p.unite,
                    'status': p.status,
                    'timestamp': measurement.timestamp
                })
            
            logger.info(f"✅ {len(result)} polluants récupérés pour zone '{zone}'")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération polluants zone '{zone}': {e}")
            return None
        finally:
            db.close()
    
    def get_historical_data(
        self, 
        zone: str, 
        start_date: datetime, 
        end_date: datetime, 
        granularity: str = 'daily'
    ) -> List[Dict]:
        """
        Récupérer les données historiques pour une zone
        
        Args:
            zone: Identifiant de la zone
            start_date: Date de début
            end_date: Date de fin
            granularity: Granularité ('hourly' ou 'daily')
            
        Returns:
            Liste de dictionnaires avec timestamp, aqi et tous les polluants
            Format: [
                {
                    'timestamp': datetime,
                    'aqi': 75,
                    'status': 'MODERATE',
                    'pm25': 35.5,
                    'pm10': 55.2,
                    ...
                }
            ]
        """
        db = self._get_db_session()
        try:
            # Récupérer toutes les mesures dans la période avec leurs polluants
            measurements = (
                db.query(AirQualityMeasurementModel)
                .options(joinedload(AirQualityMeasurementModel.pollutants))
                .filter(
                    and_(
                        AirQualityMeasurementModel.zone_id == zone,
                        AirQualityMeasurementModel.timestamp >= start_date,
                        AirQualityMeasurementModel.timestamp <= end_date
                    )
                )
                .order_by(AirQualityMeasurementModel.timestamp)
                .all()
            )
            
            if not measurements:
                logger.warning(f"⚠️ Aucune donnée historique pour zone '{zone}' entre {start_date} et {end_date}")
                return []
            
            history = []
            for measurement in measurements:
                # Construire l'entrée historique
                entry = {
                    'timestamp': measurement.timestamp,
                    'aqi': measurement.aqi,
                    'status': measurement.status
                }
                
                # Ajouter les polluants
                for p in measurement.pollutants:
                    pollutant_key = p.nom.lower().replace('.', '').replace(' ', '')
                    entry[pollutant_key] = p.valeur
                
                history.append(entry)
            
            logger.info(f"✅ {len(history)} points historiques récupérés pour zone '{zone}'")
            return history
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération historique zone '{zone}': {e}")
            return []
        finally:
            db.close()
    
    def get_all_zones(self) -> List[Dict]:
        """
        Récupérer toutes les zones disponibles
        
        Returns:
            Liste de dictionnaires avec id, name, description
        """
        db = self._get_db_session()
        try:
            zones = db.query(ZoneModel).all()
            
            result = []
            for zone in zones:
                result.append({
                    'id': zone.id,
                    'name': zone.name,
                    'description': zone.description
                })
            
            logger.info(f"✅ {len(result)} zones disponibles")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération zones: {e}")
            return []
        finally:
            db.close()
    
    def check_health(self) -> bool:
        """
        Vérifier l'état de la connexion à la base de données
        
        Returns:
            True si la connexion fonctionne, False sinon
        """
        db = self._get_db_session()
        try:
            # Tenter une requête simple
            count = db.query(ZoneModel).count()
            logger.info(f"✅ Health check OK: {count} zones dans la base")
            return count > 0
        except Exception as e:
            logger.error(f"❌ Health check FAILED: {e}")
            return False
        finally:
            db.close()
    
    def get_zone_statistics(self, zone: str, days: int = 7) -> Optional[Dict]:
        """
        Obtenir des statistiques pour une zone sur les N derniers jours
        
        Args:
            zone: Identifiant de la zone
            days: Nombre de jours pour le calcul (défaut: 7)
            
        Returns:
            Dict avec statistiques (moyenne, min, max AQI)
        """
        db = self._get_db_session()
        try:
            # Calculer statistiques sur les N derniers jours
            days_ago = datetime.now() - timedelta(days=days)
            
            stats = (
                db.query(
                    func.avg(AirQualityMeasurementModel.aqi).label('avg_aqi'),
                    func.min(AirQualityMeasurementModel.aqi).label('min_aqi'),
                    func.max(AirQualityMeasurementModel.aqi).label('max_aqi'),
                    func.count(AirQualityMeasurementModel.id).label('count')
                )
                .filter(
                    and_(
                        AirQualityMeasurementModel.zone_id == zone,
                        AirQualityMeasurementModel.timestamp >= days_ago
                    )
                )
                .first()
            )
            
            if not stats or stats.count == 0:
                logger.warning(f"⚠️ Aucune statistique disponible pour zone '{zone}'")
                return None
            
            result = {
                'zone': zone,
                'avg_aqi': round(float(stats.avg_aqi), 2) if stats.avg_aqi else 0,
                'min_aqi': stats.min_aqi if stats.min_aqi else 0,
                'max_aqi': stats.max_aqi if stats.max_aqi else 0,
                'measurement_count': stats.count,
                'period_days': days
            }
            
            logger.info(f"✅ Statistiques calculées pour zone '{zone}' sur {days} jours")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul statistiques zone '{zone}': {e}")
            return None
        finally:
            db.close()
    
    def get_latest_measurement_time(self, zone: str) -> Optional[datetime]:
        """
        Récupérer l'horodatage de la dernière mesure pour une zone
        
        Args:
            zone: Identifiant de la zone
            
        Returns:
            datetime de la dernière mesure ou None
        """
        db = self._get_db_session()
        try:
            measurement = (
                db.query(AirQualityMeasurementModel.timestamp)
                .filter(AirQualityMeasurementModel.zone_id == zone)
                .order_by(desc(AirQualityMeasurementModel.timestamp))
                .first()
            )
            
            if measurement:
                return measurement[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération timestamp zone '{zone}': {e}")
            return None
        finally:
            db.close()