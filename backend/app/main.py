"""Main FastAPI application entry point.

Configures the FastAPI app with CORS, routing, startup/shutdown
events, and model loading.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import logger
from app.ml.predictor import engine


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events.

    On startup: Load the ML model into memory.
    On shutdown: Clean up resources.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")

    try:
        engine.load_model(settings.model_path)
        logger.info("ML model loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"Failed to load model: {e}")
        logger.warning(
            "Server starting without ML model. "
            "Run 'python -m app.ml.train' to train the model."
        )
    except Exception as e:
        logger.error(f"Unexpected error loading model: {e}", exc_info=True)

    yield

    # Shutdown
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title=settings.app_name,
        description=(
            "AI-powered residential property price prediction API for "
            "Navi Mumbai. Provides instant price estimates using a trained "
            "Gradient Boosting model across 10+ locations in Navi Mumbai."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(router, prefix="/api/v1")

    # Root endpoint
    @app.get("/", tags=["System"])
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "api_prefix": "/api/v1",
        }

    return app


app = create_app()
