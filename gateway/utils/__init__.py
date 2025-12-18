"""Utilitaires de l'API Gateway"""
from .logger import logger, log_request, log_error
from .error_handler import (
    ServiceError,
    service_error_handler,
    http_exception_handler,
    general_exception_handler,
    handle_rest_error,
    handle_grpc_error,
    handle_soap_error,
    handle_graphql_error
)

__all__ = [
    "logger",
    "log_request",
    "log_error",
    "ServiceError",
    "service_error_handler",
    "http_exception_handler",
    "general_exception_handler",
    "handle_rest_error",
    "handle_grpc_error",
    "handle_soap_error",
    "handle_graphql_error"
]