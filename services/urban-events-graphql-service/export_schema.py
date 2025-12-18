from graphql_schemas.queries import Query
from graphql_schemas.mutations import Mutation
import graphene

# Crée le schéma GraphQL
schema = graphene.Schema(query=Query, mutation=Mutation)

# Génère le SDL (Schema Definition Language)
sdl = str(schema)

# Écrit dans un fichier .graphql
with open("schema.graphql", "w") as f:
    f.write(sdl)

print("Schéma GraphQL exporté dans schema.graphql")
