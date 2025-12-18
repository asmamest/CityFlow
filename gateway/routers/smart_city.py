"""Router FastAPI pour le workflow métier Smart City - ORCHESTRATION COMPLÈTE"""
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from  clients import (
    MobilityRestClient,
    AirQualitySoapClient,
    EmergencyGrpcClient,
    UrbanEventsGraphQLClient
)
from  models.smart_city import (
    PlanTripRequest, PlanTripResponse, TripAnalysis,
    AirQualityInfo, TransportInfo, AlertInfo, EventInfo,
    RouteRecommendation, HealthCheckResponse
)
from  utils import logger

router = APIRouter(prefix="/smart-city", tags=["Smart City Workflow"])

# Dependencies pour tous les clients
async def get_all_clients():
    """Initialise tous les clients nécessaires au workflow"""
    mobility = MobilityRestClient()
    air_quality = AirQualitySoapClient()
    emergency = EmergencyGrpcClient()
    urban_events = UrbanEventsGraphQLClient()
    
    try:
        yield {
            "mobility": mobility,
            "air_quality": air_quality,
            "emergency": emergency,
            "urban_events": urban_events
        }
    finally:
        await mobility.close()
        await emergency.close()
        await urban_events.close()

@router.get("/", summary="Page d'accueil Smart City")
async def smart_city_home():
    """Informations sur les workflows Smart City"""
    return {
        "service": "Smart City Orchestration",
        "version": "1.0.0",
        "description": "Orchestration intelligente de tous les services de la ville",
        "workflows": [
            {
                "endpoint": "/smart-city/plan-trip",
                "method": "POST",
                "description": "Planification intelligente de trajet avec analyse multi-services"
            },
            {
                "endpoint": "/smart-city/health",
                "method": "GET",
                "description": "Health check de tous les microservices"
            }
        ]
    }

