# 🏙️ Smart City Platform - API Gateway

## 📋 Vue d'ensemble

Plateforme intelligente d'orchestration de microservices pour une ville connectée. Cette API Gateway unifie **4 microservices** utilisant différents protocoles de communication (REST, SOAP, gRPC, GraphQL) pour fournir une expérience utilisateur cohérente.

## 🎯 Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                      🌐 CLIENT (Web)                          │
└──────────────────────────────────────────────────────────────────────┘
                                   ↓
┌──────────────────────────────────────────────────────────────────────┐
│                   🚪 API GATEWAY (FastAPI)                           │
│                        Port: 8080                                     │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
         ↓              ↓              ↓              ↓
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │  REST  │    │  SOAP  │    │  gRPC  │    │GraphQL │
    └────────┘    └────────┘    └────────┘    └────────┘
         ↓              ↓              ↓              ↓
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │🚗      │    │🌫️      │    │🚨      │    │📅      │
    │Mobilité│    │Qualité │    │Urgences│    │Événe-  │
    │        │    │de l'Air│    │        │    │ments   │
    │:8000   │    │:8001   │    │:50051  │    │:8004   │
    └────────┘    └────────┘    └────────┘    └────────┘
        ↓                ↓                         ↓
                  ┌────────┐
                  │  🗄️     │
                  │Postgres│
                  │:5433   │
                  └────────┘
```

## 🎨 Services Intégrés

### 1. 🚗 Service Mobilité (REST)

- **Protocole**: REST/HTTP
- **Port**: 8000
- **Fonctionnalités**:
  - Consultation des horaires de transport
  - État du trafic en temps réel
  - Disponibilité des véhicules
  - CRUD des lignes de transport

### 2. 🌫️ Service Qualité de l'Air (SOAP)

- **Protocole**: SOAP/XML
- **Port**: 8001
- **Fonctionnalités**:
  - Indice de qualité de l'air (AQI)
  - Niveaux de polluants
  - Comparaison entre zones
  - Historique des données

### 3. 🚨 Service Urgences (gRPC)

- **Protocole**: gRPC/Protocol Buffers
- **Port**: 50051
- **Fonctionnalités**:
  - Création d'alertes d'urgence
  - Suivi des interventions
  - Historique et statistiques
  - Notifications en temps réel

### 4. 📅 Service Événements Urbains (GraphQL)

- **Protocole**: GraphQL
- **Port**: 8004
- **Fonctionnalités**:
  - Gestion des événements urbains
  - Zones et types d'événements
  - Filtrage avancé
  - Mutations CRUD

## 🚀 Démarrage Rapide

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 8 Go RAM minimum
- Ports disponibles: 8080, 8000, 8001, 8004, 50051, 5433

### Installation

```bash
# 1. Cloner le projet
git clone <repository-url>
cd smart-city-platform

# 2. Vérifier la structure
ls -la
# Vous devriez voir: gateway/, services/, docker-compose.yml

# 3. Démarrer tous les services
docker-compose up -d

# 4. Vérifier que tous les services sont UP
docker-compose ps

# 5. Consulter les logs
docker-compose logs -f api-gateway
```

### Accès à la documentation

Une fois les services démarrés, accédez à:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

## 📚 Utilisation de l'API Gateway

### Endpoints Principaux

#### 🏠 Accueil

```bash
curl http://localhost:8080/
```

#### 🏥 Health Check Global

```bash
curl http://localhost:8080/smart-city/health
```

#### 🚀 Workflow Métier - Planification de Trajet

```bash
curl -X POST "http://localhost:8080/smart-city/plan-trip" \
  -H "Content-Type: application/json" \
  -d '{
    "zone_depart": "downtown",
    "zone_arrivee": "industrial",
    "heure_depart": "14:30",
    "preferences": ["metro", "bus"]
  }'
```

### Endpoints par Service

#### 🚗 Mobilité (REST)

```bash
# Horaires d'une ligne
curl http://localhost:8080/mobility/horaires/L1

# État du trafic
curl http://localhost:8080/mobility/trafic

# Disponibilité des véhicules
curl http://localhost:8080/mobility/disponibilite

# Lister les lignes
curl http://localhost:8080/mobility/lignes
```

#### 🌫️ Qualité de l'Air (SOAP)

```bash
# AQI d'une zone
curl http://localhost:8080/air/aqi/downtown

# Polluants
curl http://localhost:8080/air/pollutants/downtown

# Comparer deux zones
curl -X POST http://localhost:8080/air/compare \
  -H "Content-Type: application/json" \
  -d '{"zone_a": "downtown", "zone_b": "park"}'
```

#### 🚨 Urgences (gRPC)

```bash
# Créer une alerte
curl -X POST http://localhost:8080/emergency/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "type": "FIRE",
    "description": "Incendie dans un immeuble",
    "location": {
      "latitude": 36.8065,
      "longitude": 10.1815,
      "address": "123 Rue Principale",
      "city": "Tunis",
      "zone": "downtown"
    },
    "priority": "CRITICAL",
    "reporter_name": "Ahmed Ben Ali",
    "reporter_phone": "+21612345678",
    "affected_people": 10
  }'

# Alertes actives d'une zone
curl "http://localhost:8080/emergency/alerts/active/downtown"
```

#### 📅 Événements Urbains (GraphQL)

```bash
# Lister les zones
curl http://localhost:8080/urban/zones

# Lister les événements
curl "http://localhost:8080/urban/events?status=IN_PROGRESS"

