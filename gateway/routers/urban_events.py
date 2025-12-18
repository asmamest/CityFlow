"""Router FastAPI pour le service Événements Urbains (GraphQL)"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from  clients import UrbanEventsGraphQLClient
from  models.urban_events import (
    Zone, EventType, Event,
    GetEventsRequest, CreateEventRequest,
    UpdateEventRequest, EventMutationResponse
)
from  utils import logger

router = APIRouter(prefix="/urban", tags=["Événements Urbains"])

# Dependency pour le client GraphQL
async def get_urban_client():
    client = UrbanEventsGraphQLClient()
    try:
        yield client
    finally:
        await client.close()

@router.get("/", summary="Page d'accueil du service Événements Urbains")
async def urban_events_home():
    """Informations sur le service Événements Urbains"""
    return {
        "service": "Événements Urbains",
        "version": "1.0.0",
        "protocol": "GraphQL",
        "description": "Service de gestion des événements urbains",
        "endpoints": [
            "/urban/zones",
            "/urban/event-types",
            "/urban/events",
            "/urban/events/{event_id}"
        ],
        "priorities": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        "statuses": ["PENDING", "IN_PROGRESS", "RESOLVED", "CANCELLED"]
    }

@router.get(
    "/zones",
    response_model=List[dict],
    summary="Liste des zones urbaines"
)
async def get_zones(
    client: UrbanEventsGraphQLClient = Depends(get_urban_client)
):
    """
    Liste toutes les zones urbaines disponibles.
    """
    logger.info("Gateway: Getting all zones")
    result = await client.get_zones()
    return result

@router.get(
    "/zones/{zone_id}",
    response_model=dict,
    summary="Détails d'une zone"
)
async def get_zone(
    zone_id: str,
    client: UrbanEventsGraphQLClient = Depends(get_urban_client)
):
    """
    Récupère les détails d'une zone spécifique.
    """
    logger.info(f"Gateway: Getting zone {zone_id}")
    result = await client.get_zone(zone_id)
    if not result:
        raise HTTPException(status_code=404, detail="Zone not found")
    return result

@router.get(
    "/event-types",
    response_model=List[dict],
    summary="Liste des types d'événements"
)
async def get_event_types(
    client: UrbanEventsGraphQLClient = Depends(get_urban_client)
):
    """
    Liste tous les types d'événements disponibles.
    """
    logger.info("Gateway: Getting all event types")
    result = await client.get_event_types()
    return result

@router.get(
    "/events",
    response_model=List[dict],
    summary="Liste des événements avec filtres"
)
async def get_events(
    event_type_id: Optional[str] = Query(None, description="Filtrer par type d'événement"),
    zone_id: Optional[str] = Query(None, description="Filtrer par zone"),
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    priority: Optional[str] = Query(None, description="Filtrer par priorité"),
    date_from: Optional[str] = Query(None, description="Date de début (ISO format)"),
    date_to: Optional[str] = Query(None, description="Date de fin (ISO format)"),
    client: UrbanEventsGraphQLClient = Depends(get_urban_client)
):
    """
    Liste les événements urbains avec filtres optionnels.
    
    Filtres disponibles:
    - **event_type_id**: ID du type d'événement
    - **zone_id**: ID de la zone
    - **status**: PENDING, IN_PROGRESS, RESOLVED, CANCELLED
    - **priority**: LOW, MEDIUM, HIGH, CRITICAL
    - **date_from**: Date de début (format ISO)
    - **date_to**: Date de fin (format ISO)
    """
    logger.info("Gateway: Getting events with filters")
    result = await client.get_events(
        event_type_id=event_type_id,
        zone_id=zone_id,
        status=status,
        priority=priority,
        date_from=date_from,
        date_to=date_to
    )
    return result

@router.get(
    "/events/{event_id}",
    response_model=dict,
    summary="Détails d'un événement"
)
async def get_event(
    event_id: str,
    client: UrbanEventsGraphQLClient = Depends(get_urban_client)
):
    """
    Récupère les détails complets d'un événement.
    """
    logger.info(f"Gateway: Getting event {event_id}")
    result = await client.get_event(event_id)
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return result

@router.post(
    "/events",
    response_model=dict,
    status_code=201,
    summary="Créer un nouvel événement"
)
async def create_event(
    request: CreateEventRequest,
    client: UrbanEventsGraphQLClient = Depends(get_urban_client)
):
    """
    Crée un nouvel événement urbain.
    
    - **name**: Nom de l'événement
    - **description**: Description détaillée
    - **event_type_id**: ID du type d'événement
    - **zone_id**: ID de la zone
    - **date**: Date de l'événement (ISO format)
    - **priority**: LOW, MEDIUM, HIGH, CRITICAL
    - **status**: PENDING (défaut), IN_PROGRESS, RESOLVED, CANCELLED
    """
    logger.info(f"Gateway: Creating event {request.name}")
    result = await client.create_event(
        name=request.name,
        description=request.description,
        event_type_id=request.event_type_id,
        zone_id=request.zone_id,
        date=request.date,
        priority=request.priority.value,
        status=request.status.value
    )
    return result

@router.put(
    "/events/{event_id}",
    response_model=dict,
    summary="Mettre à jour un événement"
)
async def update_event(
    event_id: str,
    request: UpdateEventRequest,
    client: UrbanEventsGraphQLClient = Depends(get_urban_client)
):
    """
    Met à jour un événement existant.
    
    Tous les champs sont optionnels. Seuls les champs fournis seront mis à jour.
    """
    logger.info(f"Gateway: Updating event {event_id}")
    
    # Préparer les kwargs en excluant les valeurs None
    update_data = {
        k: v.value if hasattr(v, 'value') else v
        for k, v in request.model_dump(exclude_unset=True).items()
    }
    
    result = await client.update_event(event_id, **update_data)
    return result

@router.delete(
    "/events/{event_id}",
    summary="Supprimer un événement"
)
async def delete_event(
    event_id: str,
    client: UrbanEventsGraphQLClient = Depends(get_urban_client)
):
    """
    Supprime un événement.
    """
    logger.info(f"Gateway: Deleting event {event_id}")
    result = await client.delete_event(event_id)
    return result

@router.get(
    "/events/by-zone/{zone_id}/active",
    response_model=List[dict],
    summary="Événements actifs d'une zone"
)
async def get_active_events_by_zone(
    zone_id: str,
    client: UrbanEventsGraphQLClient = Depends(get_urban_client)
):
    """
    Récupère tous les événements actifs (status != RESOLVED, CANCELLED) d'une zone.
    """
    logger.info(f"Gateway: Getting active events for zone {zone_id}")
    
    # Récupérer les événements IN_PROGRESS et PENDING
    events_in_progress = await client.get_events(
        zone_id=zone_id,
        status="IN_PROGRESS"
    )
    events_pending = await client.get_events(
        zone_id=zone_id,
        status="PENDING"
    )
    
    # Combiner les résultats
    active_events = events_in_progress + events_pending
    
    return active_events