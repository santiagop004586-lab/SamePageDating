from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class PropertyBase(BaseModel):
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[Decimal] = None
    sqft: Optional[int] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None
    list_price: Optional[Decimal] = None
    photo_url: Optional[str] = None
    photos: Optional[List[str]] = None


class PropertyCreate(PropertyBase):
    external_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PropertyUpdate(BaseModel):
    list_price: Optional[Decimal] = None
    status: Optional[str] = None


class PropertyMetrics(BaseModel):
    arv: Optional[Decimal] = None
    estimated_rehab: Optional[Decimal] = None
    market_rent: Optional[Decimal] = None
    section8_rent: Optional[Decimal] = None
    total_project_cost: Optional[Decimal] = None
    monthly_cash_flow: Optional[Decimal] = None
    cap_rate: Optional[Decimal] = None
    cash_on_cash_return: Optional[Decimal] = None
    deal_spread: Optional[Decimal] = None


class PropertyInDB(PropertyBase):
    id: int
    external_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None
    
    # Calculated fields
    arv: Optional[Decimal] = None
    estimated_rehab: Optional[Decimal] = None
    market_rent: Optional[Decimal] = None
    section8_rent: Optional[Decimal] = None
    
    # Investment metrics
    total_project_cost: Optional[Decimal] = None
    monthly_cash_flow: Optional[Decimal] = None
    cap_rate: Optional[Decimal] = None
    cash_on_cash_return: Optional[Decimal] = None
    deal_spread: Optional[Decimal] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PropertyResponse(BaseModel):
    """Response model for property detail endpoint"""
    id: int
    address: str
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    
    bedrooms: Optional[int]
    bathrooms: Optional[Decimal]
    sqft: Optional[int]
    year_built: Optional[int]
    property_type: Optional[str]
    
    list_price: Optional[Decimal]
    list_date: Optional[date]
    status: Optional[str]
    photo_url: Optional[str]
    photos: Optional[List[str]]
    
    # Calculated fields
    arv: Optional[Decimal]
    estimated_rehab: Optional[Decimal]
    market_rent: Optional[Decimal]
    section8_rent: Optional[Decimal]
    
    # Investment metrics
    total_project_cost: Optional[Decimal]
    monthly_cash_flow: Optional[Decimal]
    cap_rate: Optional[Decimal]
    cash_on_cash_return: Optional[Decimal]
    deal_spread: Optional[Decimal]
    
    class Config:
        from_attributes = True


class InvestmentAssumptions(BaseModel):
    """User-customizable investment assumptions"""
    down_payment_pct: float = Field(default=0.20, ge=0, le=1)
    interest_rate: float = Field(default=0.07, ge=0, le=0.20)
    loan_term_years: int = Field(default=30, ge=1, le=30)
    closing_costs_pct: float = Field(default=0.03, ge=0, le=0.15, description="Non-refundable closing costs (lender fees, title, recording). Default: 3%.")
    closing_costs_fixed: Optional[float] = Field(default=None, ge=0, description="Fixed closing cost dollar amount (overrides pct if set)")
    escrow_pct: float = Field(default=0.03, ge=0, le=0.15, description="Escrow prepayments at closing (prepaid taxes/insurance). Refunded when you refi/sell. Default: 3%.")
    escrow_fixed: Optional[float] = Field(default=None, ge=0, description="Fixed escrow dollar amount (overrides pct if set)")
    property_tax_rate: float = Field(default=0.0267, ge=0, le=0.10)
    insurance_pct: float = Field(default=0.01, ge=0, le=0.05)
    insurance_fixed: Optional[float] = Field(default=None, ge=0, description="Fixed monthly insurance dollar amount (overrides pct if set)")
    maintenance_pct: float = Field(default=0.01, ge=0, le=0.05)
    maintenance_fixed: Optional[float] = Field(default=None, ge=0, description="Fixed monthly maintenance dollar amount (overrides pct if set)")
    property_mgmt_pct: float = Field(default=0.10, ge=0, le=0.20)
    property_mgmt_fixed: Optional[float] = Field(default=None, ge=0, description="Fixed monthly property management dollar amount (overrides pct if set)")
    vacancy_rate: float = Field(default=0.08, ge=0, le=0.30)
    vacancy_fixed: Optional[float] = Field(default=None, ge=0, description="Fixed monthly vacancy dollar amount (overrides pct if set)")
    capex_reserve_pct: float = Field(default=0.10, ge=0, le=0.20)
    reserves_amount: Optional[float] = Field(default=5000.0, ge=0, description="Upfront cash reserves held back at closing")
    down_payment_fixed: Optional[float] = Field(default=None, ge=0, description="Fixed down payment dollar amount (overrides pct if set)")
    rehab_cost: Optional[float] = Field(default=None, ge=0, description="Custom rehab cost override")
    arv_override: Optional[float] = Field(default=None, ge=0, description="Custom ARV override")
    gross_rent_override: Optional[float] = Field(default=None, ge=0, description="Post-renovation rent override (overrides Section 8 FMR rent for BRRRR cash flow)")
    pmi_rate: Optional[float] = Field(default=0.0, ge=0, le=0.05, description="PMI/MIP rate")
    purchase_price_override: Optional[float] = Field(default=None, ge=0, description="Custom purchase price override (model a negotiated price without changing listing price)")


class CalculateMetricsRequest(BaseModel):
    """Request to calculate metrics with custom assumptions"""
    property_id: int
    assumptions: Optional[InvestmentAssumptions] = None


class CalculateMetricsResponse(BaseModel):
    """Response with calculated metrics"""
    property_id: int
    metrics: PropertyMetrics
    assumptions: InvestmentAssumptions
