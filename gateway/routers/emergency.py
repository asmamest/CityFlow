"""Router FastAPI pour le service Urgences (gRPC)"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from  clients import EmergencyGrpcClient
from  models.emergency import (
    CreateAlertRequest, AlertResponse,
    GetActiveAlertsRequest, UpdateAlertStatusRequest,
    AlertHistoryRequest, AlertHistoryResponse
)
from  utils import logger

router = APIRouter(prefix="/emergency", tags=["Urgences"])

# Dependency pour le client gRPC
async def get_emergency_client():
    client = EmergencyGrpcClient()
    try:
        yield client
    finally:
        await client.close()

@router.get("/", summary="Page d'accueil du service Urgences")
async def emergency_home():
    """Informations sur le service Urgences"""
    return {
        "service": "Urgences",
        "version": "1.0.0",
        "protocol": "gRPC",
        "description": "Service de gestion des alertes d'urgence",
        "endpoints": [
            "/emergency/alerts",
            "/emergency/alerts/active/{zone}",
            "/emergency/alerts/{alert_id}/status",
            "/emergency/alerts/history"
        ],
        "alert_types": [
            "ACCIDENT", "FIRE", "AMBULANCE_REQUEST",
            "MEDICAL_EMERGENCY", "NATURAL_DISASTER",
            "SECURITY_THREAT", "PUBLIC_HEALTH"
        ],
        "priorities": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        "statuses": ["PENDING", "IN_PROGRESS", "RESOLVED", "CANCELLED"]
    }

@router.post(
    "/alerts",
    response_model=dict,
    status_code=201,
    summary="Créer une nouvelle alerte"
)
async def create_alert(
    request: CreateAlertRequest,
    client: EmergencyGrpcClient = Depends(get_emergency_client)
):
    """
    Crée une nouvelle alerte d'urgence.
    
    Types d'alertes:
    - ACCIDENT: Accident de la route ou industriel
    - FIRE: Incendie
    - AMBULANCE_REQUEST: Demande d'ambulance
    - MEDICAL_EMERGENCY: Urgence médicale critique
    - NATURAL_DISASTER: Catastrophe naturelle
    - SECURITY_THREAT: Menace sécuritaire
    - PUBLIC_HEALTH: Crise de santé publique
    
    Priorités (temps de réponse):
    - LOW: < 30 minutes
    - MEDIUM: < 15 minutes
    - HIGH: < 8 minutes
    - CRITICAL: < 5 minutes
    """
    logger.info(f"Gateway: Creating alert of type {request.type}")
    result = await client.create_alert(
        alert_type=request.type.value,
        description=request.description,
        location=request.location.model_dump(),
        priority=request.priority.value,
        reporter_name=request.reporter_name,
        reporter_phone=request.reporter_phone,
        affected_people=request.affected_people
    )
    return result

@router.get(
    "/alerts/active/{zone}",
    response_model=List[dict],
    summary="Alertes actives d'une zone"
)
async def get_active_alerts(
    zone: str,
    alert_type: Optional[str] = Query(None, description="Type d'alerte à filtrer"),
    min_priority: Optional[str] = Query(None, description="Priorité minimale"),
    client: EmergencyGrpcClient = Depends(get_emergency_client)
):
    """
    Récupère toutes les alertes actives pour une zone donnée.
    
    - **zone**: Nom de la zone
    - **alert_type** (optionnel): Filtrer par type d'alerte
    - **min_priority** (optionnel): Priorité minimale (LOW, MEDIUM, HIGH, CRITICAL)
    """
    logger.info(f"Gateway: Getting active alerts for zone {zone}")
    result = await client.get_active_alerts(
        zone=zone,
        alert_type=alert_type,
        min_priority=min_priority
    )
    return result

@router.put(
    "/alerts/{alert_id}/status",
    response_model=dict,
    summary="Mettre à jour le statut d'une alerte"
)
async def update_alert_status(
    alert_id: str,
    request: UpdateAlertStatusRequest,
    client: EmergencyGrpcClient = Depends(get_emergency_client)
):
    """
    Met à jour le statut d'une alerte existante.
    
    Statuts possibles:
    - PENDING: En attente d'assignation
    - IN_PROGRESS: Intervention en cours
    - RESOLVED: Résolue
    - CANCELLED: Annulée
    """
    logger.info(f"Gateway: Updating alert {alert_id} status to {request.new_status}")
    result = await client.update_alert_status(
        alert_id=alert_id,
        new_status=request.new_status.value,
        assigned_team=request.assigned_team or "",
        notes=request.notes or ""
    )
    return result

@router.post(
    "/alerts/history",
    response_model=dict,
    summary="Historique des alertes"
)
async def get_alert_history(
    request: AlertHistoryRequest,
    client: EmergencyGrpcClient = Depends(get_emergency_client)
):
    """
    Récupère l'historique des alertes avec statistiques.
    
    - **zone** (optionnel): Filtrer par zone
    - **alert_type** (optionnel): Filtrer par type
    - **start_date** (optionnel): Date de début (timestamp Unix)
    - **end_date** (optionnel): Date de fin (timestamp Unix)
    - **limit**: Nombre maximum de résultats (défaut: 100)
    """
    logger.info("Gateway: Getting alert history")
    result = await client.get_alert_history(
        zone=request.zone,
        alert_type=request.alert_type.value if request.alert_type else None,
        start_date=request.start_date,
        end_date=request.end_date,
        limit=request.limit
    )
    return result

@router.get(
    "/stats/{zone}",
    summary="Statistiques des alertes par zone"
)
async def get_zone_stats(
    zone: str,
    client: EmergencyGrpcClient = Depends(get_emergency_client)
):
    """
    Récupère des statistiques globales pour une zone.
    
    Retourne le nombre d'alertes actives par type et priorité.
    """
    logger.info(f"Gateway: Getting stats for zone {zone}")
    
    # Récupérer toutes les alertes actives
    alerts = await client.get_active_alerts(zone=zone)
    
    # Calculer les statistiques
    stats = {
        "zone": zone,
        "total_active_alerts": len(alerts),
        "by_type": {},
        "by_priority": {},
        "by_status": {}
    }
    
    for alert in alerts:
        # Par type
        alert_type = alert["type"]
        stats["by_type"][alert_type] = stats["by_type"].get(alert_type, 0) + 1
        
        # Par priorité
        priority = alert["priority"]
        stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
        
        # Par statut
        status = alert["status"]
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
    
    return stats