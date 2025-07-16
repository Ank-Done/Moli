"""
Pydantic schemas for Analytics-related operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class MonthlyComparisonResponse(BaseModel):
    """Monthly comparison response schema"""
    product_id: int
    product_code: str
    product_name: str
    category_name: str
    product_type: str
    
    # Current Month Data
    current_year: int
    current_month: int
    current_month_name: str
    current_quantity: Decimal
    current_sales: Decimal
    current_margin: Decimal
    current_margin_pct: Decimal
    current_customers: int
    current_orders: int
    
    # Previous Month Data
    previous_year: Optional[int]
    previous_month: Optional[int]
    previous_month_name: Optional[str]
    previous_quantity: Decimal
    previous_sales: Decimal
    previous_margin: Decimal
    previous_margin_pct: Decimal
    previous_customers: int
    previous_orders: int
    
    # Comparison Calculations
    quantity_change_percentage: Optional[Decimal]
    sales_change_percentage: Optional[Decimal]
    margin_change_percentage: Optional[Decimal]
    quantity_difference: Decimal
    sales_difference: Decimal
    margin_difference: Decimal
    
    # Performance Classification
    performance_category: str  # 'EXCELLENT', 'GOOD', 'STABLE', 'DECLINING', 'CRITICAL'

    class Config:
        from_attributes = True

class DailyProfitabilityResponse(BaseModel):
    """Daily profitability response schema"""
    sale_date: date
    week_day: str
    product_code: str
    product_name: str
    category_name: str
    order_count: int
    total_quantity: Decimal
    total_sales: Decimal
    total_margin: Decimal
    avg_margin_percentage: Decimal
    total_cost: Decimal
    avg_selling_price: Decimal
    avg_cost_price: Decimal
    unique_customers: int
    
    # Key metric: Profitability per kg
    profit_per_kg: Decimal
    
    # Daily trends
    previous_day_sales: Optional[Decimal]
    day_over_day_growth: Optional[Decimal]

    class Config:
        from_attributes = True

class DashboardMetricsResponse(BaseModel):
    """Dashboard metrics response schema"""
    # Current month sales (formatted in millions)
    current_month_sales: str = Field(..., description="Sales in millions format (e.g., '2.5M')")
    current_month_orders: int
    current_avg_order: Decimal
    ytd_sales: str = Field(..., description="Year to date sales in millions format")
    
    # Basic metrics
    total_customers: int
    total_products: int
    
    # Change indicators
    sales_change_pct: Optional[Decimal]
    orders_change_pct: Optional[Decimal]
    avg_order_change_pct: Optional[Decimal]
    
    # Monthly sales data for charts (ordered by calendar month)
    monthly_sales: List[Dict[str, Any]] = Field(..., description="Monthly sales ordered by calendar")
    sales_by_type: List[Dict[str, Any]]
    
    # Top performers
    top_agents: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    worst_products: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class ProfitPerKgAnalysisResponse(BaseModel):
    """Profit per kg analysis response schema"""
    product_id: int
    product_code: str
    product_name: str
    category_name: str
    product_type: str
    
    # Analysis period
    start_date: date
    end_date: date
    
    # Profit per kg metrics
    avg_profit_per_kg: Decimal
    min_profit_per_kg: Decimal
    max_profit_per_kg: Decimal
    total_kg_sold: Decimal
    total_profit: Decimal
    
    # Performance metrics
    profitable_days: int
    total_sales_days: int
    profitability_ratio: Decimal  # profitable_days / total_sales_days
    
    # Trend analysis
    trend_direction: str  # 'IMPROVING', 'DECLINING', 'STABLE'
    volatility_score: Decimal
    
    # Market position
    rank_by_profit_per_kg: Optional[int]
    percentile_profit_per_kg: Optional[Decimal]

    class Config:
        from_attributes = True

class YearlyComparisonResponse(BaseModel):
    """Yearly comparison response schema"""
    product_id: int
    product_code: str
    product_name: str
    category_name: str
    product_type: str
    
    # Current Year Data
    current_year: int
    current_year_quantity: Decimal
    current_year_sales: Decimal
    current_year_margin: Decimal
    current_year_margin_pct: Decimal
    
    # Previous Year Data
    previous_year: int
    previous_year_quantity: Decimal
    previous_year_sales: Decimal
    previous_year_margin: Decimal
    previous_year_margin_pct: Decimal
    
    # Year-over-Year Comparison
    year_over_year_quantity_change: Optional[Decimal]
    year_over_year_sales_change: Optional[Decimal]
    year_over_year_margin_change: Optional[Decimal]

    class Config:
        from_attributes = True

class MonthlyReportResponse(BaseModel):
    """Monthly report response schema"""
    report_year: int
    report_month: int
    month_name: str
    
    # Executive Summary
    products_sold: int
    total_quantity_sold: Decimal
    total_sales_amount: Decimal
    total_margin_amount: Decimal
    overall_margin_percentage: Decimal
    total_customers: int
    total_orders: int
    
    # Top performers
    top_products_by_sales: List[MonthlyComparisonResponse]
    top_products_by_margin: List[MonthlyComparisonResponse]
    underperforming_products: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class SalesAgentPerformanceResponse(BaseModel):
    """Sales agent performance response schema"""
    agent_id: int
    agent_code: str
    agent_name: str
    agent_type: str
    
    # Performance metrics
    total_sales: Decimal
    total_orders: int
    avg_order_value: Decimal
    total_customers: int
    total_products_sold: int
    
    # Profit metrics
    total_margin: Decimal
    avg_margin_percentage: Decimal
    profit_per_kg_avg: Decimal
    
    # Period comparison
    sales_growth: Optional[Decimal]
    orders_growth: Optional[Decimal]
    
    # Rankings
    sales_rank: Optional[int]
    margin_rank: Optional[int]

    class Config:
        from_attributes = True

class ProductPerformanceResponse(BaseModel):
    """Product performance response schema"""
    product_id: int
    product_code: str
    product_name: str
    category_name: str
    industry: str
    
    # Sales metrics
    total_quantity: Decimal
    total_sales: Decimal
    total_orders: int
    avg_order_size: Decimal
    
    # Profitability metrics
    total_margin: Decimal
    avg_margin_percentage: Decimal
    profit_per_kg: Decimal
    
    # Market metrics
    market_share: Optional[Decimal]
    price_competitiveness: Optional[str]  # 'COMPETITIVE', 'OVERPRICED', 'UNDERPRICED'
    
    # Trend analysis
    sales_trend: str  # 'GROWING', 'DECLINING', 'STABLE'
    demand_pattern: str  # 'SEASONAL', 'CONSISTENT', 'IRREGULAR'

    class Config:
        from_attributes = True