"""
VERITAS - Core Exceptions and Error Handlers
Standardized error models matching the API Contract:
{
  "error": {
    "code": "ENTITY_NOT_FOUND",
    "message": "Requested entity with ID 'P999' does not exist."
  }
}
"""
import logging
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
import sentry_sdk

logger = logging.getLogger("veritas.exceptions")


class VeritasAPIException(Exception):
    """Base exception for all domain-specific VERITAS API errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(VeritasAPIException):
    """Raised when a requested entity cannot be found in the knowledge graph."""

    def __init__(self, entity_id: str):
        super().__init__(
            code="ENTITY_NOT_FOUND",
            message=f"Requested entity with ID '{entity_id}' does not exist.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class PathNotFoundException(VeritasAPIException):
    """Raised when no connecting path exists between source and target entities."""

    def __init__(self, source_id: str, target_id: str):
        super().__init__(
            code="PATH_NOT_FOUND",
            message=f"No connecting path found between source '{source_id}' and target '{target_id}'.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidAlgorithmMetricException(VeritasAPIException):
    """Raised when an unsupported centrality metric is requested."""

    def __init__(self, metric: str, supported: list[str]):
        super().__init__(
            code="INVALID_METRIC",
            message=f"Unsupported centrality metric '{metric}'. Supported metrics: {', '.join(supported)}.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DatabaseConnectionException(VeritasAPIException):
    """Raised when a critical graph database error occurs."""

    def __init__(self, message: str = "Graph database service is currently unavailable."):
        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


async def veritas_exception_handler(request: Request, exc: VeritasAPIException) -> JSONResponse:
    """Format domain exceptions according to API Contract."""
    logger.warning(f"Domain exception {exc.code} on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Capture unhandled 500 errors in Sentry and return standardized error format."""
    logger.exception(f"Unhandled error processing {request.method} {request.url.path}: {exc}")
    sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
            }
        },
    )
