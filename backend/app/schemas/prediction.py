"""Pydantic schemas for API request/response validation.

Defines all data models used by the FastAPI endpoints for
type checking, validation, and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    """Request schema for house price prediction.

    All property details needed to generate a price estimate.
    """

    location: str = Field(
        ...,
        description="Navi Mumbai location/node name (e.g., Kharghar, Panvel, Vashi)",
        examples=["Kharghar"],
    )
    area_sqft: float = Field(
        ...,
        gt=100,
        lt=10000,
        description="Carpet area in square feet (100-10000)",
        examples=[1000.0],
    )
    bhk: int = Field(
        ...,
        ge=1,
        le=6,
        description="Number of bedrooms (1-6)",
        examples=[2],
    )
    bathrooms: int = Field(
        ...,
        ge=1,
        le=6,
        description="Number of bathrooms (1-6)",
        examples=[2],
    )
    floor: int = Field(
        ...,
        ge=0,
        le=100,
        description="Floor number (0 for ground floor)",
        examples=[5],
    )
    total_floors: int = Field(
        ...,
        ge=1,
        le=80,
        description="Total number of floors in the building",
        examples=[20],
    )
    age_of_property: float = Field(
        ...,
        ge=0,
        le=50,
        description="Age of property in years",
        examples=[5.0],
    )
    parking: bool = Field(
        default=True,
        description="Whether parking is available",
    )
    lift: bool = Field(
        default=True,
        description="Whether lift is available",
    )

    @field_validator("location")
    @classmethod
    def normalize_location(cls, v: str) -> str:
        """Normalize location name."""
        return v.strip().title()


class PriceRange(BaseModel):
    """Predicted price range (low to high estimate)."""

    low: float = Field(..., description="Lower bound estimate in INR")
    high: float = Field(..., description="Upper bound estimate in INR")


class LocationContext(BaseModel):
    """Market context for the predicted location."""

    name: str
    avg_price: float = Field(..., description="Average property price in this location")
    median_price: float = Field(
        ..., description="Median property price in this location"
    )
    avg_price_per_sqft: float = Field(
        ..., description="Average price per square foot"
    )
    data_points: int = Field(
        ..., description="Number of data points used for this location"
    )


class InputSummary(BaseModel):
    """Echo of the input parameters for verification."""

    location: str
    area_sqft: float
    bhk: int
    bathrooms: int
    floor: int
    total_floors: int
    age_of_property: float
    parking: bool
    lift: bool


class PredictionResponse(BaseModel):
    """Response schema for house price prediction."""

    predicted_price: float = Field(
        ..., description="Estimated price in INR"
    )
    price_range: PriceRange = Field(
        ..., description="Confidence interval for the prediction"
    )
    price_per_sqft: float = Field(
        ..., description="Predicted price per square foot"
    )
    confidence_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Model confidence score (0-1)",
    )
    location_context: LocationContext = Field(
        ..., description="Market context for the location"
    )
    feature_importance: Dict[str, float] = Field(
        ..., description="Relative importance of each feature"
    )
    input_summary: InputSummary = Field(
        ..., description="Echo of input parameters"
    )


class LocationInfo(BaseModel):
    """Information about a single location."""

    name: str
    count: int = Field(..., description="Number of properties in dataset")
    avg_price: float
    median_price: float
    min_price: float
    max_price: float
    avg_price_per_sqft: float


class LocationsResponse(BaseModel):
    """Response schema for the locations endpoint."""

    locations: List[LocationInfo]
    total: int


class ModelInfo(BaseModel):
    """Model metadata and performance information."""

    model_type: str
    features: List[str]
    feature_importance: Dict[str, float]
    metrics: Dict[str, Any]
    locations_count: int
    locations: List[str]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    model_loaded: bool = Field(..., description="Whether the ML model is loaded")
    environment: str = Field(..., description="Current environment")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
