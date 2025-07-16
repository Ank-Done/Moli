#!/usr/bin/env python3
"""
CYBERIA FASTAPI APPLICATION
Sistema de Inteligencia Empresarial para Moliendas y Alimentos
Implementación moderna con FastAPI para manejo de productos de azúcar y edulcorantes
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime, date
import logging

# Import our modules
from config.database import get_db_connection, test_connection
from models.products import ProductService
from models.sales import SalesService
from models.users import UserService
from models.pricing import PricingService
from models.analytics import AnalyticsService
from schemas.products import ProductResponse, ProductCreate, ProductUpdate, ProductFilter
from schemas.sales import SalesDocumentResponse, SalesDocumentCreate, DocumentDetailCreate
from schemas.users import UserResponse, CustomerResponse
from schemas.pricing import PriceResponse, PriceUpdate
from schemas.analytics import MonthlyComparisonResponse, DailyProfitabilityResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cyberia - Sistema de Inteligencia Empresarial",
    description="Sistema avanzado para gestión de productos de azúcar, edulcorantes y servicios logísticos para Moliendas y Alimentos",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
product_service = ProductService()
sales_service = SalesService()
user_service = UserService()
pricing_service = PricingService()
analytics_service = AnalyticsService()

# ========================================
# ROOT ENDPOINTS
# ========================================

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Serve the dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serve the dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/products", response_class=HTMLResponse)
async def get_products_page(request: Request):
    """Serve the products management page"""
    return templates.TemplateResponse("products.html", {"request": request})

@app.get("/sales", response_class=HTMLResponse)
async def get_sales_page(request: Request):
    """Serve the sales management page"""
    return templates.TemplateResponse("sales.html", {"request": request})

@app.get("/customers", response_class=HTMLResponse)
async def get_customers_page(request: Request):
    """Serve the customers page"""
    return templates.TemplateResponse("customers.html", {"request": request})

@app.get("/pricing", response_class=HTMLResponse)
async def get_pricing_page(request: Request):
    """Serve the pricing management page"""
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/analytics", response_class=HTMLResponse)
async def get_analytics_page(request: Request):
    """Serve the analytics page"""
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/reports", response_class=HTMLResponse)
async def get_reports_page(request: Request):
    """Serve the reports page"""
    return templates.TemplateResponse("reports.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        test_connection()
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "database": "connected",
            "service": "Cyberia FastAPI v2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# ========================================
# PRODUCT ENDPOINTS
# ========================================

@app.get("/api/products", response_model=List[ProductResponse])
async def get_products(
    industry: Optional[str] = Query(None, description="Filter by industry: SUGAR_PROCESSING, LOGISTICS, SUPPLIES"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    is_active: bool = Query(True, description="Filter by active status"),
    limit: int = Query(50, le=500, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip")
):
    """Get list of products with optional filters"""
    try:
        filters = ProductFilter(
            industry=industry,
            category_id=category_id,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        products = await product_service.get_products(filters)
        return products
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int = Path(..., description="Product ID")):
    """Get specific product by ID"""
    try:
        product = await product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products", response_model=ProductResponse)
async def create_product(product_data: ProductCreate):
    """Create new product"""
    try:
        product = await product_service.create_product(product_data)
        return product
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_data: ProductUpdate):
    """Update existing product"""
    try:
        product = await product_service.update_product(product_id, product_data)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    """Delete product (soft delete)"""
    try:
        success = await product_service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/search")
async def search_products(
    q: Optional[str] = Query(None, description="Search query"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    category: Optional[str] = Query(None, description="Filter by category path"),
    price_range: Optional[str] = Query(None, description="Filter by price range"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    sort_by: str = Query("name", description="Sort field: name, price, popularity"),
    sort_order: str = Query("asc", description="Sort order: asc, desc"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Advanced product search with multiple filters"""
    try:
        results = await product_service.search_products(
            query=q,
            industry=industry,
            category=category,
            price_range=price_range,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/categories")
async def get_product_categories():
    """Get hierarchical product categories"""
    try:
        categories = await product_service.get_categories()
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/suggestions")
async def get_product_suggestions(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, le=20, description="Maximum suggestions")
):
    """Get product suggestions for autocomplete"""
    try:
        suggestions = await product_service.get_suggestions(q, limit)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/filter-options")
async def get_filter_options():
    """Get available filter options for UI"""
    try:
        filters = await product_service.get_filter_options()
        return filters
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# SALES ENDPOINTS
# ========================================

@app.get("/api/sales/documents", response_model=List[SalesDocumentResponse])
async def get_sales_documents(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    agent_id: Optional[int] = Query(None, description="Filter by agent"),
    status: Optional[str] = Query(None, description="Filter by status"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0)
):
    """Get sales documents with filters"""
    try:
        documents = await sales_service.get_sales_documents(
            start_date=start_date,
            end_date=end_date,
            customer_id=customer_id,
            agent_id=agent_id,
            status=status,
            document_type=document_type,
            limit=limit,
            offset=offset
        )
        return documents
    except Exception as e:
        logger.error(f"Error getting sales documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales/documents", response_model=SalesDocumentResponse)
async def create_sales_document(document_data: SalesDocumentCreate):
    """Create new sales document"""
    try:
        document = await sales_service.create_sales_document(document_data)
        return document
    except Exception as e:
        logger.error(f"Error creating sales document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sales/documents/{document_id}", response_model=SalesDocumentResponse)
async def get_sales_document(document_id: int):
    """Get specific sales document with details"""
    try:
        document = await sales_service.get_sales_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Sales document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sales document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales/documents/{document_id}/details")
