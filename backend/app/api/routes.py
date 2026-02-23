"""API routes for house price prediction endpoints.

Provides RESTful endpoints for:
- Price prediction
- Location listing
- Model information
- Health checks
"""

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.core.logging import logger
from app.ml.predictor import engine
from app.schemas.prediction import (
    ErrorResponse,
    HealthResponse,
    LocationsResponse,
    ModelInfo,
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter()
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint",
)
async def health_check() -> HealthResponse:
    """Check the health status of the API and ML model."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        model_loaded=engine.is_loaded(),
        environment=settings.app_env,
    )


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Prediction error"},
    },
    tags=["Prediction"],
    summary="Predict house price",
    description="Generate a price prediction for a property in Navi Mumbai "
    "based on location, area, BHK, and other features.",
)
async def predict_price(request: PredictionRequest) -> PredictionResponse:
    """Generate a house price prediction.

    Accepts property details and returns an estimated price with
    confidence interval and market context.
    """
    if not engine.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model is not loaded. Please try again later.",
        )

    try:
        result = engine.predict(
            location=request.location,
            area_sqft=request.area_sqft,
            bhk=request.bhk,
            bathrooms=request.bathrooms,
            floor=request.floor,
            total_floors=request.total_floors,
            age_of_property=request.age_of_property,
            parking=int(request.parking),
            lift=int(request.lift),
        )
        return PredictionResponse(**result)

    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the prediction.",
        )


@router.get(
    "/locations",
    response_model=LocationsResponse,
    tags=["Data"],
    summary="List all available locations",
    description="Returns all Navi Mumbai locations with price statistics.",
)
async def get_locations() -> LocationsResponse:
    """Return all valid locations with their price statistics."""
    if not engine.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model is not loaded.",
        )

    locations = engine.get_locations()
    return LocationsResponse(locations=locations, total=len(locations))


@router.get(
    "/model-info",
    response_model=ModelInfo,
    tags=["System"],
    summary="Get model information",
    description="Returns metadata about the trained ML model, "
    "including features, metrics, and supported locations.",
)
async def get_model_info() -> ModelInfo:
    """Return model metadata and performance metrics."""
    if not engine.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model is not loaded.",
        )

    info = engine.get_model_info()
    return ModelInfo(**info)
