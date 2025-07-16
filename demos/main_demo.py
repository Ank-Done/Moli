#!/usr/bin/env python3
"""
CYBERIA FASTAPI APPLICATION - DEMO VERSION
Sistema de Inteligencia Empresarial para Moliendas y Alimentos
Versión demo con datos simulados (sin base de datos)
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime, date
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cyberia - Sistema de Inteligencia Empresarial (Demo)",
    description="Sistema avanzado para gestión de productos de azúcar, edulcorantes y servicios logísticos - Versión Demo",
    version="2.0.0-demo",
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

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mock data para demostración
MOCK_DASHBOARD_DATA = {
    "current_month_sales": "2.5M",
    "current_month_orders": 156,
    "current_avg_order": 16025.50,
    "ytd_sales": "18.7M",
    "total_customers": 89,
    "total_products": 247,
    "sales_change_pct": 12.5,
    "orders_change_pct": 8.3,
    "avg_order_change_pct": 15.2,
    "monthly_sales": [
        {"month_name": "Enero", "total_sales": 2800000, "year": 2024, "month": 1},
        {"month_name": "Febrero", "total_sales": 2650000, "year": 2024, "month": 2},
        {"month_name": "Marzo", "total_sales": 3200000, "year": 2024, "month": 3},
        {"month_name": "Abril", "total_sales": 2900000, "year": 2024, "month": 4},
        {"month_name": "Mayo", "total_sales": 3400000, "year": 2024, "month": 5},
        {"month_name": "Junio", "total_sales": 2750000, "year": 2024, "month": 6},
        {"month_name": "Julio", "total_sales": 0, "year": 2024, "month": 7}
    ],
    "sales_by_type": [
        {"order_type": "Venta Directa", "total_sales": 8500000},
        {"order_type": "Distribuidor", "total_sales": 6200000},
        {"order_type": "Exportación", "total_sales": 2800000},
        {"order_type": "Mayorista", "total_sales": 1200000}
    ],
    "top_agents": [
        {"agent_code": "AGT001", "agent_name": "María González", "total_sales": 3500000, "total_orders": 45},
        {"agent_code": "AGT002", "agent_name": "Carlos Rivera", "total_sales": 2800000, "total_orders": 38},
        {"agent_code": "AGT003", "agent_name": "Ana López", "total_sales": 2200000, "total_orders": 32},
        {"agent_code": "AGT004", "agent_name": "José Martínez", "total_sales": 1900000, "total_orders": 28},
        {"agent_code": "AGT005", "agent_name": "Laura Sánchez", "total_sales": 1600000, "total_orders": 24}
    ],
    "top_products": [
        {"product_code": "AZ001", "product_name": "Azúcar Estándar 50kg", "total_quantity": 125000, "total_sales": 4500000},
        {"product_code": "AZ002", "product_name": "Azúcar Refinada 25kg", "total_quantity": 98000, "total_sales": 3800000},
        {"product_code": "AZ003", "product_name": "Azúcar Morena 50kg", "total_quantity": 78000, "total_sales": 2900000},
        {"product_code": "ED001", "product_name": "Edulcorante Premium 1kg", "total_quantity": 15000, "total_sales": 1200000},
        {"product_code": "AZ004", "product_name": "Azúcar Glass 10kg", "total_quantity": 32000, "total_sales": 980000}
    ],
    "worst_products": [
        {"product_code": "ED003", "product_name": "Edulcorante Básico 500g", "total_quantity": 2500, "total_sales": 180000, "avg_margin": 5.2},
        {"product_code": "AZ007", "product_name": "Azúcar Orgánica 1kg", "total_quantity": 1200, "total_sales": 95000, "avg_margin": 7.8},
        {"product_code": "ED004", "product_name": "Stevia Natural 250g", "total_quantity": 800, "total_sales": 75000, "avg_margin": 8.5},
        {"product_code": "AZ008", "product_name": "Azúcar Demerara 2kg", "total_quantity": 950, "total_sales": 68000, "avg_margin": 9.2},
        {"product_code": "ED005", "product_name": "Edulcorante Líquido 500ml", "total_quantity": 600, "total_sales": 45000, "avg_margin": 11.8}
    ]
}

MOCK_PRODUCTS = [
    {
        "product_id": 1,
        "product_code": "AZ001",
        "product_name": "Azúcar Estándar 50kg",
        "industry": "SUGAR_PROCESSING",
        "unit": "kg",
        "standard_cost": 850.0,
        "standard_margin": 25.0,
        "is_active": True,
        "current_sale_price": 1125.0,
        "current_cost_price": 850.0,
        "current_margin_percentage": 24.4,
        "category": {
            "category_id": 1,
            "category_name": "Azúcar Refinada",
            "category_code": "AZ_REF"
        },
        "product_type": {
            "product_type_id": 1,
            "type_name": "Azúcar Industrial",
            "type_code": "AZ_IND"
        }
    },
    {
        "product_id": 2,
        "product_code": "AZ002", 
        "product_name": "Azúcar Refinada 25kg",
        "industry": "SUGAR_PROCESSING",
        "unit": "kg",
        "standard_cost": 450.0,
        "standard_margin": 28.0,
        "is_active": True,
        "current_sale_price": 625.0,
        "current_cost_price": 450.0,
        "current_margin_percentage": 28.0,
        "category": {
            "category_id": 1,
            "category_name": "Azúcar Refinada",
            "category_code": "AZ_REF"
        },
        "product_type": {
            "product_type_id": 1,
            "type_name": "Azúcar Industrial",
            "type_code": "AZ_IND"
        }
    }
]

# ========================================
# TEMPLATE ENDPOINTS
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
    return JSONResponse({"message": "Sales page - coming soon in full version"})

@app.get("/customers", response_class=HTMLResponse)
async def get_customers_page(request: Request):
    """Serve the customers page"""
    return JSONResponse({"message": "Customers page - coming soon in full version"})

@app.get("/pricing", response_class=HTMLResponse)
async def get_pricing_page(request: Request):
    """Serve the pricing management page"""
    return JSONResponse({"message": "Pricing page - coming soon in full version"})

@app.get("/analytics", response_class=HTMLResponse)
async def get_analytics_page(request: Request):
    """Serve the analytics page"""
    return JSONResponse({"message": "Analytics page - coming soon in full version"})

@app.get("/reports", response_class=HTMLResponse)
async def get_reports_page(request: Request):
    """Serve the reports page"""
    return JSONResponse({"message": "Reports page - coming soon in full version"})

# ========================================
# API ENDPOINTS
# ========================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "database": "mock data",
        "service": "Cyberia FastAPI Demo v2.0.0"
    }

@app.get("/api/analytics/dashboard-metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics with formatted currency"""
    try:
        return MOCK_DASHBOARD_DATA
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return {"error": str(e)}

