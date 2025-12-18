# 🚀 Guide de Démarrage Rapide - Smart City Gateway

## ⚡ Démarrage en 5 minutes

### 1️⃣ Prérequis

```bash
# Vérifier Docker
docker --version
# Docker version 20.10.0 ou supérieur requis

# Vérifier Docker Compose
docker-compose --version
# Version 2.0.0 ou supérieur requis
```

### 2️⃣ Lancement

```bash
# Cloner et accéder au répertoire
cd smart-city-platform

# Démarrer tous les services
docker-compose up -d

# Attendre 60 secondes pour l'initialisation
sleep 60

# Vérifier que tout est UP
docker-compose ps
```

### 3️⃣ Vérification

```bash
# Test rapide de la Gateway
curl http://localhost:8080/health

# Réponse attendue:
# {"status":"healthy","service":"api-gateway","version":"1.0.0",...}
```

### 4️⃣ Exploration

Ouvrez votre navigateur:

- **Documentation Interactive**: http://localhost:8080/docs
- **Page d'accueil**: http://localhost:8080/

### 5️⃣ Premier Test - Workflow Complet

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

## 📚 Exemples Rapides

### Test Mobilité (REST)

```bash
curl http://localhost:8080/mobility/trafic
```

### Test Qualité de l'Air (SOAP)

```bash
curl http://localhost:8080/air/aqi/downtown
```

### Test Urgences (gRPC)

```bash
curl "http://localhost:8080/emergency/alerts/active/downtown"
```

### Test Événements (GraphQL)

```bash
curl http://localhost:8080/urban/zones
```

## 🛑 Arrêt

```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

## 🐛 Dépannage Rapide

### Problème: Service ne démarre pas

```bash
# Voir les logs
docker-compose logs -f api-gateway

# Rebuild le service
docker-compose up -d --build api-gateway
```

### Problème: Port déjà utilisé

```bash
# Vérifier les ports
lsof -i :8080
lsof -i :8000
lsof -i :8001

# Arrêter le processus ou changer le port dans docker-compose.yml
```

### Problème: Services ne communiquent pas

```bash
# Vérifier le réseau Docker
docker network inspect smart-city-network

# Redémarrer tous les services
docker-compose restart
```

## 📊 Tests Automatisés

```bash
# Rendre le script exécutable
chmod +x test_gateway.sh

# Exécuter tous les tests
./test_gateway.sh
```

## 🎯 Prochaines Étapes

1. ✅ Explorer la documentation Swagger: http://localhost:8080/docs
2. ✅ Tester le workflow `/smart-city/plan-trip`
3. ✅ Consulter le README.md complet pour plus de détails
4. ✅ Personnaliser les configurations dans docker-compose.yml
5. ✅ Intégrer avec votre application frontend

## 🆘 Besoin d'aide ?

- **Documentation complète**: Voir README.md
- **Logs**: `docker-compose logs -f`
- **Health Check**: `curl http://localhost:8080/smart-city/health`

---

Bon développement ! 🏙️✨
