"""
Main application entry point for the FastAPI backend.
Initializes the app, middleware, and core routes.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.utils.helpers import format_response
from app.api.router import api_router

# Initialize logging based on settings
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Setup CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler to ensure JSON responses on unexpected errors.
    
    Args:
        request (Request): The incoming request.
        exc (Exception): The unhandled exception.
        
    Returns:
        JSONResponse: 500 error response.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=format_response("error", "Internal Server Error")
    )

@app.get("/health", summary="Health Check")
async def health_check() -> JSONResponse:
    """
    Health check endpoint to verify the server is running.
    
    Returns:
        JSONResponse: A simple status dictionary.
    """
    logger.info("Health check endpoint accessed.")
    return JSONResponse(
        status_code=200,
        content=format_response("success", "API is running locally and healthy.")
    )
