# scripts/init_db.py
from database.models import Base
from database.connection import engine

# Crée toutes les tables définies dans models.py
Base.metadata.create_all(bind=engine)
print("✅ Tables créées !")
