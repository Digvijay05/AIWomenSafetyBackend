# app/core/exception_handler.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from typing import Dict, Any

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom exception handler that returns JSON envelope format
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "INTERNAL_ERROR"
    error_message = "An internal error occurred"
    
    if hasattr(exc, "status_code"):
        status_code = exc.status_code
    if hasattr(exc, "detail"):
        error_message = str(exc.detail)
        # Extract error code if provided in detail dict format
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            error_code = exc.detail.get("code", "UNKNOWN_ERROR")
            error_message = exc.detail.get("message", error_message)
    
    # Map common status codes to error codes
    if status_code == 401:
        error_code = "UNAUTHORIZED"
    elif status_code == 403:
        error_code = "FORBIDDEN"
    elif status_code == 404:
        error_code = "NOT_FOUND"
    elif status_code == 400:
        error_code = "BAD_REQUEST"
    elif status_code == 422:
        error_code = "VALIDATION_ERROR"
    elif status_code == 500:
        error_code = "INTERNAL_ERROR"
    elif status_code == 503:
        error_code = "SERVICE_UNAVAILABLE"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": error_code,
                "message": error_message
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Custom validation exception handler that returns JSON envelope format
    """
    errors = exc.errors()
    error_messages = [f"{'.'.join(err.get('loc', []))}: {err.get('msg', '')}" for err in errors]
    error_message = "; ".join(error_messages)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": f"Validation error: {error_message}"
            }
        }
    )