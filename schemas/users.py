"""
Pydantic schemas for User-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class UserTypeResponse(BaseModel):
    """User type response schema"""
    user_type_id: int
    type_code: str
    type_name: str
    description: Optional[str]
    industry: Optional[str]

class UserBase(BaseModel):
    """Base user schema"""
    user_code: str = Field(..., max_length=30, description="Unique user code")
    user_name: str = Field(..., max_length=60, description="User full name")
    email: Optional[str] = Field(None, max_length=100, description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    is_active: bool = Field(True, description="Active status")

class UserCreate(UserBase):
    """Schema for creating users"""
    user_type_id: int = Field(..., description="User type ID")

class UserUpdate(BaseModel):
    """Schema for updating users"""
    user_name: Optional[str] = Field(None, max_length=60)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Complete user response schema"""
    user_id: int
    user_type: UserTypeResponse
    initial_prefix: Optional[str]
    created_date: datetime
    modified_date: datetime

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    """Base customer schema"""
    customer_code: str = Field(..., max_length=30, description="Unique customer code")
    business_name: str = Field(..., max_length=60, description="Business name")
    rfc: Optional[str] = Field(None, max_length=20, description="RFC (tax ID)")
    credit_enabled: bool = Field(False, description="Credit sales enabled")
    credit_limit: Optional[float] = Field(0, ge=0, description="Credit limit")
    payment_terms: int = Field(0, ge=0, description="Payment terms in days")
    is_active: bool = Field(True, description="Active status")

class CustomerCreate(CustomerBase):
    """Schema for creating customers"""
    customer_type_id: Optional[int] = Field(None, description="Customer type ID")

class CustomerUpdate(BaseModel):
    """Schema for updating customers"""
    business_name: Optional[str] = Field(None, max_length=60)
    rfc: Optional[str] = Field(None, max_length=20)
    credit_enabled: Optional[bool] = None
    credit_limit: Optional[float] = Field(None, ge=0)
    payment_terms: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class CustomerResponse(CustomerBase):
    """Complete customer response schema"""
    customer_id: int
    customer_type: Optional[UserTypeResponse] = None
    created_date: datetime
    modified_date: datetime

    class Config:
        from_attributes = True

class AddressBase(BaseModel):
    """Base address schema"""
    entity_type: str = Field(..., description="Entity type: CUSTOMER, USER, SUPPLIER")
    entity_id: int = Field(..., description="Entity ID")
    address_type: str = Field("PRIMARY", description="Address type: PRIMARY, BILLING, SHIPPING")
    street: Optional[str] = Field(None, max_length=100, description="Street address")
    city: Optional[str] = Field(None, max_length=50, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State")
    postal_code: Optional[str] = Field(None, max_length=10, description="Postal code")
    country: str = Field("México", max_length=50, description="Country")
    is_active: bool = Field(True, description="Active status")

    @validator('entity_type')
    def validate_entity_type(cls, v):
        allowed_types = ['CUSTOMER', 'USER', 'SUPPLIER']
        if v not in allowed_types:
            raise ValueError(f'Entity type must be one of: {allowed_types}')
        return v

    @validator('address_type')
    def validate_address_type(cls, v):
        allowed_types = ['PRIMARY', 'BILLING', 'SHIPPING']
        if v not in allowed_types:
            raise ValueError(f'Address type must be one of: {allowed_types}')
        return v

class AddressCreate(AddressBase):
    """Schema for creating addresses"""
    pass

class AddressUpdate(BaseModel):
    """Schema for updating addresses"""
    address_type: Optional[str] = None
    street: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class AddressResponse(AddressBase):
    """Complete address response schema"""
    address_id: int

    class Config:
        from_attributes = True