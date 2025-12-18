"""
Client SOAP pour le service Air Quality
Gère les appels SOAP et la conversion XML → Python
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from xml.etree import ElementTree as ET
import logging

logger = logging.getLogger(__name__)


class SOAPClient:
    """Client pour appeler le service SOAP Air Quality"""
    
    def __init__(self, soap_url: str = "http://localhost:8001"):
        """
        Initialiser le client SOAP
        
        Args:
            soap_url: URL du service SOAP (sans /?wsdl)
        """
        self.soap_url = soap_url
        self.wsdl_url = f"{soap_url}/?wsdl"
        self.namespace = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'tns': 'http://smartcity.air-quality.soap',
            's0': 'http://smartcity.air-quality.soap/models'
        }
    
    def _make_soap_request(self, action: str, body: str) -> str:
        """
        Effectuer une requête SOAP
        
        Args:
            action: Nom de l'action SOAP
            body: Corps de la requête SOAP (sans envelope)
            
        Returns:
            Réponse XML brute
        """
        envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:smar="http://smartcity.air-quality.soap">
    <soap:Header/>
    <soap:Body>
        {body}
    </soap:Body>
</soap:Envelope>"""
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': action
        }
        
        try:
            response = requests.post(
                self.soap_url,
                data=envelope,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur requête SOAP {action}: {e}")
            raise
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[str]:
        """Parser un timestamp ISO et le retourner en format ISO string"""
        try:
            if timestamp_str:
                return timestamp_str
            return None
        except Exception:
            return None
    
    def get_aqi(self, zone: str) -> Dict[str, Any]:
        """
        Récupérer l'AQI pour une zone
        
        Args:
            zone: Identifiant de la zone (ex: 'CENTRE', 'NORD')
            
        Returns:
            Dict avec zone, aqi, category, timestamp, description
        """
        body = f"""
        <smar:GetAQI>
            <smar:zone>{zone}</smar:zone>
        </smar:GetAQI>
        """
        
        response_xml = self._make_soap_request('GetAQI', body)
        root = ET.fromstring(response_xml)
        
        result = root.find('.//tns:GetAQIResult', self.namespace)
        
        return {
            'zone': result.find('s0:zone', self.namespace).text,
            'aqi': int(result.find('s0:aqi', self.namespace).text),
            'category': result.find('s0:category', self.namespace).text,
            'timestamp': self._parse_timestamp(result.find('s0:timestamp', self.namespace).text),
            'description': result.find('s0:description', self.namespace).text
        }
    
    def get_pollutants(self, zone: str) -> Dict[str, Any]:
        """
        Récupérer tous les polluants pour une zone
        
        Args:
            zone: Identifiant de la zone
            
        Returns:
            Dict avec zone, pollutants (liste), timestamp
        """
        body = f"""
        <smar:GetPollutants>
            <smar:zone>{zone}</smar:zone>
        </smar:GetPollutants>
        """
        
        response_xml = self._make_soap_request('GetPollutants', body)
        root = ET.fromstring(response_xml)
        
        result = root.find('.//tns:GetPollutantsResult', self.namespace)
        
        pollutants = []
        for pollutant in result.findall('.//s0:Pollutant', self.namespace):
            pollutants.append({
                'name': pollutant.find('s0:name', self.namespace).text,
                'value': float(pollutant.find('s0:value', self.namespace).text),
                'unit': pollutant.find('s0:unit', self.namespace).text,
                'timestamp': self._parse_timestamp(pollutant.find('s0:timestamp', self.namespace).text),
                'status': pollutant.find('s0:status', self.namespace).text
            })
        
        return {
            'zone': result.find('s0:zone', self.namespace).text,
            'pollutants': pollutants,
            'timestamp': self._parse_timestamp(result.find('s0:timestamp', self.namespace).text)
        }
    
    def compare_zones(self, zone_a: str, zone_b: str) -> Dict[str, Any]:
        """
        Comparer deux zones
        
        Args:
            zone_a: Première zone
            zone_b: Deuxième zone
            
        Returns:
            Dict avec comparaison des deux zones
        """
        body = f"""
        <smar:CompareZones>
            <smar:zoneA>{zone_a}</smar:zoneA>
            <smar:zoneB>{zone_b}</smar:zoneB>
        </smar:CompareZones>
        """
        
        response_xml = self._make_soap_request('CompareZones', body)
        root = ET.fromstring(response_xml)
        
        result = root.find('.//tns:CompareZonesResult', self.namespace)
        
        return {
            'zoneA': result.find('s0:zoneA', self.namespace).text,
            'zoneB': result.find('s0:zoneB', self.namespace).text,
            'aqiA': int(result.find('s0:aqiA', self.namespace).text),
            'aqiB': int(result.find('s0:aqiB', self.namespace).text),
            'cleanest_zone': result.find('s0:cleanest_zone', self.namespace).text,
            'difference': int(result.find('s0:difference', self.namespace).text),
            'recommendations': result.find('s0:recommendations', self.namespace).text,
            'timestamp': self._parse_timestamp(result.find('s0:timestamp', self.namespace).text)
        }
    
    def get_history(
        self, 
        zone: str, 
        start_date: str, 
        end_date: str, 
        granularity: str = 'daily'
    ) -> Dict[str, Any]:
        """
        Récupérer l'historique des mesures
        
        Args:
            zone: Identifiant de la zone
            start_date: Date de début (ISO format)
            end_date: Date de fin (ISO format)
            granularity: 'hourly' ou 'daily'
            
        Returns:
            Dict avec zone, start_date, end_date, granularity, data_points
        """
        body = f"""
        <smar:GetHistory>
            <smar:zone>{zone}</smar:zone>
            <smar:startDate>{start_date}</smar:startDate>
            <smar:endDate>{end_date}</smar:endDate>
            <smar:granularity>{granularity}</smar:granularity>
        </smar:GetHistory>
        """
        
        response_xml = self._make_soap_request('GetHistory', body)
        root = ET.fromstring(response_xml)
        
        result = root.find('.//tns:GetHistoryResult', self.namespace)
        
        data_points = []
        for point in result.findall('.//s0:DataPoint', self.namespace):
            data_point = {
                'timestamp': self._parse_timestamp(point.find('s0:timestamp', self.namespace).text),
                'aqi': int(point.find('s0:aqi', self.namespace).text)
            }
            
            # Ajouter les polluants optionnels
            for pollutant in ['pm25', 'pm10', 'no2', 'co2', 'o3', 'so2']:
                elem = point.find(f's0:{pollutant}', self.namespace)
                if elem is not None and elem.text:
                    data_point[pollutant] = float(elem.text)
            
            data_points.append(data_point)
        
        return {
            'zone': result.find('s0:zone', self.namespace).text,
            'start_date': self._parse_timestamp(result.find('s0:start_date', self.namespace).text),
            'end_date': self._parse_timestamp(result.find('s0:end_date', self.namespace).text),
            'granularity': result.find('s0:granularity', self.namespace).text,
            'data_points': data_points
        }
    
    def filter_pollutants(self, zone: str, threshold: float) -> Dict[str, Any]:
        """
        Filtrer les polluants au-dessus d'un seuil
        
        Args:
            zone: Identifiant de la zone
            threshold: Seuil de filtrage
            
        Returns:
            Dict avec zone, pollutants filtrés, timestamp
        """
        body = f"""
        <smar:FilterPollutants>
            <smar:zone>{zone}</smar:zone>
            <smar:threshold>{threshold}</smar:threshold>
        </smar:FilterPollutants>
        """
        
        response_xml = self._make_soap_request('FilterPollutants', body)
        root = ET.fromstring(response_xml)
        
        result = root.find('.//tns:FilterPollutantsResult', self.namespace)
        
        pollutants = []
        for pollutant in result.findall('.//s0:Pollutant', self.namespace):
            pollutants.append({
                'name': pollutant.find('s0:name', self.namespace).text,
                'value': float(pollutant.find('s0:value', self.namespace).text),
                'unit': pollutant.find('s0:unit', self.namespace).text,
                'timestamp': self._parse_timestamp(pollutant.find('s0:timestamp', self.namespace).text),
                'status': pollutant.find('s0:status', self.namespace).text
            })
        
        return {
            'zone': result.find('s0:zone', self.namespace).text,
            'pollutants': pollutants,
            'threshold': threshold,
            'timestamp': self._parse_timestamp(result.find('s0:timestamp', self.namespace).text)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifier l'état du service SOAP
        
        Returns:
            Dict avec status, version, uptime, database_status, last_check
        """
        body = "<smar:HealthCheck/>"
        
        response_xml = self._make_soap_request('HealthCheck', body)
        root = ET.fromstring(response_xml)
        
        result = root.find('.//tns:HealthCheckResult', self.namespace)
        
        return {
            'status': result.find('s0:status', self.namespace).text,
            'version': result.find('s0:version', self.namespace).text,
            'uptime_seconds': int(result.find('s0:uptime_seconds', self.namespace).text),
            'database_status': result.find('s0:database_status', self.namespace).text,
            'last_check': self._parse_timestamp(result.find('s0:last_check', self.namespace).text)
        }