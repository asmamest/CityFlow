FROM python:3.10-slim

LABEL maintainer="air-quality-service"
LABEL description="Air Quality SOAP Service pour plateforme Smart City (PostgreSQL)"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    LOG_LEVEL=INFO \
    DATABASE_URL=postgresql+psycopg2://mobility_user:mobility_pass@smart-city-postgres:5432/mobility_db


# Créer répertoire de travail
WORKDIR /app

# Installer dépendances système (ajout de postgresql-client et libpq-dev)
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer dossiers nécessaires
RUN mkdir -p logs data wsdl

# Exposer le port
EXPOSE 8000

# Health check amélioré (vérifie uniquement si le service répond)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/?wsdl || exit 1

# Script d'attente pour PostgreSQL
COPY wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh

# OPTION 1: Avec Gunicorn (Production)
CMD ["/wait-for-postgres.sh", "postgres", "gunicorn", "wsgi:app", "-b", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]

# OPTION 2: Avec Python directement (Développement/Simple)
# CMD ["/wait-for-postgres.sh", "postgres", "python", "main.py"]