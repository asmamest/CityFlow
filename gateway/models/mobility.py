"""Modèles Pydantic pour le service Mobilité"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class TypeTransport(str, Enum):
    """Types de transport disponibles"""
    BUS = "bus"
    METRO = "metro"
    TRAIN = "train"
    TRAMWAY = "tramway"

class LigneCreate(BaseModel):
    """Modèle pour créer une ligne"""
    numero: str = Field(..., description="Numéro de la ligne (ex: L1, B15)")
    nom: str = Field(..., description="Nom de la ligne")
    type_transport: TypeTransport = Field(..., description="Type de transport")
    terminus_debut: str = Field(..., description="Terminus de départ")
    terminus_fin: str = Field(..., description="Terminus d'arrivée")
    actif: bool = Field(default=True, description="Ligne active ou non")

class LigneUpdate(BaseModel):
    """Modèle pour mettre à jour une ligne"""
    numero: Optional[str] = Field(None, description="Numéro de la ligne")
    nom: Optional[str] = Field(None, description="Nom de la ligne")
    type_transport: Optional[TypeTransport] = Field(None, description="Type de transport")
    terminus_debut: Optional[str] = Field(None, description="Terminus de départ")
    terminus_fin: Optional[str] = Field(None, description="Terminus d'arrivée")
    actif: Optional[bool] = Field(None, description="Ligne active ou non")

class LigneResponse(BaseModel):
    """Réponse complète d'une ligne"""
    id: str
    numero: str
    nom: str
    type_transport: str
    terminus_debut: str
    terminus_fin: str
    actif: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Horaire(BaseModel):
    """Modèle pour un horaire"""
    heure: str = Field(..., description="Heure de passage")
    station: str = Field(..., description="Nom de la station")
    direction: str = Field(..., description="Direction du trajet")

class HorairesResponse(BaseModel):
    """Réponse pour les horaires d'une ligne"""
    ligne: str
    horaires: List[Horaire]
    derniere_mise_a_jour: Optional[str] = None

class EtatTrafic(BaseModel):
    """État du trafic pour une ligne"""
    ligne: str
    etat: str = Field(..., description="normal, ralenti, perturbé, interrompu")
    message: Optional[str] = None
    derniere_mise_a_jour: Optional[str] = None

class TraficResponse(BaseModel):
    """Réponse globale de l'état du trafic"""
    lignes: List[EtatTrafic]
    timestamp: Optional[str] = None

class DisponibiliteVehicule(BaseModel):
    """Disponibilité d'un véhicule"""
    type_transport: str
    disponibles: int
    en_service: int
    en_maintenance: int
    taux_disponibilite: float = Field(..., ge=0, le=100)

class DisponibiliteResponse(BaseModel):
    """Réponse globale de disponibilité"""
    vehicules: List[DisponibiliteVehicule]
    timestamp: Optional[str] = None