"""
Pydantic schemas for Product-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    """Base product schema"""
    product_code: str = Field(..., max_length=30, description="Unique product code")
    product_name: str = Field(..., max_length=60, description="Product name")
    industry: str = Field(..., description="Industry: SUGAR_PROCESSING, LOGISTICS, SUPPLIES")
    unit: Optional[str] = Field("KG", max_length=20, description="Unit of measurement")
    standard_cost: Optional[Decimal] = Field(0, ge=0, description="Standard cost")
    standard_margin: Optional[Decimal] = Field(0, ge=0, le=100, description="Standard margin percentage")
    is_active: bool = Field(True, description="Active status")

    @validator('industry')
    def validate_industry(cls, v):
        allowed_industries = ['SUGAR_PROCESSING', 'LOGISTICS', 'SUPPLIES']
        if v not in allowed_industries:
            raise ValueError(f'Industry must be one of: {allowed_industries}')
        return v

class ProductCreate(ProductBase):
    """Schema for creating products"""
    product_type_id: int = Field(..., description="Product type ID")
    category_id: int = Field(..., description="Category ID")

class ProductUpdate(BaseModel):
    """Schema for updating products"""
    product_name: Optional[str] = Field(None, max_length=60)
    unit: Optional[str] = Field(None, max_length=20)
    standard_cost: Optional[Decimal] = Field(None, ge=0)
    standard_margin: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None

class ProductTypeResponse(BaseModel):
    """Product type response schema"""
    product_type_id: int
    type_code: str
    type_name: str
    industry: str
    description: Optional[str]

class ProductCategoryResponse(BaseModel):
    """Product category response schema"""
    category_id: int
    category_code: str
    category_name: str
    parent_category_id: Optional[int]
    industry: str
    level: int
    path: Optional[str]
    description: Optional[str]

class SugarProductAttributesResponse(BaseModel):
    """Sugar product attributes response schema"""
    sugar_type: Optional[str]
    granule_size: Optional[str]
    purity_level: Optional[Decimal]
    color_grade: Optional[str]
    packaging_type: Optional[str]
    packaging_size: Optional[Decimal]
    shelf_life_days: Optional[int]

class LogisticsServiceAttributesResponse(BaseModel):
    """Logistics service attributes response schema"""
    service_type: Optional[str]
    service_subtype: Optional[str]
    unit_type: Optional[str]
    minimum_quantity: Optional[Decimal]
    maximum_quantity: Optional[Decimal]
    setup_time: Optional[int]

class ProductResponse(ProductBase):
    """Complete product response schema"""
    product_id: int
    product_type: ProductTypeResponse
    category: ProductCategoryResponse
    sugar_attributes: Optional[SugarProductAttributesResponse] = None
    logistics_attributes: Optional[LogisticsServiceAttributesResponse] = None
    created_date: datetime
    modified_date: datetime
    
    # Current pricing information
    current_sale_price: Optional[Decimal] = None
    current_cost_price: Optional[Decimal] = None
    current_margin_percentage: Optional[Decimal] = None

    class Config:
        from_attributes = True

class ProductFilter(BaseModel):
    """Product filter schema"""
    industry: Optional[str] = None
    category_id: Optional[int] = None
    product_type_id: Optional[int] = None
    is_active: bool = True
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    limit: int = Field(50, le=500)
    offset: int = Field(0, ge=0)

class ProductSearchResponse(BaseModel):
    """Product search response schema"""
    products: List[ProductResponse]
    total_results: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: Dict[str, Any]

class ProductSuggestionResponse(BaseModel):
    """Product suggestion response schema"""
    product_id: int
    product_code: str
    product_name: str
    sale_price: Optional[Decimal]
    category: str
    display_text: str

class FilterOptionsResponse(BaseModel):
    """Filter options response schema"""
    categories: List[Dict[str, Any]]
    price_ranges: List[Dict[str, Any]]
    keyword_types: List[Dict[str, Any]]
    industries: List[str]
    product_types: List[Dict[str, Any]]

class CategoryTreeResponse(BaseModel):
    """Category tree response schema"""
    category_id: int
    category_info: ProductCategoryResponse
    children: List['CategoryTreeResponse'] = []
    product_count: int = 0

# Update forward references
CategoryTreeResponse.model_rebuild()