"""Clients pour les différents microservices"""
from .rest_client import MobilityRestClient
from .soap_client import AirQualitySoapClient
from .grpc_client import EmergencyGrpcClient
from .graphql_client import UrbanEventsGraphQLClient

__all__ = [
    "MobilityRestClient",
    "AirQualitySoapClient",
    "EmergencyGrpcClient",
    "UrbanEventsGraphQLClient"
]