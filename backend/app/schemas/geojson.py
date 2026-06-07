from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class GeometryPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


class FeatureProperties(BaseModel):
    """Properties for a GeoJSON Feature"""
    id: int
    address: str
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    list_price: Optional[float]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    sqft: Optional[int]
    year_built: Optional[int]
    property_type: Optional[str]
    status: Optional[str]
    photo_url: Optional[str]
    photos: Optional[List[str]]
    unit_details: Optional[List[Dict[str, Any]]]
    arv: Optional[float]
    estimated_rehab: Optional[float]
    market_rent: Optional[float]
    section8_rent: Optional[float]
    property_tax_rate: Optional[float]
    estimates: Optional[Dict[str, Any]]
    total_project_cost: Optional[float]
    monthly_cash_flow: Optional[float]
    monthly_mortgage: Optional[float]
    expense_breakdown: Optional[Dict[str, float]]
    brrrr: Optional[Dict[str, Any]]
    appreciation: Optional[Dict[str, Any]]
    cap_rate: Optional[float]
    cash_on_cash_return: Optional[float]
    deal_spread: Optional[float]
    break_even_price: Optional[float]
    median_estimate: Optional[float]
    roi: Optional[float]
    breakeven_years: Optional[float]
    noi: Optional[float]
    marker_color: str


class Feature(BaseModel):
    """GeoJSON Feature"""
    type: str = "Feature"
    id: str
    geometry: GeometryPoint
    properties: FeatureProperties


class FeatureCollection(BaseModel):
    """GeoJSON FeatureCollection"""
    type: str = "FeatureCollection"
    features: List[Feature]
    total_count: int = 0


class BoundingBox(BaseModel):
    """Bounding box for map viewport"""
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class PropertyFilters(BaseModel):
    """Filters for property search"""
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    bedrooms_min: Optional[int] = None
    bedrooms_max: Optional[int] = None
    cash_flow_min: Optional[float] = None
    cap_rate_min: Optional[float] = None
    deal_spread_min: Optional[float] = None
