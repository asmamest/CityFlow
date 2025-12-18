# 🌐 Guide d'Intégration Frontend - Smart City API Gateway

## 📋 Vue d'ensemble

Ce guide explique comment intégrer l'API Gateway Smart City dans une application Web frontend (React, Vue, Angular, etc.).

## 🔗 Configuration de Base

### URL de Base

```javascript
const API_BASE_URL = "http://localhost:8080";
// En production: 'https://api.smartcity.com'
```

### Client HTTP (Axios)

```javascript
import axios from "axios";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Intercepteur pour gérer les erreurs
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data);
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Client HTTP (Fetch)

```javascript
class SmartCityAPI {
  constructor(baseURL = "http://localhost:8080") {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  }

  // GET request
  get(endpoint) {
    return this.request(endpoint, { method: "GET" });
  }

  // POST request
  post(endpoint, data) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}

const api = new SmartCityAPI();
export default api;
```

## 🎯 Services par Fonctionnalité

### 1. Service Mobilité 🚗

#### Récupérer l'état du trafic

```javascript
// React Hook Example
import { useState, useEffect } from "react";
import api from "./api";

function TrafficStatus() {
  const [traffic, setTraffic] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTraffic = async () => {
      try {
        const data = await api.get("/mobility/trafic");
        setTraffic(data);
      } catch (error) {
        console.error("Error fetching traffic:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTraffic();

    // Rafraîchir toutes les 30 secondes
    const interval = setInterval(fetchTraffic, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Chargement...</div>;

  return (
    <div className="traffic-status">
      <h2>État du Trafic</h2>
      {traffic?.lignes?.map((ligne) => (
        <div key={ligne.ligne} className={`ligne ligne-${ligne.etat}`}>
          <span>{ligne.ligne}</span>
          <span className="badge">{ligne.etat}</span>
        </div>
      ))}
    </div>
  );
}
```

#### Consulter les horaires

```javascript
async function getHoraires(ligneName) {
  try {
    const data = await api.get(`/mobility/horaires/${ligneName}`);
    return data;
  } catch (error) {
    console.error("Error fetching horaires:", error);
    throw error;
  }
}

// Utilisation
const horaires = await getHoraires("L1");
console.log(horaires);
```

### 2. Service Qualité de l'Air 🌫️

#### Afficher l'AQI d'une zone

```javascript
function AirQualityWidget({ zone }) {
  const [aqi, setAqi] = useState(null);

  useEffect(() => {
    const fetchAQI = async () => {
      const data = await api.get(`/air/aqi/${zone}`);
      setAqi(data);
    };
    fetchAQI();
  }, [zone]);

  const getAQIColor = (value) => {
    if (value <= 50) return "green";
    if (value <= 100) return "yellow";
    if (value <= 150) return "orange";
    if (value <= 200) return "red";
    return "purple";
  };

  return (
    <div className="aqi-widget">
      <h3>Qualité de l'air - {zone}</h3>
      {aqi && (
        <div
          className="aqi-value"
          style={{ backgroundColor: getAQIColor(aqi.aqi) }}
        >
          <div className="aqi-number">{aqi.aqi}</div>
          <div className="aqi-category">{aqi.category}</div>
        </div>
      )}
    </div>
  );
}
```

#### Comparer deux zones

```javascript
async function compareAirQuality(zoneA, zoneB) {
  try {
    const data = await api.post("/air/compare", {
      zone_a: zoneA,
      zone_b: zoneB,
    });
    return data;
  } catch (error) {
    console.error("Error comparing zones:", error);
    throw error;
  }
}

// Utilisation
const comparison = await compareAirQuality("downtown", "park");
console.log(`Meilleure zone: ${comparison.better_zone}`);
```

### 3. Service Urgences 🚨

#### Créer une alerte

```javascript
async function createEmergencyAlert(alertData) {
  try {
    const data = await api.post("/emergency/alerts", {
      type: alertData.type,
      description: alertData.description,
      location: {
        latitude: alertData.latitude,
        longitude: alertData.longitude,
        address: alertData.address,
        city: alertData.city,
        zone: alertData.zone,
      },
      priority: alertData.priority,
      reporter_name: alertData.reporterName,
      reporter_phone: alertData.reporterPhone,
      affected_people: alertData.affectedPeople || 0,
    });

    return data;
  } catch (error) {
    console.error("Error creating alert:", error);
    throw error;
  }
}

// Exemple d'utilisation dans un formulaire
function EmergencyForm() {
  const [formData, setFormData] = useState({
    type: "FIRE",
    description: "",
    latitude: 0,
    longitude: 0,
    priority: "HIGH",
    // ...
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await createEmergencyAlert(formData);
      alert(`Alerte créée avec succès! ID: ${result.alert_id}`);
    } catch (error) {
      alert("Erreur lors de la création de l'alerte");
    }
  };

  return <form onSubmit={handleSubmit}>{/* Formulaire */}</form>;
}
```

#### Afficher les alertes actives

```javascript
function ActiveAlerts({ zone }) {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetchAlerts = async () => {
      const data = await api.get(`/emergency/alerts/active/${zone}`);
      setAlerts(data);
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000); // Refresh toutes les 10s
    return () => clearInterval(interval);
  }, [zone]);

  return (
    <div className="alerts-container">
      <h2>🚨 Alertes Actives - {zone}</h2>
      {alerts.length === 0 ? (
        <p>Aucune alerte active</p>
      ) : (
        alerts.map((alert) => (
          <div
            key={alert.alert_id}
            className={`alert alert-${alert.priority.toLowerCase()}`}
          >
            <div className="alert-header">
              <span className="alert-type">{alert.type}</span>
              <span className="alert-priority">{alert.priority}</span>
            </div>
            <p>{alert.description}</p>
            <small>
              Créée le {new Date(alert.created_at).toLocaleString()}
            </small>
          </div>
        ))
      )}
    </div>
  );
}
```

### 4. Service Événements Urbains 📅

#### Lister les événements

```javascript
function EventsList({ filters = {} }) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const fetchEvents = async () => {
      const params = new URLSearchParams(filters).toString();
      const data = await api.get(`/urban/events?${params}`);
      setEvents(data);
    };
    fetchEvents();
  }, [filters]);

  return (
    <div className="events-list">
      {events.map((event) => (
        <div key={event.id} className="event-card">
          <h3>{event.name}</h3>
          <p>{event.description}</p>
          <div className="event-meta">
            <span>📍 {event.zone?.name}</span>
            <span>📅 {new Date(event.date).toLocaleDateString()}</span>
            <span className={`badge priority-${event.priority.toLowerCase()}`}>
              {event.priority}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

// Utilisation avec filtres
<EventsList
  filters={{
    status: "IN_PROGRESS",
    priority: "HIGH",
    zone_id: "zone_001",
  }}
/>;
```

## 🚀 Workflow Principal - Planification de Trajet

### Composant Complet React

```javascript
import { useState } from "react";
import api from "./api";

function TripPlanner() {
  const [formData, setFormData] = useState({
    zone_depart: "downtown",
    zone_arrivee: "industrial",
    heure_depart: "14:30",
    preferences: ["metro", "bus"],
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = await api.post("/smart-city/plan-trip", formData);
      setResult(data);
    } catch (error) {
      console.error("Error planning trip:", error);
      alert("Erreur lors de la planification du trajet");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="trip-planner">
      <h1>🚀 Planifier mon Trajet</h1>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Zone de départ</label>
          <select
            value={formData.zone_depart}
            onChange={(e) =>
              setFormData({ ...formData, zone_depart: e.target.value })
            }
          >
            <option value="downtown">Centre-ville</option>
            <option value="industrial">Zone Industrielle</option>
            <option value="park">Parc</option>
          </select>
        </div>

        <div className="form-group">
          <label>Zone d'arrivée</label>
          <select
            value={formData.zone_arrivee}
            onChange={(e) =>
              setFormData({ ...formData, zone_arrivee: e.target.value })
            }
          >
            <option value="downtown">Centre-ville</option>
            <option value="industrial">Zone Industrielle</option>
            <option value="park">Parc</option>
          </select>
        </div>

        <div className="form-group">
          <label>Heure de départ</label>
          <input
            type="time"
            value={formData.heure_depart}
            onChange={(e) =>
              setFormData({ ...formData, heure_depart: e.target.value })
            }
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Analyse en cours..." : "Planifier mon trajet"}
        </button>
      </form>

      {result && result.success && (
        <div className="trip-result">
          <h2>📊 Analyse de votre trajet</h2>

          {/* Qualité de l'air */}
          <div className="air-quality-section">
            <h3>🌫️ Qualité de l'air</h3>
            <div className="air-comparison">
              <div className="air-zone">
                <h4>{result.analysis.zone_depart}</h4>
                <div
                  className="aqi-badge"
                  data-category={result.analysis.air_quality_depart.category}
                >
                  AQI: {result.analysis.air_quality_depart.aqi}
                </div>
                <p>{result.analysis.air_quality_depart.recommendation}</p>
              </div>

              <div className="air-zone">
                <h4>{result.analysis.zone_arrivee}</h4>
                <div
                  className="aqi-badge"
                  data-category={result.analysis.air_quality_arrivee.category}
                >
                  AQI: {result.analysis.air_quality_arrivee.aqi}
                </div>
                <p>{result.analysis.air_quality_arrivee.recommendation}</p>
              </div>
            </div>
            <p className="comparison">
              {result.analysis.air_quality_comparison}
            </p>
          </div>

          {/* Transports disponibles */}
          <div className="transport-section">
            <h3>🚇 Transports Disponibles</h3>
            {result.analysis.transports_disponibles.map((transport, idx) => (
              <div key={idx} className="transport-card">
                <h4>{transport.ligne}</h4>
                <div className="transport-info">
                  <span>État: {transport.etat_trafic}</span>
                  <span>Disponibilité: {transport.disponibilite}</span>
                </div>
                <div className="horaires">
                  Prochains passages:{" "}
                  {transport.horaires_prochain_passage.join(", ")}
                </div>
              </div>
            ))}
          </div>

          {/* Alertes */}
          {result.analysis.alertes_actives.length > 0 && (
            <div className="alerts-section">
              <h3>🚨 Alertes Actives</h3>
              {result.analysis.alertes_actives.map((alert) => (
                <div
                  key={alert.alert_id}
                  className={`alert alert-${alert.priority.toLowerCase()}`}
                >
                  <strong>{alert.type}</strong>: {alert.description}
                </div>
              ))}
            </div>
          )}

          {/* Recommandation principale */}
          <div className="recommendation">
            <h3>🎯 Recommandation</h3>
            <div className="main-recommendation">
              <h4>{result.analysis.recommandation_principale.description}</h4>
              <p>
                Lignes suggérées:{" "}
                {result.analysis.recommandation_principale.lignes_suggerees.join(
                  ", "
                )}
              </p>
              <p>
                Durée estimée:{" "}
                {result.analysis.recommandation_principale.duree_estimee}
              </p>
            </div>
          </div>

          {/* Conseil global */}
          <div
            className={`overall-advice comfort-${result.analysis.niveau_confort}`}
          >
            <strong>{result.analysis.conseil_principal}</strong>
            <p>Niveau de confort: {result.analysis.niveau_confort}</p>
          </div>

          <small>Temps de traitement: {result.processing_time_ms}ms</small>
        </div>
      )}
    </div>
  );
}

export default TripPlanner;
```

## 🎨 Styles CSS Suggérés

```css
.aqi-badge {
  padding: 10px;
  border-radius: 8px;
  font-weight: bold;
  text-align: center;
}

.aqi-badge[data-category="Good"] {
  background: #00e400;
  color: white;
}

.aqi-badge[data-category="Moderate"] {
  background: #ffff00;
  color: black;
}

.aqi-badge[data-category="Unhealthy for Sensitive Groups"] {
  background: #ff7e00;
  color: white;
}

.alert {
  padding: 15px;
  margin: 10px 0;
  border-radius: 5px;
  border-left: 4px solid;
}

.alert-critical {
  background: #fee;
  border-color: #f00;
}

.alert-high {
  background: #ffe;
  border-color: #fa0;
}

.comfort-excellent {
  background: #e8f5e9;
  border: 2px solid #4caf50;
}

.comfort-bon {
  background: #fff9c4;
  border: 2px solid #ffc107;
}

.comfort-moyen {
  background: #ffe0b2;
  border: 2px solid #ff9800;
}

.comfort-difficile {
  background: #ffebee;
  border: 2px solid #f44336;
}
```

## 📱 Gestion des Erreurs

```javascript
// Wrapper avec gestion d'erreurs
async function safeAPICall(apiFunction, fallbackValue = null) {
  try {
    return await apiFunction();
  } catch (error) {
    console.error("API Error:", error);

    // Afficher une notification à l'utilisateur
    showNotification("error", "Erreur de connexion au serveur");

    return fallbackValue;
  }
}

// Utilisation
const traffic = await safeAPICall(() => api.get("/mobility/trafic"), {
  lignes: [],
});
```

## 🔄 Actualisation Automatique

```javascript
// Hook personnalisé pour auto-refresh
function useAutoRefresh(fetchFunction, interval = 30000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      const result = await fetchFunction();
      setData(result);
      setLoading(false);
    };

    fetch();
    const intervalId = setInterval(fetch, interval);

    return () => clearInterval(intervalId);
  }, [fetchFunction, interval]);

  return { data, loading };
}

// Utilisation
function LiveTraffic() {
  const { data: traffic, loading } = useAutoRefresh(
    () => api.get("/mobility/trafic"),
    30000 // Refresh toutes les 30 secondes
  );

  if (loading) return <div>Chargement...</div>;

  return <TrafficDisplay data={traffic} />;
}
```

---

## 🎯 Prochaines Étapes

1. ✅ Implémenter l'authentification JWT si nécessaire
2. ✅ Ajouter un state management (Redux, Zustand)
3. ✅ Implémenter le cache local pour améliorer les performances
4. ✅ Ajouter des WebSockets pour les notifications temps réel
5. ✅ Créer des tests unitaires avec Jest/Vitest

Bon développement ! 🚀
