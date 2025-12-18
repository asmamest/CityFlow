"""Modèles Pydantic pour le service Événements Urbains"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class EventPriority(str, Enum):
    """Priorités d'événements"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EventStatus(str, Enum):
    """Statuts d'événements"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"

class Zone(BaseModel):
    """Zone urbaine"""
    id: str
    name: str
    description: Optional[str] = None

class EventType(BaseModel):
    """Type d'événement"""
    id: str
    name: str
    description: Optional[str] = None

class Event(BaseModel):
    """Événement urbain complet"""
    id: str
    name: str
    description: str
    eventTypeId: str
    zoneId: str
    date: str
    priority: str
    status: str
    createdAt: str
    updatedAt: str
    eventType: Optional[EventType] = None
    zone: Optional[Zone] = None

class GetEventsRequest(BaseModel):
    """Requête pour filtrer les événements"""
    event_type_id: Optional[str] = None
    zone_id: Optional[str] = None
    status: Optional[EventStatus] = None
    priority: Optional[EventPriority] = None
    date_from: Optional[str] = Field(None, description="Date ISO format")
    date_to: Optional[str] = Field(None, description="Date ISO format")

class CreateEventRequest(BaseModel):
    """Requête pour créer un événement"""
    name: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    event_type_id: str
    zone_id: str
    date: str = Field(..., description="Date ISO format")
    priority: EventPriority
    status: EventStatus = EventStatus.PENDING

class UpdateEventRequest(BaseModel):
    """Requête pour mettre à jour un événement"""
    name: Optional[str] = Field(None, min_length=3)
    description: Optional[str] = Field(None, min_length=10)
    event_type_id: Optional[str] = None
    zone_id: Optional[str] = None
    date: Optional[str] = None
    priority: Optional[EventPriority] = None
    status: Optional[EventStatus] = None

class EventMutationResponse(BaseModel):
    """Réponse d'une mutation"""
    success: bool
    message: str
    event: Optional[Event] = None