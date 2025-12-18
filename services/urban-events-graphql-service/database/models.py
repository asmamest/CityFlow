"""
Models SQLAlchemy pour le microservice Events

Architecture:
- ZoneModel: Mapping de la table partagée (lecture seule)
- EventModel: Table propre au microservice avec FK vers zones
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship, declarative_base

# Base SQLAlchemy
Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class EventStatus(str, Enum):
    """Statut des événements urbains"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class Priority(str, Enum):
    """Niveau de priorité des événements"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================================
# MODELS
# ============================================================================

class ZoneModel(Base):
    """
    Mapping de la table partagée 'zones'
    
    ⚠️ IMPORTANT:
    - Cette table existe déjà dans la base de données
    - Elle est partagée entre plusieurs microservices
    - Ne PAS créer/modifier/supprimer cette table
    - Utilisation en lecture seule uniquement
    """
    __tablename__ = "zones"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Pas de relation inverse pour éviter les dépendances circulaires
    # et respecter le principe de séparation des microservices


class EventModel(Base):
    """
    Table des événements urbains (propre au microservice)
    
    Gère les incidents, alertes et événements de la Smart City
    avec référence à une zone géographique existante.
    """
    __tablename__ = "events"
    
    # Identifiants
    id = Column(String(50), primary_key=True)
    
    # Informations de base
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Références externes
    zone_id = Column(
        String(50),
        ForeignKey("zones.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="FK vers la table partagée zones"
    )
    
    event_type_id = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Référence simple vers un type d'événement (futur microservice?)"
    )
    
    # Données métier
    date = Column(
        DateTime,
        nullable=False,
        index=True,
        comment="Date/heure de l'événement"
    )
    
    priority = Column(
        SQLEnum(Priority, name="priority_enum", create_type=True),
        nullable=False,
        default=Priority.MEDIUM,
        index=True
    )
    
    status = Column(
        SQLEnum(EventStatus, name="event_status_enum", create_type=True),
        nullable=False,
        default=EventStatus.PENDING,
        index=True
    )
    
    # Métadonnées
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Date de création"
    )
    
    updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow,
        comment="Date de dernière modification"
    )
    
    # ========================================================================
    # RELATIONS
    # ========================================================================
    
    zone = relationship(
        "ZoneModel",
        lazy="joined",  # Charge automatiquement la zone avec l'événement
        foreign_keys=[zone_id],
    )
    
    def __repr__(self) -> str:
        return (
            f"<EventModel(id={self.id!r}, name={self.name!r}, "
            f"status={self.status.value}, zone_id={self.zone_id!r})>"
        )
    
    def __str__(self) -> str:
        return f"Event: {self.name} ({self.status.value})"
