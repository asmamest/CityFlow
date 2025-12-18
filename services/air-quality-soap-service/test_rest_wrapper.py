"""
Script de test pour le wrapper REST FastAPI
Teste tous les endpoints et affiche les réponses JSON
"""
import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8002"
ZONES = ["CENTRE", "NORD", "SUD", "EST"]


def print_response(title: str, response: requests.Response):
    """Afficher une réponse de manière formatée"""
    print("\n" + "=" * 80)
    print(f"📍 {title}")
    print("=" * 80)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(response.text)
    else:
        print(f"❌ Erreur: {response.text}")


def test_root():
    """Test de la page d'accueil"""
    response = requests.get(f"{BASE_URL}/")
    print_response("GET / - Page d'accueil", response)


def test_get_aqi():
    """Test de l'endpoint GET /api/aqi/{zone}"""
    for zone in ZONES[:2]:  # Tester 2 zones
        response = requests.get(f"{BASE_URL}/api/aqi/{zone}")
        print_response(f"GET /api/aqi/{zone}", response)


def test_get_pollutants():
    """Test de l'endpoint GET /api/pollutants/{zone}"""
    zone = "SUD"
    response = requests.get(f"{BASE_URL}/api/pollutants/{zone}")
    print_response(f"GET /api/pollutants/{zone}", response)


def test_compare_zones():
    """Test de l'endpoint GET /api/compare/{zoneA}/{zoneB}"""
    zone_a, zone_b = "NORD", "SUD"
    response = requests.get(f"{BASE_URL}/api/compare/{zone_a}/{zone_b}")
    print_response(f"GET /api/compare/{zone_a}/{zone_b}", response)


def test_filter_pollutants():
    """Test de l'endpoint GET /api/filter/{zone}"""
    zone = "SUD"
    threshold = 35.0
    response = requests.get(f"{BASE_URL}/api/filter/{zone}?threshold={threshold}")
    print_response(f"GET /api/filter/{zone}?threshold={threshold}", response)


def test_history():
    """Test de l'endpoint GET /api/history/{zone}"""
    zone = "CENTRE"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    params = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'granularity': 'daily'
    }
    
    response = requests.get(f"{BASE_URL}/api/history/{zone}", params=params)
    print_response(f"GET /api/history/{zone} (7 derniers jours)", response)


def test_health():
    """Test de l'endpoint GET /api/health"""
    response = requests.get(f"{BASE_URL}/api/health")
    print_response("GET /api/health", response)


def test_list_zones():
    """Test de l'endpoint GET /api/zones"""
    response = requests.get(f"{BASE_URL}/api/zones")
    print_response("GET /api/zones", response)


def main():
    """Exécuter tous les tests"""
    print("\n" + "🧪" * 40)
    print("TESTS DU WRAPPER REST FASTAPI - SERVICE SOAP AIR QUALITY")
    print("🧪" * 40)
    
    try:
        # Test de connexion
        print("\n🔗 Test de connexion au serveur REST...")
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print(f"❌ Impossible de se connecter à {BASE_URL}")
            print("💡 Assurez-vous que le serveur REST est démarré (python soap_wrapper.py)")
            return
        print("✅ Connexion établie\n")
        
        # Exécuter les tests
        test_root()
        test_get_aqi()
        test_get_pollutants()
        test_compare_zones()
        test_filter_pollutants()
        test_history()
        test_health()
        test_list_zones()
        
        print("\n" + "=" * 80)
        print("✅ TOUS LES TESTS TERMINÉS")
        print("=" * 80)
        print(f"\n📖 Documentation Swagger: {BASE_URL}/docs")
        print(f"📖 Documentation ReDoc: {BASE_URL}/redoc")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Impossible de se connecter à {BASE_URL}")
        print("💡 Démarrez d'abord le serveur REST:")
        print("   python soap_wrapper.py")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


if __name__ == "__main__":
    main()