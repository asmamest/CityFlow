"""Client GraphQL pour le service Événements Urbains"""
from gql import gql, Client as GqlClient
from gql.transport.aiohttp import AIOHTTPTransport
from typing import Dict, Any, List, Optional
from  config import settings
from  utils import logger, handle_graphql_error, ServiceError

class UrbanEventsGraphQLClient:
    """Client GraphQL pour interroger le service Événements Urbains"""
    
    def __init__(self):
        self.url = settings.URBAN_EVENTS_GRAPHQL_URL
        self.timeout = settings.GRAPHQL_TIMEOUT
        
        # Configuration du transport
        transport = AIOHTTPTransport(
            url=self.url,
            timeout=self.timeout
        )
        
        self.client = GqlClient(
            transport=transport,
            fetch_schema_from_transport=True
        )
        
        logger.info(f"GraphQL Client initialized: {self.url}")
    
    async def close(self):
        """Ferme le client GraphQL"""
        await self.client.close_async()
    
    async def _execute_query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Exécute une requête GraphQL"""
        try:
            async with self.client as session:
                result = await session.execute(gql(query), variable_values=variables)
                return result
        except Exception as e:
            logger.error(f"GraphQL Error: {str(e)}")
            raise handle_graphql_error(e, "urban-events-graphql")
    
    async def get_zones(self) -> List[Dict[str, Any]]:
        """Liste toutes les zones urbaines"""
        query = """
        query {
          zones {
            id
            name
            description
          }
        }
        """
        try:
            logger.info("GraphQL Query: zones")
            result = await self._execute_query(query)
            logger.info(f"GraphQL Response: {len(result.get('zones', []))} zones")
            return result.get("zones", [])
        except Exception as e:
            raise handle_graphql_error(e, "urban-events-graphql")
    
    async def get_zone(self, zone_id: str) -> Dict[str, Any]:
        """Récupère une zone par ID"""
        query = """
        query GetZone($zoneId: String!) {
          zone(zoneId: $zoneId) {
            id
            name
            description
          }
        }
        """
        try:
            logger.info(f"GraphQL Query: zone(id={zone_id})")
            result = await self._execute_query(query, {"zoneId": zone_id})
            logger.info(f"GraphQL Response: zone {zone_id}")
            return result.get("zone", {})
        except Exception as e:
            raise handle_graphql_error(e, "urban-events-graphql")
    
    async def get_event_types(self) -> List[Dict[str, Any]]:
        """Liste tous les types d'événements"""
        query = """
        query {
          eventTypes {
            id
            name
            description
          }
        }
        """
        try:
            logger.info("GraphQL Query: eventTypes")
            result = await self._execute_query(query)
            logger.info(f"GraphQL Response: {len(result.get('eventTypes', []))} types")
            return result.get("eventTypes", [])
        except Exception as e:
            raise handle_graphql_error(e, "urban-events-graphql")
    
    async def get_events(
        self,
        event_type_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Liste les événements avec filtres optionnels"""
        query = """
        query GetEvents(
          $eventTypeId: String,
          $zoneId: String,
          $status: String,
          $priority: String,
          $dateFrom: String,
          $dateTo: String
        ) {
          events(
            eventTypeId: $eventTypeId,
            zoneId: $zoneId,
            status: $status,
            priority: $priority,
            dateFrom: $dateFrom,
            dateTo: $dateTo
          ) {
            id
            name
            description
            eventTypeId
            zoneId
            date
            priority
            status
            createdAt
            updatedAt
            eventType {
              id
              name
              description
            }
            zone {
              id
              name
              description
            }
          }
        }
        """
        
        variables = {}
        if event_type_id:
            variables["eventTypeId"] = event_type_id
        if zone_id:
            variables["zoneId"] = zone_id
        if status:
            variables["status"] = status
        if priority:
            variables["priority"] = priority
        if date_from:
            variables["dateFrom"] = date_from
        if date_to:
            variables["dateTo"] = date_to
        
        try:
            logger.info(f"GraphQL Query: events with filters {variables}")
            result = await self._execute_query(query, variables)
            events = result.get("events", [])
            logger.info(f"GraphQL Response: {len(events)} events")
            return events
        except Exception as e:
            raise handle_graphql_error(e, "urban-events-graphql")
    
    async def get_event(self, event_id: str) -> Dict[str, Any]:
        """Récupère un événement par ID"""
        query = """
        query GetEvent($eventId: String!) {
          event(eventId: $eventId) {
            id
            name
            description
            eventTypeId
            zoneId
            date
            priority
            status
            createdAt
            updatedAt
            eventType {
              id
              name
              description
            }
            zone {
              id
              name
              description
            }
          }
        }
        """
        try:
            logger.info(f"GraphQL Query: event(id={event_id})")
            result = await self._execute_query(query, {"eventId": event_id})
            logger.info(f"GraphQL Response: event {event_id}")
            return result.get("event", {})
        except Exception as e:
            raise handle_graphql_error(e, "urban-events-graphql")
    
    async def create_event(
        self,
        name: str,
        description: str,
        event_type_id: str,
        zone_id: str,
        date: str,
        priority: str,
        status: str = "PENDING"
    ) -> Dict[str, Any]:
        """Crée un nouvel événement"""
        mutation = """
        mutation CreateEvent(
          $name: String!,
          $description: String!,
          $eventTypeId: String!,
          $zoneId: String!,
          $date: String!,
          $priority: String!,
          $status: String
        ) {
          createEvent(
            name: $name,
            description: $description,
            eventTypeId: $eventTypeId,
            zoneId: $zoneId,
            date: $date,
            priority: $priority,
            status: $status
          ) {
            success
            message
            event {
              id
              name
              description
              priority
              status
            }
          }
        }
        """
        
        variables = {
            "name": name,
            "description": description,
            "eventTypeId": event_type_id,
            "zoneId": zone_id,
            "date": date,
            "priority": priority,
            "status": status
        }
        
        try:
            logger.info(f"GraphQL Mutation: createEvent(name={name})")
            result = await self._execute_query(mutation, variables)
            logger.info("GraphQL Response: event created")
            return result.get("createEvent", {})
        except Exception as e:
            raise handle_graphql_error(e, "urban-events-graphql")
    
    async def update_event(
        self,
        event_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Met à jour un événement"""
        mutation = """
        mutation UpdateEvent(
          $eventId: String!,
          $name: String,
          $description: String,
          $eventTypeId: String,
          $zoneId: String,
          $date: String,
          $priority: String,
          $status: String
        ) {
          updateEvent(
            eventId: $eventId,
            name: $name,
            description: $description,
            eventTypeId: $eventTypeId,
            zoneId: $zoneId,
            date: $date,
            priority: $priority,
            status: $status
          ) {
            success
            message
            event {
              id
              name
              status
            }
          }
        }
        """
        
        variables = {"eventId": event_id, **kwargs}
        
        try:
            logger.info(f"GraphQL Mutation: updateEvent(id={event_id})")
            result = await self._execute_query(mutation, variables)
            logger.info(f"GraphQL Response: event {event_id} updated")
            return result.get("updateEvent", {})
        except Exception as e:
            raise handle_graphql_error(e, "urban-events-graphql")
    
    async def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Supprime un événement"""
        mutation = """
        mutation DeleteEvent($eventId: String!) {
          deleteEvent(eventId: $eventId) {
            success
            message
          }
        }
        """
        
        try:
            logger.info(f"GraphQL Mutation: deleteEvent(id={event_id})")
            result = await self._execute_query(mutation, {"eventId": event_id})
            logger.info(f"GraphQL Response: event {event_id} deleted")
            return result.get("deleteEvent", {})
        except Exception as e:
            raise handle_graphql_error(e, "urban-events-graphql")