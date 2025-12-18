"""
Configuration et gestion de la connexion à la base de données PostgreSQL

Architecture:
- Session factory avec gestion du cycle de vie
- Pool de connexions optimisé pour FastAPI
- Support des variables d'environnement
- Health check intégré
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from pydantic_settings import BaseSettings

# Configuration du logger
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

class DatabaseSettings(BaseSettings):
    """
    Configuration de la base de données via variables d'environnement
    
    Variables d'env supportées:
    - DATABASE_URL: URL complète de connexion (prioritaire)
    - POSTGRES_USER: Nom d'utilisateur PostgreSQL
    - POSTGRES_PASSWORD: Mot de passe
    - POSTGRES_HOST: Hôte (défaut: localhost)
    - POSTGRES_PORT: Port (défaut: 5432)
    - POSTGRES_DB: Nom de la base de données
    - DB_POOL_SIZE: Taille du pool de connexions (défaut: 5)
    - DB_MAX_OVERFLOW: Connexions supplémentaires max (défaut: 10)
    - DB_ECHO: Afficher les requêtes SQL (défaut: False)
    """
    
    # Option 1: URL complète
    DATABASE_URL: Optional[str] = None
    
    # Option 2: Paramètres individuels
    POSTGRES_USER: str = "mobility_user"
    POSTGRES_PASSWORD: str = "mobility_pass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_DB: str = "mobility_db"
    
    # Configuration du pool de connexions
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600  # Recyclage toutes les heures
    DB_POOL_PRE_PING: bool = True  # Vérifie la connexion avant utilisation
    
    # Debugging
    DB_ECHO: bool = False
    DB_ECHO_POOL: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_database_url(self) -> str:
        """Construit l'URL de connexion PostgreSQL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# ============================================================================
# ENGINE & SESSION
# ============================================================================

class DatabaseManager:
    """
    Gestionnaire centralisé de la base de données
    
    Singleton pattern pour partager l'engine et la session factory
    """
    
    _instance: Optional['DatabaseManager'] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._initialize()
    
    def _initialize(self):
        """Initialise l'engine et la session factory"""
        settings = DatabaseSettings()
        database_url = settings.get_database_url()
        
        logger.info(f"Initializing database connection to {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
        
        # Création de l'engine avec pool de connexions
        self._engine = create_engine(
            database_url,
            poolclass=pool.QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=settings.DB_POOL_PRE_PING,
            echo=settings.DB_ECHO,
            echo_pool=settings.DB_ECHO_POOL,
            future=True,  # SQLAlchemy 2.0 style
        )
        
        # Configuration des événements de connexion
        self._setup_connection_events()
        
        # Création de la session factory
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,  # Important pour FastAPI
        )
        
        logger.info("Database connection initialized successfully")
    
    def _setup_connection_events(self):
        """Configure les événements de connexion PostgreSQL"""
        
        @event.listens_for(self._engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Event déclenché à chaque nouvelle connexion"""
            logger.debug("New database connection established")
        
        @event.listens_for(self._engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Event déclenché quand une connexion est récupérée du pool"""
            pass
    
    @property
    def engine(self) -> Engine:
        """Retourne l'engine SQLAlchemy"""
        if self._engine is None:
            raise RuntimeError("Database engine not initialized")
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Retourne la session factory"""
        if self._session_factory is None:
            raise RuntimeError("Session factory not initialized")
        return self._session_factory
    
    def create_session(self) -> Session:
        """Crée une nouvelle session"""
        return self.session_factory()
    
    def health_check(self) -> bool:
        """
        Vérifie la santé de la connexion à la base de données
        
        Returns:
            bool: True si la connexion est OK, False sinon
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.debug("Database health check: OK")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self):
        """Ferme toutes les connexions"""
        if self._engine:
            logger.info("Closing database connections")
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


# ============================================================================
# INSTANCES GLOBALES
# ============================================================================

# Instance singleton du gestionnaire
db_manager = DatabaseManager()

# Engine et session factory exposés pour faciliter l'utilisation
engine = db_manager.engine
SessionLocal = db_manager.session_factory


# ============================================================================
# DEPENDENCY INJECTION (FastAPI)
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection pour FastAPI
    
    Usage dans un resolver GraphQL ou endpoint REST:
    
    ```python
    from database.connection import get_db
    
    @app.post("/events")
    def create_event(event: EventCreate, db: Session = Depends(get_db)):
        # Utiliser db ici
        pass
    ```
    
    Yields:
        Session: Session SQLAlchemy avec gestion automatique du cycle de vie
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager pour utilisation en dehors de FastAPI
    
    Yields:
        Session: Session SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database context error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# UTILITAIRES
# ============================================================================

def init_db():
    """
    Initialise la base de données (crée les tables si nécessaire)
    
    """
    from database.models import Base
    
    logger.warning("Creating all tables - USE ALEMBIC IN PRODUCTION!")
    Base.metadata.create_all(bind=engine)
    logger.info("All tables created successfully")


def drop_all_tables():
    """
    
    À utiliser UNIQUEMENT en développement/test!
    """
    from database.models import Base
    
    logger.warning("Dropping all tables - THIS IS IRREVERSIBLE!")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")


async def check_database_health() -> dict:
    """
    Health check async pour FastAPI
    
    Usage:
    

    Returns:
        dict: Statut de santé de la base de données
    """
    try:
        is_healthy = db_manager.health_check()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "database": "postgresql",
            "pool_size": db_manager.engine.pool.size(),
            "checked_in": db_manager.engine.pool.checkedin(),
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# ============================================================================
# SHUTDOWN HANDLER
# ============================================================================

def shutdown_database():
    
    logger.info("Shutting down database connections")
    db_manager.close()