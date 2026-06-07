from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal


class ComparableSaleBase(BaseModel):
    address: str
    bedrooms: Optional[int]
    bathrooms: Optional[Decimal]
    sqft: Optional[int]
    sale_price: Optional[Decimal]
    sale_date: Optional[date]


class ComparableSaleResponse(ComparableSaleBase):
    id: int
    distance_miles: Optional[Decimal] = None
    adjusted_value: Optional[Decimal] = None
    adjustment_amount: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class CompsAnalysis(BaseModel):
    """Comparable sales analysis for a property"""
    property_id: int
    property_address: str
    comps: List[ComparableSaleResponse]
    estimated_arv: Optional[Decimal]


class MarketStats(BaseModel):
    """Market statistics for a ZIP code or area"""
    zip_code: str
    total_properties: int
    avg_price: Optional[Decimal]
    median_price: Optional[Decimal]
    avg_cap_rate: Optional[Decimal]
    avg_cash_flow: Optional[Decimal]
    avg_deal_spread: Optional[Decimal]


class HudFMRResponse(BaseModel):
    """HUD Fair Market Rent response"""
    zip_code: str
    year: int
    bedrooms: int
    fmr_amount: Decimal
    county_name: Optional[str]
    
    class Config:
        from_attributes = True