# Créer un événement
curl -X POST http://localhost:8080/urban/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marathon de la ville",
    "description": "Course annuelle dans le centre-ville",
    "event_type_id": "evt_001",
    "zone_id": "zone_001",
    "date": "2025-12-15T08:00:00",
    "priority": "HIGH"
  }'
```

## 🎯 Workflow Métier Intelligent

Le endpoint `/smart-city/plan-trip` est le **cœur de l'orchestration**. Il interroge **tous les microservices** simultanément pour fournir une analyse complète du trajet.

### Flux d'Exécution

```
1. 📡 COLLECTE DES DONNÉES
   ├─ SOAP → Qualité de l'air (départ & arrivée)
   ├─ REST → Trafic & disponibilité des transports
   ├─ gRPC → Alertes d'urgence actives
   └─ GraphQL → Événements urbains en cours

2. 🧮 ANALYSE INTELLIGENTE
   ├─ Comparaison AQI entre zones
   ├─ Évaluation des perturbations
   ├─ Calcul du niveau de confort
   └─ Génération de recommandations

3. 🎯 RECOMMANDATIONS
   ├─ Itinéraire principal
   ├─ Alternatives (écologique, rapide)
   ├─ Alertes et avertissements
   └─ Conseil personnalisé
```

### Exemple de Réponse

```json
{
  "success": true,
  "message": "Analyse complète du trajet générée avec succès",
  "analysis": {
    "zone_depart": "downtown",
    "zone_arrivee": "industrial",
    "heure_demandee": "14:30",
    "air_quality_depart": {
      "zone": "downtown",
      "aqi": 85,
      "category": "Moderate",
      "recommendation": "✅ Qualité acceptable - Privilégiez les transports fermés"
    },
    "air_quality_arrivee": {
      "zone": "industrial",
      "aqi": 142,
      "category": "Unhealthy for Sensitive Groups",
      "recommendation": "⚠️ Qualité médiocre - Évitez les modes de transport ouverts"
    },
    "transports_disponibles": [
      {
        "ligne": "Metro L1",
        "type_transport": "Metro",
        "etat_trafic": "normal",
        "disponibilite": "87%",
        "horaires_prochain_passage": ["14:30", "14:45", "15:00"]
      }
    ],
    "alertes_actives": [],
    "niveau_alerte_global": "LOW",
    "evenements_impactants": [],
    "recommandation_principale": {
      "type": "alternatif",
      "description": "Itinéraire alternatif recommandé en raison de: pollution élevée",
      "lignes_suggerees": ["Metro L1", "Bus B15"],
      "duree_estimee": "25-30 minutes"
    },
    "conseil_principal": "⚠️ Conditions acceptables mais soyez vigilant aux perturbations.",
    "niveau_confort": "bon"
  },
  "warnings": [],
  "processing_time_ms": 1234.56
}
```

## 🔧 Configuration

### Variables d'Environnement

Les variables sont définies dans `docker-compose.yml`:

```yaml
# API Gateway
APP_NAME: "Smart City API Gateway"
DEBUG: "True"
LOG_LEVEL: "INFO"

# URLs des Services
MOBILITY_SERVICE_URL: "http://mobility-service:8000"
AIR_QUALITY_WSDL_URL: "http://air-quality-soap-service:8000/?wsdl"
EMERGENCY_GRPC_HOST: "emergency-grpc"
EMERGENCY_GRPC_PORT: "50051"
URBAN_EVENTS_GRAPHQL_URL: "http://urban-events-graphql:8004/graphql"

# Timeouts (secondes)
REST_TIMEOUT: "10"
SOAP_TIMEOUT: "15"
GRPC_TIMEOUT: "10"
GRAPHQL_TIMEOUT: "10"
```

## 🐛 Débogage

### Logs

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f api-gateway
docker-compose logs -f mobility-service
docker-compose logs -f air-quality-soap-service
docker-compose logs -f emergency-grpc
docker-compose logs -f urban-events-graphql
```

### Rebuild

```bash
# Rebuild un service
docker-compose up -d --build api-gateway

# Rebuild tous les services
docker-compose up -d --build
```

### Vérification de Santé

```bash
# Gateway
curl http://localhost:8080/health

# Tous les services via Gateway
curl http://localhost:8080/smart-city/health
```

## 🚢 Déploiement

### Production

Pour un déploiement en production:

1. **Modifier les variables d'environnement**:

   - `DEBUG: "False"`
   - Ajouter des secrets pour les mots de passe
   - Configurer CORS correctement

2. **Sécurité**:

   - Utiliser HTTPS
   - Ajouter un reverse proxy (Nginx/Traefik)
   - Activer l'authentification JWT

3. **Performance**:

   - Augmenter le nombre de workers Uvicorn
   - Mettre en place un cache Redis
   - Load balancing avec plusieurs instances

4. **Monitoring**:
   - Prometheus + Grafana
   - ELK Stack pour les logs
   - Alerting avec AlertManager

## 📊 Tests

### Tests Manuels avec cURL

```bash
# Test complet du workflow
./tests/test_plan_trip.sh

# Test de chaque service
./tests/test_mobility.sh
./tests/test_air_quality.sh
./tests/test_emergency.sh
./tests/test_urban_events.sh
```

### Tests Automatisés

```bash
# Installation de pytest
pip install pytest pytest-asyncio httpx

# Exécution des tests
pytest tests/ -v
```

## 🤝 Contribution

Les contributions sont bienvenues! Veuillez:

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- FastAPI pour le framework web
- Zeep pour le client SOAP
- gRPC pour la communication haute performance
- GraphQL pour les requêtes flexibles

---

Développé avec ❤️
