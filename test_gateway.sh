#!/bin/bash

# ============================================================
# SCRIPT DE TEST COMPLET - SMART CITY API GATEWAY
# ============================================================

echo "🧪 Starting Smart City API Gateway Tests..."
echo "==========================================="

GATEWAY_URL="http://localhost:8080"
SUCCESS_COUNT=0
FAIL_COUNT=0

# Fonction pour tester un endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo ""
    echo "🔍 Testing: $name"
    echo "   Method: $method"
    echo "   Endpoint: $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$GATEWAY_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo "   ✅ Success (HTTP $http_code)"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "   ❌ Failed (HTTP $http_code)"
        echo "   Response: $body"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# ============================================================
# TESTS DE BASE
# ============================================================

echo ""
echo "📋 Section 1: Base Endpoints"
echo "----------------------------"

test_endpoint "Gateway Home" "GET" "/"
test_endpoint "Gateway Health" "GET" "/health"
test_endpoint "Gateway Info" "GET" "/info"

# ============================================================
# TESTS MOBILITÉ (REST)
# ============================================================

echo ""
echo "🚗 Section 2: Mobility Service (REST)"
echo "-------------------------------------"

test_endpoint "Mobility Home" "GET" "/mobility/"
test_endpoint "Get Trafic" "GET" "/mobility/trafic"
test_endpoint "Get Disponibilite" "GET" "/mobility/disponibilite"
test_endpoint "List Lignes" "GET" "/mobility/lignes"

# ============================================================
# TESTS QUALITÉ DE L'AIR (SOAP)
# ============================================================
echo ""
echo "🌫️ Section 3: Air Quality Service (SOAP)"
echo "----------------------------------------"

python3 - <<EOF
from zeep import Client, Settings
from zeep.transports import Transport
import requests
import sys

wsdl_url = "http://air-quality-soap-service:8000/?wsdl"

try:
    session = requests.Session()
    transport = Transport(session=session)
    client = Client(wsdl=wsdl_url, transport=transport, settings=Settings(strict=False))
    
    service = client.bind('AirQualitySOAPService', 'Application')
    
    # HealthCheck
    response = service.HealthCheck()
    print("🔍 Air Quality HealthCheck Response:", response)
    
except Exception as e:
    print("❌ SOAP Test Failed:", e)
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi


# ============================================================
# TESTS URGENCES (gRPC)
# ============================================================

echo ""
echo "🚨 Section 4: Emergency Service (gRPC)"
echo "--------------------------------------"

test_endpoint "Emergency Home" "GET" "/emergency/"
test_endpoint "Get Active Alerts" "GET" "/emergency/alerts/active/downtown"

# Test création d'alerte
test_endpoint "Create Alert" "POST" "/emergency/alerts" '{
    "type": "FIRE",
    "description": "Test fire alert from automated testing",
    "location": {
        "latitude": 36.8065,
        "longitude": 10.1815,
        "address": "123 Test Street",
        "city": "Tunis",
        "zone": "downtown"
    },
    "priority": "HIGH",
    "reporter_name": "Test User",
    "reporter_phone": "+21612345678",
    "affected_people": 5
}'

# ============================================================
# TESTS ÉVÉNEMENTS URBAINS (GraphQL)
# ============================================================

echo ""
echo "📅 Section 5: Urban Events Service (GraphQL)"
echo "-------------------------------------------"

test_endpoint "Urban Events Home" "GET" "/urban/"
test_endpoint "Get Zones" "GET" "/urban/zones"
test_endpoint "Get Event Types" "GET" "/urban/event-types"
test_endpoint "Get Events" "GET" "/urban/events"

# ============================================================
# TESTS WORKFLOW SMART CITY
# ============================================================

echo ""
echo "🚀 Section 6: Smart City Workflow"
echo "---------------------------------"

test_endpoint "Smart City Home" "GET" "/smart-city/"
test_endpoint "Full Health Check" "GET" "/smart-city/health"

# Test du workflow complet de planification de trajet
test_endpoint "Plan Trip Workflow" "POST" "/smart-city/plan-trip" '{
    "zone_depart": "downtown",
    "zone_arrivee": "industrial",
    "heure_depart": "14:30",
    "preferences": ["metro", "bus"]
}'

# ============================================================
# RÉSUMÉ DES TESTS
# ============================================================

echo ""
echo "==========================================="
echo "📊 Test Summary"
echo "==========================================="
echo "✅ Successful tests: $SUCCESS_COUNT"
echo "❌ Failed tests: $FAIL_COUNT"
echo ""

TOTAL=$((SUCCESS_COUNT + FAIL_COUNT))
if [ $TOTAL -gt 0 ]; then
    SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($SUCCESS_COUNT/$TOTAL)*100}")
    echo "📈 Success rate: $SUCCESS_RATE%"
fi

echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️ Some tests failed. Please check the output above."
    exit 1
fi