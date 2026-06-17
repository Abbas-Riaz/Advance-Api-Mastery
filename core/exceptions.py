# core/exceptions.py

from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import (
    NotAuthenticated,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    ValidationError,
    MethodNotAllowed,
    Throttled,
)
from core.responses import ApiResponse


def custom_exception_handler(exc, context):

    # ── Step 1 ──────────────────────────────────────────
    # Let DRF do its own processing first.
    # This converts Django's Http404 → DRF's NotFound
    # and populates response.data and response.status_code
    # If response is None — totally unknown error → let Django handle as 500
    response = exception_handler(exc, context)
    if response is None:
        return None

    # ── Step 2 ──────────────────────────────────────────
    # Question 1: What TYPE of error is this?
    # Question 2: What MESSAGE should the client see?

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        message = "Login required or token is invalid."
        code = "AUTHENTICATION_ERROR"
        http_status = status.HTTP_401_UNAUTHORIZED

    elif isinstance(exc, PermissionDenied):
        message = "You do not have permission to do this."
        code = "PERMISSION_DENIED"
        http_status = status.HTTP_403_FORBIDDEN

    elif isinstance(exc, NotFound):
        message = "The resource you requested was not found."
        code = "NOT_FOUND"
        http_status = status.HTTP_404_NOT_FOUND

    elif isinstance(exc, ValidationError):
        message = "Invalid data. Please fix the errors below."
        code = "VALIDATION_ERROR"
        http_status = status.HTTP_400_BAD_REQUEST

    elif isinstance(exc, MethodNotAllowed):
        message = "This HTTP method is not allowed here."
        code = "METHOD_NOT_ALLOWED"
        http_status = status.HTTP_405_METHOD_NOT_ALLOWED

    elif isinstance(exc, Throttled):
        message = "Too many requests. Please slow down."
        code = "RATE_LIMITED"
        http_status = status.HTTP_429_TOO_MANY_REQUESTS

    else:
        message = str(exc.detail) if hasattr(exc, "detail") else "Something went wrong."
        code = exc.default_code if hasattr(exc, "default_code") else "SERVER_ERROR"
        http_status = response.status_code
    # ── Step 3 ──────────────────────────────────────────
    # Question 3: Are there FIELD-LEVEL errors?
    # Only ValidationError has these. Everything else → errors = None

    errors = None

    if isinstance(exc, ValidationError):
        if isinstance(response.data, dict):
            # {"name": ["required"], "price": ["must be > 0"]}
            errors = response.data
        elif isinstance(response.data, list):
            # ["passwords do not match"]  ← non-field error, wrap it
            errors = {"non_field_errors": response.data}

    # ── Step 4 ──────────────────────────────────────────
    # Return ONE consistent shape for every error, always

    return ApiResponse.error(
        message=message, errors=errors, code=code, status_code=http_status
    )
