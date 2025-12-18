FROM python:3.11-slim

LABEL maintainer="smart-city-gateway"
LABEL description="API Gateway pour plateforme Smart City - Multi-protocoles"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer répertoire de travail
WORKDIR /app

# Installer dépendances système pour SOAP et gRPC
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le fichier proto
COPY protos/emergency.proto protos/

# Générer les stubs gRPC depuis le proto
RUN python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./protos \
    --grpc_python_out=./protos \
    ./protos/emergency.proto

# Copier tout le code source de la gateway
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p logs

# Exposer le port de l'API Gateway
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)"

# Commande de démarrage avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]