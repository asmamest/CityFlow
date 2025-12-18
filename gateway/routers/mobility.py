"""Router FastAPI pour le service Mobilité (REST)"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from  clients import MobilityRestClient
from  models.mobility import (
    LigneCreate, LigneUpdate, LigneResponse,
    HorairesResponse, TraficResponse, DisponibiliteResponse
)
from  utils import logger

router = APIRouter(prefix="/mobility", tags=["Mobilité"])

# Dependency pour le client
async def get_mobility_client():
    client = MobilityRestClient()
    try:
        yield client
    finally:
        await client.close()

@router.get("/", summary="Page d'accueil du service Mobilité")
async def mobility_home():
    """Informations sur le service Mobilité"""
    return {
        "service": "Mobilité",
        "version": "1.0.0",
        "description": "Service de gestion des transports en commun",
        "endpoints": [
            "/mobility/horaires/{ligne}",
            "/mobility/trafic",
            "/mobility/disponibilite",
            "/mobility/lignes"
        ]
    }

@router.get(
    "/horaires/{ligne}",
    response_model=dict,
    summary="Consulter les horaires d'une ligne"
)
async def get_horaires(
    ligne: str,
    client: MobilityRestClient = Depends(get_mobility_client)
):
    """
    Récupère les horaires d'une ligne de transport.
    
    - **ligne**: Numéro de la ligne (ex: L1, B15, T3)
    """
    logger.info(f"Gateway: Getting horaires for ligne {ligne}")
    result = await client.get_horaires(ligne)
    return result

@router.get(
    "/trafic",
    response_model=dict,
    summary="État du trafic en temps réel"
)
async def get_trafic(
    client: MobilityRestClient = Depends(get_mobility_client)
):
    """
    Récupère l'état actuel du trafic pour toutes les lignes.
    
    États possibles: normal, ralenti, perturbé, interrompu
    """
    logger.info("Gateway: Getting traffic status")
    result = await client.get_trafic()
    return result

@router.get(
    "/disponibilite",
    response_model=dict,
    summary="Disponibilité des véhicules"
)
async def get_disponibilite(
    client: MobilityRestClient = Depends(get_mobility_client)
):
    """
    Récupère la disponibilité actuelle des véhicules par type de transport.
    """
    logger.info("Gateway: Getting vehicle availability")
    result = await client.get_disponibilite()
    return result

@router.get(
    "/lignes",
    response_model=List[dict],
    summary="Liste toutes les lignes"
)
async def list_lignes(
    client: MobilityRestClient = Depends(get_mobility_client)
):
    """
    Liste toutes les lignes de transport configurées.
    """
    logger.info("Gateway: Listing all lignes")
    result = await client.get_lignes()
    return result

@router.get(
    "/lignes/{ligne_id}",
    response_model=dict,
    summary="Détails d'une ligne"
)
async def get_ligne(
    ligne_id: str,
    client: MobilityRestClient = Depends(get_mobility_client)
):
    """
    Récupère les détails d'une ligne par son ID.
    """
    logger.info(f"Gateway: Getting ligne {ligne_id}")
    result = await client.get_ligne(ligne_id)
    return result

@router.post(
    "/lignes",
    response_model=dict,
    status_code=201,
    summary="Créer une nouvelle ligne"
)
async def create_ligne(
    ligne: LigneCreate,
    client: MobilityRestClient = Depends(get_mobility_client)
):
    """
    Crée une nouvelle ligne de transport.
    """
    logger.info(f"Gateway: Creating ligne {ligne.numero}")
    result = await client.create_ligne(ligne.model_dump())
    return result

@router.put(
    "/lignes/{ligne_id}",
    response_model=dict,
    summary="Mettre à jour une ligne"
)
async def update_ligne(
    ligne_id: str,
    ligne: LigneUpdate,
    client: MobilityRestClient = Depends(get_mobility_client)
):
    """
    Met à jour une ligne existante.
    """
    logger.info(f"Gateway: Updating ligne {ligne_id}")
    result = await client.update_ligne(
        ligne_id,
        ligne.model_dump(exclude_unset=True)
    )
    return result

@router.delete(
    "/lignes/{ligne_id}",
    summary="Supprimer une ligne"
)
async def delete_ligne(
    ligne_id: str,
    client: MobilityRestClient = Depends(get_mobility_client)
):
    """
    Supprime une ligne de transport.
    """
    logger.info(f"Gateway: Deleting ligne {ligne_id}")
    result = await client.delete_ligne(ligne_id)
    return result