@router.post(
    "/plan-trip",
    response_model=PlanTripResponse,
    summary="🚀 Planifier un trajet intelligent"
)
async def plan_trip(
    request: PlanTripRequest,
    clients: Dict[str, Any] = Depends(get_all_clients)
):
    """
    ## 🏙️ WORKFLOW MÉTIER COMPLET - PLANIFICATION INTELLIGENTE DE TRAJET
    
    Ce endpoint orchestre TOUS les microservices pour fournir une analyse complète:
    
    ### 📊 Données collectées:
    1. **Qualité de l'Air** (SOAP): AQI des zones de départ et d'arrivée
    2. **Mobilité** (REST): État du trafic et disponibilité des transports
    3. **Urgences** (gRPC): Alertes actives dans les zones concernées
    4. **Événements Urbains** (GraphQL): Événements impactant la mobilité
    
    ### 🎯 Intelligence:
    - Recommandations d'itinéraires selon la qualité de l'air
    - Alertes sur les perturbations du trafic
    - Suggestions d'alternatives en cas de problème
    - Analyse du niveau de confort du trajet
    
    ### Exemple de requête:
    ```json
    {
      "zone_depart": "downtown",
      "zone_arrivee": "industrial",
      "heure_depart": "14:30",
      "preferences": ["metro", "bus"]
    }
    ```
    """
    start_time = time.time()
    logger.info(f"🚀 Starting trip planning: {request.zone_depart} → {request.zone_arrivee}")
    
    warnings = []
    
    try:
        # ============================================================
        # ÉTAPE 1: COLLECTE PARALLÈLE DES DONNÉES DES 4 MICROSERVICES
        # ============================================================
        
        logger.info("📡 Step 1/5: Collecting data from all microservices...")
        
        # 1.1 - Qualité de l'air (SOAP)
        try:
            air_depart = await clients["air_quality"].get_aqi(request.zone_depart)
            air_arrivee = await clients["air_quality"].get_aqi(request.zone_arrivee)
        except Exception as e:
            logger.error(f"Air quality service error: {str(e)}")
            warnings.append("⚠️ Données de qualité de l'air indisponibles")
            air_depart = {"zone": request.zone_depart, "aqi": 0, "category": "Unknown", "description": "N/A", "timestamp": datetime.now().isoformat()}
            air_arrivee = {"zone": request.zone_arrivee, "aqi": 0, "category": "Unknown", "description": "N/A", "timestamp": datetime.now().isoformat()}
        
        # 1.2 - Mobilité (REST)
        try:
            trafic_data = await clients["mobility"].get_trafic()
            disponibilite_data = await clients["mobility"].get_disponibilite()
        except Exception as e:
            logger.error(f"Mobility service error: {str(e)}")
            warnings.append("⚠️ Données de mobilité indisponibles")
            trafic_data = {"lignes": []}
            disponibilite_data = {"vehicules": []}
        
        # 1.3 - Alertes d'urgence (gRPC)
        try:
            alertes_depart = await clients["emergency"].get_active_alerts(request.zone_depart)
            alertes_arrivee = await clients["emergency"].get_active_alerts(request.zone_arrivee)
            all_alerts = alertes_depart + alertes_arrivee
        except Exception as e:
            logger.error(f"Emergency service error: {str(e)}")
            warnings.append("⚠️ Données d'urgence indisponibles")
            all_alerts = []
        
        # 1.4 - Événements urbains (GraphQL)
        try:
            events_depart = await clients["urban_events"].get_events(zone_id=request.zone_depart, status="IN_PROGRESS")
            events_arrivee = await clients["urban_events"].get_events(zone_id=request.zone_arrivee, status="IN_PROGRESS")
            all_events = events_depart + events_arrivee
        except Exception as e:
            logger.error(f"Urban events service error: {str(e)}")
            warnings.append("⚠️ Données d'événements indisponibles")
            all_events = []
        
        # ============================================================
        # ÉTAPE 2: ANALYSE DE LA QUALITÉ DE L'AIR
        # ============================================================
        
        logger.info("🌫️ Step 2/5: Analyzing air quality...")
        
        def get_air_recommendation(aqi: int) -> str:
            if aqi <= 50:
                return "✅ Qualité excellente - Tous modes de transport recommandés"
            elif aqi <= 100:
                return "✅ Qualité acceptable - Privilégiez les transports fermés"
            elif aqi <= 150:
                return "⚠️ Qualité médiocre - Évitez les modes de transport ouverts"
            elif aqi <= 200:
                return "⚠️ Mauvaise qualité - Privilégiez fortement les transports fermés"
            else:
                return "🚨 Qualité très mauvaise - Limitez vos déplacements"
        
        air_quality_depart = AirQualityInfo(
            zone=air_depart["zone"],
            aqi=air_depart["aqi"],
            category=air_depart["category"],
            description=air_depart["description"],
            timestamp=air_depart["timestamp"],
            recommendation=get_air_recommendation(air_depart["aqi"])
        )
        
        air_quality_arrivee = AirQualityInfo(
            zone=air_arrivee["zone"],
            aqi=air_arrivee["aqi"],
            category=air_arrivee["category"],
            description=air_arrivee["description"],
            timestamp=air_arrivee["timestamp"],
            recommendation=get_air_recommendation(air_arrivee["aqi"])
        )
        
        # Comparaison
        diff_aqi = abs(air_depart["aqi"] - air_arrivee["aqi"])
        if air_depart["aqi"] < air_arrivee["aqi"]:
            comparison = f"⚠️ Attention: La qualité de l'air se dégrade vers {request.zone_arrivee} (différence: {diff_aqi} points AQI)"
        elif air_depart["aqi"] > air_arrivee["aqi"]:
            comparison = f"✅ Bonne nouvelle: La qualité de l'air s'améliore vers {request.zone_arrivee} (différence: {diff_aqi} points AQI)"
        else:
            comparison = f"➡️ La qualité de l'air est similaire dans les deux zones"
        
        # ============================================================
        # ÉTAPE 3: ANALYSE DES TRANSPORTS DISPONIBLES
        # ============================================================
        
        logger.info("🚆 Step 3/5: Analyzing available transportation...")
        
        transports_disponibles = []
        
        for ligne in trafic_data.get("lignes", []):
            # Vérifier si ce type de transport est dans les préférences
            if ligne.get("ligne") and any(pref in ligne.get("ligne", "").lower() for pref in request.preferences):
                # Trouver la disponibilité correspondante
                dispo = "Inconnue"
                for vehicule in disponibilite_data.get("vehicules", []):
                    if vehicule.get("type_transport") in ligne.get("ligne", "").lower():
                        dispo = f"{vehicule.get('taux_disponibilite', 0)}%"
                        break
                
                transports_disponibles.append(TransportInfo(
                    ligne=ligne.get("ligne", "N/A"),
                    type_transport=ligne.get("ligne", "N/A").split()[0],
                    etat_trafic=ligne.get("etat", "unknown"),
                    disponibilite=dispo,
                    horaires_prochain_passage=[request.heure_depart, "14:45", "15:00"]
                ))
        
        # ============================================================
        # ÉTAPE 4: ANALYSE DES ALERTES ET ÉVÉNEMENTS
        # ============================================================
        
        logger.info("🚨 Step 4/5: Analyzing alerts and events...")
        
        # Alertes d'urgence
        alertes_actives = []
        niveau_alerte = "LOW"
        
        for alert in all_alerts:
            alertes_actives.append(AlertInfo(
                alert_id=alert["alert_id"],
                type=alert["type"],
                description=alert["description"],
                priority=alert["priority"],
                zone=alert["location"]["zone"],
                created_at=alert["created_at"]
            ))
            
            if alert["priority"] == "CRITICAL":
                niveau_alerte = "CRITICAL"
            elif alert["priority"] == "HIGH" and niveau_alerte != "CRITICAL":
                niveau_alerte = "HIGH"
            elif alert["priority"] == "MEDIUM" and niveau_alerte == "LOW":
                niveau_alerte = "MEDIUM"
        
        # Événements urbains
        evenements_impactants = []
        for event in all_events:
            evenements_impactants.append(EventInfo(
                event_id=event["id"],
                name=event["name"],
                description=event["description"],
                priority=event["priority"],
                status=event["status"],
                zone=event.get("zone", {}).get("name", "N/A") if event.get("zone") else "N/A",
                date=event["date"]
            ))
        
        # ============================================================
        # ÉTAPE 5: GÉNÉRATION DES RECOMMANDATIONS INTELLIGENTES
        # ============================================================
        
        logger.info("🎯 Step 5/5: Generating intelligent recommendations...")
        
        # Recommandation principale
        principale_raison = []
        
        # Facteur 1: Qualité de l'air
        if air_depart["aqi"] > 150 or air_arrivee["aqi"] > 150:
            principale_raison.append("pollution élevée")
        
        # Facteur 2: Alertes critiques
        if niveau_alerte in ["CRITICAL", "HIGH"]:
            principale_raison.append(f"alertes {niveau_alerte.lower()}")
        
        # Facteur 3: Trafic perturbé
        trafic_perturbe = any(t.etat_trafic in ["perturbé", "interrompu"] for t in transports_disponibles)
        if trafic_perturbe:
            principale_raison.append("trafic perturbé")
        
        # Construire la recommandation
        if principale_raison:
            recommandation_type = "alternatif"
            recommandation_desc = f"Itinéraire alternatif recommandé en raison de: {', '.join(principale_raison)}"
            lignes_suggerees = [t.ligne for t in transports_disponibles if t.etat_trafic == "normal"][:2]
        else:
            recommandation_type = "direct"
            recommandation_desc = "Itinéraire direct recommandé - Conditions favorables"
            lignes_suggerees = [t.ligne for t in transports_disponibles][:2]
        
        if not lignes_suggerees:
            lignes_suggerees = ["Marche à pied recommandée", "Vélo en libre-service"]
        
        recommandation_principale = RouteRecommendation(
            type=recommandation_type,
            description=recommandation_desc,
            raison=", ".join(principale_raison) if principale_raison else "Aucun problème détecté",
            lignes_suggerees=lignes_suggerees,
            duree_estimee="25-30 minutes"
        )
        
        # Recommandations alternatives
        alternatives = [
            RouteRecommendation(
                type="eco-friendly",
                description="Trajet écologique via zones à faible pollution",
                raison="Minimise l'exposition à la pollution",
                lignes_suggerees=["Métro express", "Tramway vert"],
                duree_estimee="35-40 minutes"
            ),
            RouteRecommendation(
                type="rapide",
                description="Trajet le plus rapide sans tenir compte de la qualité de l'air",
                raison="Optimise le temps de trajet",
                lignes_suggerees=["Bus express", "Métro direct"],
                duree_estimee="20-25 minutes"
            )
        ]
        
        # Niveau de confort global
        confort_score = 100
        confort_score -= (air_depart["aqi"] + air_arrivee["aqi"]) / 10
        confort_score -= len(alertes_actives) * 10
        confort_score -= len(evenements_impactants) * 5
        
        if confort_score >= 80:
            niveau_confort = "excellent"
        elif confort_score >= 60:
            niveau_confort = "bon"
        elif confort_score >= 40:
            niveau_confort = "moyen"
        else:
            niveau_confort = "difficile"
        
        # Conseil principal
        if niveau_confort in ["excellent", "bon"]:
            conseil = f"✅ Conditions favorables pour votre trajet. Bon voyage!"
        elif niveau_confort == "moyen":
            conseil = f"⚠️ Conditions acceptables mais soyez vigilant aux perturbations."
        else:
            conseil = f"🚨 Conditions difficiles. Envisagez de reporter votre déplacement si possible."
        
        # ============================================================
        # CONSTRUCTION DE LA RÉPONSE FINALE
        # ============================================================
        
        analysis = TripAnalysis(
            zone_depart=request.zone_depart,
            zone_arrivee=request.zone_arrivee,
            heure_demandee=request.heure_depart,
            air_quality_depart=air_quality_depart,
            air_quality_arrivee=air_quality_arrivee,
            air_quality_comparison=comparison,
            transports_disponibles=transports_disponibles,
            alertes_actives=alertes_actives,
            niveau_alerte_global=niveau_alerte,
            evenements_impactants=evenements_impactants,
            recommandation_principale=recommandation_principale,
            recommandations_alternatives=alternatives,
            conseil_principal=conseil,
            niveau_confort=niveau_confort,
            timestamp=datetime.now().isoformat()
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Trip planning completed in {processing_time:.2f}ms")
        
        return PlanTripResponse(
            success=True,
            message="Analyse complète du trajet générée avec succès",
            analysis=analysis,
            warnings=warnings,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Error in trip planning: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la planification du trajet: {str(e)}"
        )

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check de tous les services"
)
async def health_check(clients: Dict[str, Any] = Depends(get_all_clients)):
    """
    Vérifie l'état de santé de tous les microservices.
    
    Retourne le statut de:
    - Service Mobilité (REST)
    - Service Qualité de l'Air (SOAP)
    - Service Urgences (gRPC)
    - Service Événements Urbains (GraphQL)
    """
    logger.info("Performing health check on all services...")
    
    services_status = {}
    
    # Check Mobility (REST)
    try:
        services_status["mobility"] = await clients["mobility"].health_check()
    except:
        services_status["mobility"] = False
    
    # Check Air Quality (SOAP)
    try:
        services_status["air_quality"] = await clients["air_quality"].health_check()
    except:
        services_status["air_quality"] = False
    
    # Check Emergency (gRPC)
    try:
        services_status["emergency"] = await clients["emergency"].health_check()
    except:
        services_status["emergency"] = False
    
    # Check Urban Events (GraphQL) - pas de health check natif, on teste une requête
    try:
        await clients["urban_events"].get_zones()
        services_status["urban_events"] = True
    except:
        services_status["urban_events"] = False
    
    # Statut global
    all_healthy = all(services_status.values())
    status = "healthy" if all_healthy else "degraded"
    
    return HealthCheckResponse(
        status=status,
        services=services_status,
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )