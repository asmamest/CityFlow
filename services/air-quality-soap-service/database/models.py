"""
Modèles SQLAlchemy pour la base de données
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database.connection import Base



class LigneModel(Base):
    __tablename__ = "lignes"
    id = Column(String(36), primary_key=True)
    
    
    
class ZoneModel(Base):
    """Table des zones géographiques (référentiel partagé)"""
    __tablename__ = "zones"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    # Relations
    measurements = relationship(
        "AirQualityMeasurementModel",
        back_populates="zone",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Zone {self.id}: {self.name}>"


class AirQualityMeasurementModel(Base):
    """Table des mesures de qualité de l'air"""
    __tablename__ = "air_quality_measurements"
    
    id = Column(String(36), primary_key=True)
    zone_id = Column(String(36), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True)
    aqi = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    zone = relationship("ZoneModel", back_populates="measurements")
    pollutants = relationship("PollutantModel", back_populates="measurement", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Measurement AQI={self.aqi} Zone={self.zone_id}>"

class PollutantModel(Base):
    """Table des polluants"""
    __tablename__ = "pollutants"

    id = Column(String(36), primary_key=True)

    measurement_id = Column(
        String(36),
        ForeignKey("air_quality_measurements.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    air_quality_id = Column(
        String,
        ForeignKey("air_quality_ligne.id"),
        nullable=True,
        index=True
    )
    nom = Column(String(50), nullable=False)
    valeur = Column(Float, nullable=False)
    unite = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    # Relations
    measurement = relationship(
        "AirQualityMeasurementModel",
        back_populates="pollutants"
    )
    air_quality = relationship(
        "AirQualityLigneModel",
        backref="polluants"
    )

    def __repr__(self):
        return f"<Pollutant {self.nom}={self.valeur}{self.unite}>"




class AirQualityLigneModel(Base):
    __tablename__ = "air_quality_ligne"

    id = Column(String, primary_key=True)
    ligne_id = Column(String, ForeignKey("lignes.id"), nullable=False)

    aqi = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    ligne = relationship("LigneModel", backref="air_quality")