async def add_product_to_document(document_id: int, detail_data: DocumentDetailCreate):
    """Add product to sales document"""
    try:
        success = await sales_service.add_product_to_document(document_id, detail_data)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found or cannot be modified")
        return {"message": "Product added to document successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding product to document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/sales/documents/{document_id}/status")
async def change_document_status(
    document_id: int,
    new_status: str = Query(..., description="New status"),
    user_id: int = Query(..., description="User making the change"),
    notes: Optional[str] = Query(None, description="Change notes")
):
    """Change document status"""
    try:
        success = await sales_service.change_document_status(document_id, new_status, user_id, notes)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found or invalid status transition")
        return {"message": f"Document status changed to {new_status}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing document status {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# PRICING ENDPOINTS
# ========================================

@app.get("/api/pricing/current")
async def get_current_prices(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    price_type: Optional[str] = Query(None, description="Filter by price type: COST, SALE"),
    industry: Optional[str] = Query(None, description="Filter by industry")
):
    """Get current active prices"""
    try:
        prices = await pricing_service.get_current_prices(product_id, price_type, industry)
        return prices
    except Exception as e:
        logger.error(f"Error getting current prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/pricing/{product_id}")
async def update_product_price(
    product_id: int, 
    price_data: PriceUpdate,
    user_id: int = Query(..., description="User ID making the update")
):
    """Update product price (creates new price record)"""
    try:
        updated_price = await pricing_service.update_price(product_id, price_data, user_id)
        return updated_price
    except Exception as e:
        logger.error(f"Error updating price for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pricing/{product_id}/history")
async def get_price_history(
    product_id: int,
    price_type: Optional[str] = Query(None, description="Filter by price type"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(50, le=200, description="Maximum records")
):
    """Get price history for a product"""
    try:
        history = await pricing_service.get_price_history(product_id, price_type, start_date, end_date, limit)
        return history
    except Exception as e:
        logger.error(f"Error getting price history for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pricing/market-analysis")
async def get_market_prices(
    industry: str = Query("SUGAR_PROCESSING", description="Industry to analyze"),
    date_range: int = Query(30, description="Days to look back for analysis")
):
    """Get market price analysis"""
    try:
        market_data = await pricing_service.get_market_prices(industry, date_range)
        return market_data
    except Exception as e:
        logger.error(f"Error getting market prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pricing/bulk-update")
async def bulk_update_prices(
    price_updates: List[Dict[str, Any]],
    user_id: int = Query(..., description="User ID making the updates")
):
    """Bulk update multiple product prices"""
    try:
        updated_prices = await pricing_service.bulk_update_prices(price_updates, user_id)
        return {"message": f"Successfully updated {len(updated_prices)} prices", "updated_prices": updated_prices}
    except Exception as e:
        logger.error(f"Error bulk updating prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pricing/{product_id}/suggestions")
async def get_pricing_suggestions(
    product_id: int,
    target_margin: Optional[float] = Query(None, description="Target margin percentage")
):
    """Get pricing suggestions for a product"""
    try:
        suggestions = await pricing_service.get_pricing_suggestions(product_id, target_margin)
        return suggestions
    except Exception as e:
        logger.error(f"Error getting pricing suggestions for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ANALYTICS ENDPOINTS
# ========================================

@app.get("/api/analytics/monthly-comparison", response_model=List[MonthlyComparisonResponse])
async def get_monthly_comparison(
    year: Optional[int] = Query(None, description="Year for comparison"),
    month: Optional[int] = Query(None, description="Month for comparison"),
    product_category: Optional[str] = Query(None, description="Filter by product category")
):
    """Get monthly comparison data"""
    try:
        comparison = await analytics_service.get_monthly_comparison(year, month, product_category)
        return comparison
    except Exception as e:
        logger.error(f"Error getting monthly comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/daily-profitability", response_model=List[DailyProfitabilityResponse])
async def get_daily_profitability(
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    product_id: Optional[int] = Query(None, description="Filter by specific product")
):
    """Get daily profitability analysis"""
    try:
        profitability = await analytics_service.get_daily_profitability(start_date, end_date, product_id)
        return profitability
    except Exception as e:
        logger.error(f"Error getting daily profitability: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/dashboard-metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics with formatted currency"""
    try:
        metrics = await analytics_service.get_dashboard_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/profit-per-kg")
async def get_profit_per_kg_analysis(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    product_category: Optional[str] = Query(None, description="Filter by category")
):
    """Get profit per kg analysis for sugar products"""
    try:
        analysis = await analytics_service.get_profit_per_kg_analysis(start_date, end_date, product_category)
        return analysis
    except Exception as e:
        logger.error(f"Error getting profit per kg analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# USER ENDPOINTS
# ========================================

@app.get("/api/users", response_model=List[UserResponse])
async def get_users(
    user_type: Optional[str] = Query(None, description="Filter by user type"),
    is_active: bool = Query(True, description="Filter by active status")
):
    """Get list of users/agents"""
    try:
        users = await user_service.get_users(user_type, is_active)
        return users
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers", response_model=List[CustomerResponse])
async def get_customers(
    is_active: bool = Query(True, description="Filter by active status")
):
    """Get list of customers"""
    try:
        customers = await user_service.get_customers(is_active)
        return customers
    except Exception as e:
        logger.error(f"Error getting customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ERROR HANDLERS
# ========================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# ========================================
# STARTUP/SHUTDOWN EVENTS
# ========================================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Cyberia FastAPI Application")
    try:
        # Test database connection
        test_connection()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down Cyberia FastAPI Application")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )