#!/bin/bash
# Script d'attente pour PostgreSQL
# Usage: ./wait-for-postgres.sh <host> <command>

set -e

host="$1"
shift
cmd="$@"

# Extraire les informations de connexion depuis DATABASE_URL
# Format: postgresql://user:pass@host:port/db
if [ ! -z "$DATABASE_URL" ]; then
    # Extraire host et port depuis DATABASE_URL
    db_host=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    db_port=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    db_user=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    
    # Utiliser les valeurs extraites ou les valeurs par défaut
    host=${db_host:-$host}
    port=${db_port:-5432}
    user=${db_user:-postgres}
else
    # Valeurs par défaut si DATABASE_URL n'est pas définie
    host=${host:-postgres}
    port=5432
    user=postgres
fi

echo "⏳ Attente de PostgreSQL sur $host:$port..."
echo "👤 Utilisateur: $user"

# Attendre que PostgreSQL soit prêt (max 60 secondes)
timeout=60
counter=0

until pg_isready -h "$host" -p "$port" -U "$user" -q; do
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        echo "❌ ERREUR: PostgreSQL n'est pas accessible après ${timeout}s"
        echo "❌ Vérifiez que le conteneur PostgreSQL est démarré"
        exit 1
    fi
    echo "⏳ Tentative $counter/$timeout - PostgreSQL n'est pas encore prêt..."
    sleep 1
done

echo "✅ PostgreSQL est prêt sur $host:$port!"
echo "🚀 Démarrage de l'application..."
echo ""

# Exécuter la commande
exec $cmd