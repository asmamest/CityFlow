# 🏗️ Architecture - Smart City API Gateway

## 📐 Vue d'Ensemble de l'Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENTS (Web/Mobile)                            │
│                    React • Vue • Angular • Mobile Apps                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────────────────┐
│                    🚪 API GATEWAY (FastAPI)                              │
│                         Port 8080                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Routers                Clients              Middleware           │   │
│  │  • /mobility/*        • REST Client        • CORS                │   │
│  │  • /air/*             • SOAP Client        • Logging             │   │
│  │  • /emergency/*       • gRPC Client        • Error Handling      │   │
│  │  • /urban/*           • GraphQL Client     • Validation          │   │
│  │  • /smart-city/*                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
         │                 │                 │                 │
         ↓ REST            ↓ SOAP            ↓ gRPC           ↓ GraphQL
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 🚗 Mobilité  │  │ 🌫️ Qualité   │  │ 🚨 Urgences  │  │ 📅 Événements│
│   Service    │  │  de l'Air    │  │   Service    │  │   Urbains    │
│              │  │   Service    │  │              │  │   Service    │
│  Port: 8000  │  │  Port: 8001  │  │ Port: 50051  │  │  Port: 8004  │
│              │  │              │  │              │  │              │
│  • Horaires  │  │  • AQI       │  │  • Alertes   │  │  • Zones     │
│  • Trafic    │  │  • Polluants │  │  • Tracking  │  │  • Événements│
│  • Lignes    │  │  • Compare   │  │  • History   │  │  • Types     │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
         │
         ↓
┌──────────────┐
│  🗄️ PostgreSQL│
│  Port: 5433  │
│              │
│  • Lignes    │
│  • Horaires  │
└──────────────┘

           [smart-city-network - Docker Bridge Network]
```

## 🔄 Flux de Données - Workflow Plan Trip

```
1. CLIENT REQUEST
   │
   ↓
   POST /smart-city/plan-trip
   {
     "zone_depart": "downtown",
     "zone_arrivee": "industrial",
     "heure_depart": "14:30"
   }
   │
   ↓
2. API GATEWAY PROCESSING
   │
   ├──→ [SOAP Client] → Air Quality Service
   │    └─→ GetAQI("downtown")
   │    └─→ GetAQI("industrial")
   │
   ├──→ [REST Client] → Mobility Service
   │    └─→ GET /trafic
   │    └─→ GET /disponibilite
   │
   ├──→ [gRPC Client] → Emergency Service
   │    └─→ GetActiveAlerts("downtown")
   │    └─→ GetActiveAlerts("industrial")
   │
   └──→ [GraphQL Client] → Urban Events Service
        └─→ query { events(zoneId: "downtown", status: "IN_PROGRESS") }
        └─→ query { events(zoneId: "industrial", status: "IN_PROGRESS") }
   │
   ↓
3. DATA AGGREGATION & ANALYSIS
   │
   ├─→ Compare AQI values
   ├─→ Analyze traffic conditions
   ├─→ Evaluate emergency alerts
   ├─→ Check urban events impact
   └─→ Generate intelligent recommendations
   │
   ↓
4. RESPONSE FORMATTING
   │
   └─→ JSON Response with:
       • Air quality analysis
       • Transport recommendations
       • Active alerts
       • Impacting events
       • Route suggestions
       • Comfort level
   │
   ↓
5. CLIENT RECEIVES COMPLETE ANALYSIS
```

## 🔌 Communication Protocols

### REST (Mobilité)

```
Client → HTTP Request → Gateway → HTTP Request → Mobility Service
                                     ↓
                                 PostgreSQL
                                     ↓
Gateway ← JSON Response ← Mobility Service
```

### SOAP (Qualité de l'Air)

```
Client → HTTP Request → Gateway → SOAP Envelope (XML) → Air Quality Service
                                     ↓
                                  CSV Data
                                     ↓
Gateway ← JSON Response ← SOAP Response (XML) ← Air Quality Service
```

### gRPC (Urgences)

```
Client → HTTP Request → Gateway → Protocol Buffers → Emergency Service
                                     ↓
                                 In-Memory Store
                                     ↓
Gateway ← JSON Response ← Protocol Buffers ← Emergency Service
```

### GraphQL (Événements)

```
Client → HTTP Request → Gateway → GraphQL Query → Urban Events Service
                                     ↓
                                 In-Memory Store
                                     ↓
Gateway ← JSON Response ← GraphQL Response ← Urban Events Service
```

## 📊 Matrice des Endpoints

| Service     | Protocol      | Base Path     | Endpoints                                                   | Port  |
| ----------- | ------------- | ------------- | ----------------------------------------------------------- | ----- |
| Gateway     | HTTP/REST     | `/`           | `/`, `/health`, `/info`                                     | 8080  |
| Mobilité    | REST          | `/mobility`   | `/trafic`, `/horaires/{ligne}`, `/disponibilite`, `/lignes` | 8000  |
| Qualité Air | SOAP          | `/air`        | `/aqi/{zone}`, `/pollutants/{zone}`, `/compare`, `/history` | 8001  |
| Urgences    | gRPC          | `/emergency`  | `/alerts`, `/alerts/active/{zone}`, `/alerts/{id}/status`   | 50051 |
| Événements  | GraphQL       | `/urban`      | `/zones`, `/events`, `/event-types`                         | 8004  |
| Workflow    | Orchestration | `/smart-city` | `/plan-trip`, `/health`                                     | 8080  |

## 🏭 Patterns de Design Utilisés

### 1. API Gateway Pattern

- Point d'entrée unique pour tous les clients
- Abstraction des microservices backend
- Routage intelligent des requêtes

### 2. Service Adapter Pattern

- Clients spécifiques pour chaque protocole
- Conversion uniforme en JSON
- Isolation des changements backend

### 3. Orchestration Pattern

- Coordination de multiples services
- Workflow métier complexe (`/plan-trip`)
- Agrégation intelligente des données

### 4. Circuit Breaker Pattern (Implicite)

- Timeouts configurables
- Gestion des erreurs par service
- Réponses dégradées en cas d'échec

## 🔒 Sécurité

### Actuellement Implémenté

- ✅ CORS configuré
- ✅ Validation des entrées avec Pydantic
- ✅ Gestion des erreurs centralisée
- ✅ Health checks
- ✅ Logging des requêtes

### Recommandations pour Production

- 🔐 Authentification JWT
- 🔐 Rate limiting
- 🔐 HTTPS obligatoire
- 🔐 API Keys pour les clients
- 🔐 Whitelist d'IP
- 🔐 Encryption des données sensibles

## 📈 Scalabilité

### Horizontal Scaling

```
┌─────────────┐
│  Load       │
│  Balancer   │
└─────────────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌──▼──┐
│ GW1 │ │ GW2 │  ← Multiple instances of Gateway
└─────┘ └─────┘
```

### Vertical Scaling

- Augmenter les workers Uvicorn
- Optimiser les connexions DB
- Cache Redis pour les données fréquentes

### Service Mesh (Futur)

```
Gateway → Istio/Linkerd → Services
  └─→ Service Discovery
  └─→ Load Balancing
  └─→ Tracing
  └─→ Metrics
```

## 📊 Monitoring & Observability

### Logs

```
Gateway → Structured JSON Logs → ELK Stack
  ├─→ Request/Response logging
  ├─→ Error tracking
  └─→ Performance metrics
```

### Métriques (Future)

```
Gateway → Prometheus
  ├─→ Request rate
  ├─→ Response time
  ├─→ Error rate
  └─→ Service availability

Prometheus → Grafana → Dashboards
```

### Tracing (Future)

```
Gateway → Jaeger/Zipkin
  └─→ Distributed tracing across services
  └─→ Performance bottleneck identification
```

## 🔄 Resilience

### Retry Strategy

```python
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

try:
    response = await service_call()
except Exception:
    for i in range(MAX_RETRIES):
        await asyncio.sleep(RETRY_DELAY)
        response = await service_call()
```

### Timeout Strategy

```
REST:     10 seconds
SOAP:     15 seconds
gRPC:     10 seconds
GraphQL:  10 seconds
```

### Fallback Strategy

```
If Service Unavailable:
  └─→ Return cached data (if available)
  └─→ Return degraded response
  └─→ Log warning for monitoring
```

## 🧩 Extensibilité

### Ajouter un Nouveau Service

1. **Créer le client** (`gateway/clients/new_service_client.py`)

```python
class NewServiceClient:
    async def call_endpoint(self):
        # Implementation
        pass
```

2. **Créer les modèles** (`gateway/models/new_service.py`)

```python
class NewServiceRequest(BaseModel):
    # Fields
    pass
```

3. **Créer le router** (`gateway/routers/new_service.py`)

```python
router = APIRouter(prefix="/new", tags=["New Service"])

@router.get("/endpoint")
async def get_data():
    # Implementation
    pass
```

4. **Inclure le router** dans `main.py`

```python
app.include_router(new_service_router)
```

## 📝 Best Practices Appliquées

✅ **Separation of Concerns**: Chaque composant a une responsabilité unique
✅ **DRY (Don't Repeat Yourself)**: Code réutilisable via clients et utils
✅ **Error Handling**: Gestion centralisée des erreurs
✅ **Logging**: Logs structurés pour debugging
✅ **Type Safety**: Utilisation de Pydantic pour validation
✅ **Async/Await**: Opérations asynchrones pour performance
✅ **Docker**: Containerisation pour portabilité
✅ **Documentation**: OpenAPI/Swagger auto-générée

## 🎯 Prochaines Améliorations

1. **Cache Layer** (Redis)

   - Cache des réponses fréquentes
   - Invalidation intelligente
   - TTL configurables

2. **Message Queue** (RabbitMQ/Kafka)

   - Événements asynchrones
   - Communication découplée
   - Résilience accrue

3. **Service Discovery** (Consul/Eureka)

   - Découverte automatique des services
   - Health checking
   - Load balancing dynamique

4. **API Versioning**
   - `/v1/`, `/v2/` endpoints
   - Backward compatibility
   - Migration progressive

---

**Version**: 1.0.0  
**Dernière mise à jour**: Décembre 2025
