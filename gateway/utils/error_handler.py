"""Gestionnaire d'erreurs centralisé"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Union
import httpx
import grpc
from  utils.logger import log_error

class ServiceError(Exception):
    """Exception personnalisée pour les erreurs de service"""
    def __init__(self, service: str, message: str, status_code: int = 500):
        self.service = service
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

async def service_error_handler(request: Request, exc: ServiceError):
    """Handler pour ServiceError"""
    log_error(exc.service, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "service": exc.service,
            "message": exc.message,
            "path": str(request.url)
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler pour HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "path": str(request.url)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handler pour toutes les autres exceptions"""
    log_error("gateway", exc, {"path": str(request.url)})
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Erreur interne du serveur",
            "detail": str(exc) if hasattr(exc, '__str__') else "Unknown error",
            "path": str(request.url)
        }
    )

def handle_rest_error(error: Exception, service: str) -> ServiceError:
    """Transforme une erreur REST en ServiceError"""
    if isinstance(error, httpx.TimeoutException):
        return ServiceError(
            service=service,
            message=f"Timeout lors de la connexion à {service}",
            status_code=504
        )
    elif isinstance(error, httpx.ConnectError):
        return ServiceError(
            service=service,
            message=f"Impossible de se connecter à {service}",
            status_code=503
        )
    elif isinstance(error, httpx.HTTPStatusError):
        return ServiceError(
            service=service,
            message=f"Erreur HTTP {error.response.status_code}: {error.response.text}",
            status_code=error.response.status_code
        )
    else:
        return ServiceError(
            service=service,
            message=f"Erreur lors de l'appel à {service}: {str(error)}",
            status_code=500
        )

def handle_grpc_error(error: grpc.RpcError, service: str) -> ServiceError:
    """Transforme une erreur gRPC en ServiceError"""
    status_code_map = {
        grpc.StatusCode.UNAVAILABLE: 503,
        grpc.StatusCode.DEADLINE_EXCEEDED: 504,
        grpc.StatusCode.NOT_FOUND: 404,
        grpc.StatusCode.INVALID_ARGUMENT: 400,
        grpc.StatusCode.PERMISSION_DENIED: 403,
        grpc.StatusCode.UNAUTHENTICATED: 401,
    }
    
    status_code = status_code_map.get(error.code(), 500)
    
    return ServiceError(
        service=service,
        message=f"Erreur gRPC: {error.details()}",
        status_code=status_code
    )

def handle_soap_error(error: Exception, service: str) -> ServiceError:
    """Transforme une erreur SOAP en ServiceError"""
    return ServiceError(
        service=service,
        message=f"Erreur SOAP: {str(error)}",
        status_code=500
    )

def handle_graphql_error(error: Exception, service: str) -> ServiceError:
    """Transforme une erreur GraphQL en ServiceError"""
    return ServiceError(
        service=service,
        message=f"Erreur GraphQL: {str(error)}",
        status_code=500
    )