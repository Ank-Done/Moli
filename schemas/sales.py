"""
Pydantic schemas for Sales-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class DocumentTypeResponse(BaseModel):
    """Document type response schema"""
    document_type_id: int
    type_code: str
    type_name: str
    category: str
    requires_approval: bool
    affects_inventory: bool
    affects_accounting: bool

class SalesDocumentBase(BaseModel):
    """Base sales document schema"""
    customer_id: int = Field(..., description="Customer ID")
    agent_id: int = Field(..., description="Agent/User ID")
    document_date: Optional[datetime] = Field(None, description="Document date")
    due_date: Optional[datetime] = Field(None, description="Due date")
    notes: Optional[str] = Field(None, max_length=500, description="Document notes")

class SalesDocumentCreate(SalesDocumentBase):
    """Schema for creating sales documents"""
    document_type: str = Field(..., description="Document type code")

class DocumentDetailBase(BaseModel):
    """Base document detail schema"""
    product_id: int = Field(..., description="Product ID")
    quantity: Decimal = Field(..., gt=0, description="Quantity")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="Unit price (optional, will use dynamic pricing)")
    discount_percentage: Optional[Decimal] = Field(0, ge=0, le=100, description="Discount percentage")
    notes: Optional[str] = Field(None, max_length=200, description="Line notes")

class DocumentDetailCreate(DocumentDetailBase):
    """Schema for creating document details"""
    pass

class DocumentDetailResponse(DocumentDetailBase):
    """Document detail response schema"""
    detail_id: int
    unit_cost: Decimal
    line_total: Decimal
    margin: Decimal
    margin_percentage: Decimal
    discount_amount: Decimal
    tax_percentage: Decimal
    tax_amount: Decimal
    
    # Calculated fields
    profit_per_kg: Decimal
    sale_price_per_kg: Decimal
    cost_price_per_kg: Decimal
    
    # Product information
    product_code: str
    product_name: str
    product_category: str
    product_type: str
    industry: str

    class Config:
        from_attributes = True

class CustomerResponse(BaseModel):
    """Customer response schema"""
    customer_id: int
    customer_code: str
    business_name: str
    rfc: Optional[str]
    credit_enabled: bool
    credit_limit: Decimal
    payment_terms: int
    is_active: bool

class UserResponse(BaseModel):
    """User/Agent response schema"""
    user_id: int
    user_code: str
    user_name: str
    user_type: str
    initial_prefix: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    is_active: bool

class SalesDocumentResponse(SalesDocumentBase):
    """Complete sales document response schema"""
    document_id: int
    document_number: str
    document_type: DocumentTypeResponse
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    created_date: datetime
    modified_date: datetime
    
    # Related entities
    customer: CustomerResponse
    agent: UserResponse
    
    # Document details
    details: List[DocumentDetailResponse] = []
    
    # Summary calculations
    total_quantity: Decimal = 0
    total_margin: Decimal = 0
    avg_margin_percentage: Decimal = 0
    avg_profit_per_kg: Decimal = 0

    class Config:
        from_attributes = True

class SalesDocumentStatusUpdate(BaseModel):
    """Schema for updating document status"""
    new_status: str = Field(..., description="New status")
    user_id: int = Field(..., description="User making the change")
    notes: Optional[str] = Field(None, max_length=500, description="Status change notes")

    @validator('new_status')
    def validate_status(cls, v):
        allowed_statuses = ['DRAFT', 'APPROVED', 'DELIVERED', 'PAID', 'COMPLETED', 'CANCELLED', 'RETURNED']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {allowed_statuses}')
        return v

class SalesDocumentSearchRequest(BaseModel):
    """Sales document search request schema"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    customer_id: Optional[int] = None
    agent_id: Optional[int] = None
    status: Optional[str] = None
    document_type: Optional[str] = None
    product_id: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    page_size: int = Field(50, le=500)
    page_number: int = Field(1, ge=1)

class SalesDocumentSearchResponse(BaseModel):
    """Sales document search response schema"""
    documents: List[SalesDocumentResponse]
    total_records: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: Dict[str, Any]

class SalesProfitabilityResponse(BaseModel):
    """Sales profitability response schema"""
    sale_id: int
    document_id: int
    product_id: int
    sale_date: datetime
    quantity_sold: Decimal
    sale_price: Decimal
    cost_price: Decimal
    gross_profit: Decimal
    gross_profit_per_kg: Decimal
    margin_percentage: Decimal
    customer_id: int
    agent_id: int
    
    # Additional product and customer info
    product_name: str
    product_code: str
    customer_name: str
    agent_name: str

    class Config:
        from_attributes = True