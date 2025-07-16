"""
Pydantic schemas for Pricing-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

class PriceBase(BaseModel):
    """Base price schema"""
    price_type: str = Field(..., description="Price type: COST, SALE, MARGIN")
    price: Decimal = Field(..., ge=0, description="Price value")
    effective_date: datetime = Field(..., description="Effective date")
    expiration_date: Optional[datetime] = Field(None, description="Expiration date")
    market_factor: Optional[str] = Field(None, description="Market factor affecting price")
    approved_by: Optional[int] = Field(None, description="User ID who approved")
    is_active: bool = Field(True, description="Active status")

    @validator('price_type')
    def validate_price_type(cls, v):
        allowed_types = ['COST', 'SALE', 'MARGIN']
        if v not in allowed_types:
            raise ValueError(f'Price type must be one of: {allowed_types}')
        return v

class PriceCreate(PriceBase):
    """Schema for creating prices"""
    product_id: int = Field(..., description="Product ID")

class PriceUpdate(BaseModel):
    """Schema for updating prices"""
    price_type: str = Field(..., description="Price type: COST, SALE, MARGIN")
    price: Decimal = Field(..., ge=0, description="Price value")
    market_factor: Optional[str] = Field(None, description="Market factor affecting price")
    approved_by: Optional[int] = Field(None, description="User ID who approved")

    @validator('price_type')
    def validate_price_type(cls, v):
        allowed_types = ['COST', 'SALE', 'MARGIN']
        if v not in allowed_types:
            raise ValueError(f'Price type must be one of: {allowed_types}')
        return v

class PriceResponse(PriceBase):
    """Complete price response schema"""
    price_id: int
    product_id: int
    created_date: datetime

    class Config:
        from_attributes = True

class CurrentPriceResponse(BaseModel):
    """Current price response schema"""
    product_id: int
    product_code: str
    product_name: str
    current_sale_price: Optional[Decimal] = None
    current_cost_price: Optional[Decimal] = None
    current_margin: Optional[Decimal] = None
    current_margin_percentage: Optional[Decimal] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

class MarketFactorBase(BaseModel):
    """Base market factor schema"""
    factor_code: str = Field(..., max_length=20, description="Factor code")
    factor_name: str = Field(..., max_length=50, description="Factor name")
    industry: str = Field(..., max_length=30, description="Industry affected")
    impact: str = Field(..., description="Impact level: HIGH, MEDIUM, LOW")
    description: Optional[str] = Field(None, max_length=200, description="Factor description")
    is_active: bool = Field(True, description="Active status")

    @validator('impact')
    def validate_impact(cls, v):
        allowed_impacts = ['HIGH', 'MEDIUM', 'LOW']
        if v not in allowed_impacts:
            raise ValueError(f'Impact must be one of: {allowed_impacts}')
        return v

class MarketFactorResponse(MarketFactorBase):
    """Complete market factor response schema"""
    factor_id: int

    class Config:
        from_attributes = True

class ProductMarketFactorBase(BaseModel):
    """Base product market factor schema"""
    product_id: int = Field(..., description="Product ID")
    factor_id: int = Field(..., description="Market factor ID")
    impact_weight: Decimal = Field(1.0, ge=0.1, le=2.0, description="Impact weight (0.1 to 2.0)")
    last_update_date: datetime = Field(default_factory=datetime.now, description="Last update date")

class ProductMarketFactorResponse(ProductMarketFactorBase):
    """Complete product market factor response schema"""
    factor: MarketFactorResponse

    class Config:
        from_attributes = True

class PricingAnalysisResponse(BaseModel):
    """Pricing analysis response schema"""
    product_id: int
    product_name: str
    current_price: Decimal
    average_market_price: Optional[Decimal] = None
    price_trend: str  # 'INCREASING', 'DECREASING', 'STABLE'
    volatility_score: Decimal
    last_change_date: Optional[datetime] = None
    days_since_last_change: Optional[int] = None
    market_factors_affecting: List[MarketFactorResponse] = []

class PriceHistoryResponse(BaseModel):
    """Price history response schema"""
    product_id: int
    product_code: str
    product_name: str
    price_history: List[PriceResponse]
    price_statistics: dict  # Contains min, max, avg, std_dev, etc.
    trend_analysis: dict    # Contains trend direction, volatility, etc.

class BulkPriceUpdateRequest(BaseModel):
    """Bulk price update request schema"""
    product_ids: List[int] = Field(..., description="List of product IDs")
    price_type: str = Field(..., description="Price type: COST, SALE, MARGIN")
    adjustment_type: str = Field(..., description="Adjustment type: PERCENTAGE, FIXED_AMOUNT")
    adjustment_value: Decimal = Field(..., description="Adjustment value")
    market_factor: Optional[str] = Field(None, description="Market factor causing update")
    approved_by: int = Field(..., description="User ID who approved")

    @validator('price_type')
    def validate_price_type(cls, v):
        allowed_types = ['COST', 'SALE', 'MARGIN']
        if v not in allowed_types:
            raise ValueError(f'Price type must be one of: {allowed_types}')
        return v

    @validator('adjustment_type')
    def validate_adjustment_type(cls, v):
        allowed_types = ['PERCENTAGE', 'FIXED_AMOUNT']
        if v not in allowed_types:
            raise ValueError(f'Adjustment type must be one of: {allowed_types}')
        return v

class BulkPriceUpdateResponse(BaseModel):
    """Bulk price update response schema"""
    updated_products: int
    failed_products: int
    total_products: int
    errors: List[str] = []
    updated_product_ids: List[int] = []