@app.get("/api/products/search")
async def search_products(
    q: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Advanced product search with mock data"""
    try:
        filtered_products = MOCK_PRODUCTS.copy()
        
        if q:
            filtered_products = [p for p in filtered_products if q.lower() in p['product_name'].lower() or q.lower() in p['product_code'].lower()]
        
        if industry:
            filtered_products = [p for p in filtered_products if p['industry'] == industry]
        
        total_results = len(filtered_products)
        paginated_products = filtered_products[offset:offset + limit]
        
        return {
            "products": paginated_products,
            "total_results": total_results,
            "page": (offset // limit) + 1,
            "page_size": limit,
            "total_pages": (total_results + limit - 1) // limit,
            "filters_applied": {
                "query": q,
                "industry": industry
            }
        }
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return {"error": str(e)}

@app.get("/api/products/suggestions")
async def get_product_suggestions(q: str, limit: int = 10):
    """Get product suggestions for autocomplete"""
    try:
        suggestions = []
        for product in MOCK_PRODUCTS:
            if q.lower() in product['product_name'].lower() or q.lower() in product['product_code'].lower():
                suggestions.append({
                    "product_id": product["product_id"],
                    "product_code": product["product_code"],
                    "product_name": product["product_name"],
                    "sale_price": product["current_sale_price"],
                    "category": product["category"]["category_name"],
                    "display_text": f"{product['product_code']} - {product['product_name']}"
                })
            if len(suggestions) >= limit:
                break
        
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return {"error": str(e)}

@app.get("/api/products/filter-options")
async def get_filter_options():
    """Get available filter options for UI"""
    try:
        return {
            "categories": [
                {"code": "AZ_REF", "name": "Azúcar Refinada", "path": "/azucar/refinada"},
                {"code": "AZ_MOR", "name": "Azúcar Morena", "path": "/azucar/morena"},
                {"code": "EDUL", "name": "Edulcorantes", "path": "/edulcorantes"}
            ],
            "price_ranges": [
                {"range": "ECONOMICO", "product_count": 45},
                {"range": "MEDIO", "product_count": 128},
                {"range": "PREMIUM", "product_count": 74}
            ],
            "keyword_types": [],
            "industries": ["SUGAR_PROCESSING", "LOGISTICS", "SUPPLIES"],
            "product_types": [
                {"code": "AZ_IND", "name": "Azúcar Industrial", "industry": "SUGAR_PROCESSING"},
                {"code": "EDUL_NAT", "name": "Edulcorante Natural", "industry": "SUGAR_PROCESSING"}
            ]
        }
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        return {"error": str(e)}

@app.get("/api/products")
async def get_products(
    industry: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get list of products with mock data"""
    try:
        filtered_products = MOCK_PRODUCTS.copy()
        
        if industry:
            filtered_products = [p for p in filtered_products if p['industry'] == industry]
        
        paginated_products = filtered_products[offset:offset + limit]
        
        return paginated_products
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return {"error": str(e)}

# ========================================
# ERROR HANDLERS
# ========================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error (Demo mode)", "error": str(exc)}
    )

# ========================================
# STARTUP EVENT
# ========================================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Cyberia FastAPI Demo Application")
    logger.info("✅ Demo mode - using mock data")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down Cyberia FastAPI Demo Application")

if __name__ == "__main__":
    print("🚀 Iniciando Cyberia FastAPI Demo...")
    print("📊 Usando datos simulados (sin base de datos)")
    print("🌐 Servidor disponible en: http://localhost:8000")
    print("📚 Documentación API: http://localhost:8000/docs")
    print("🎨 Estilo inspirado en Obsidian Publish")
    print("💡 Dashboard con métricas en formato millones")
    
    uvicorn.run(
        "main_demo:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )