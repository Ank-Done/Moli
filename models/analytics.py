"""
Analytics service for dashboard metrics and comparisons
Implementa formato en millones y ordenamiento correcto por calendario
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from config.database import db_manager
from schemas.analytics import (
    DashboardMetricsResponse, MonthlyComparisonResponse, 
    DailyProfitabilityResponse, ProfitPerKgAnalysisResponse,
    MonthlyReportResponse, YearlyComparisonResponse
)

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for analytics and dashboard metrics"""
    
    def _format_currency_to_millions(self, amount: float) -> str:
        """Format currency amount to millions format"""
        if amount is None or amount == 0:
            return "0"
        
        millions = amount / 1_000_000
        
        if millions >= 1000:
            # Format as billions for very large amounts
            billions = millions / 1000
            return f"{billions:.1f}B"
        elif millions >= 100:
            return f"{millions:.0f}M"
        elif millions >= 10:
            return f"{millions:.1f}M"
        elif millions >= 1:
            return f"{millions:.2f}M"
        else:
            # For amounts less than 1 million, show in thousands
            thousands = amount / 1000
            if thousands >= 1:
                return f"{thousands:.0f}K"
            else:
                return f"{amount:.0f}"

    async def get_dashboard_metrics(self) -> DashboardMetricsResponse:
        """Get dashboard metrics with proper formatting"""
        try:
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            
            # Para julio 2025, el mes actual debe mostrar 0 ya que no hay ventas de julio aún
            logger.info(f"Getting dashboard metrics for {current_year}-{current_month:02d}")
            
            # Métricas del mes actual
            current_month_query = """
                SELECT 
                    ISNULL(SUM(sd.Total), 0) as CurrentMonthSales,
                    COUNT(DISTINCT sd.DocumentID) as CurrentMonthOrders,
                    CASE 
                        WHEN COUNT(DISTINCT sd.DocumentID) > 0 
                        THEN ISNULL(SUM(sd.Total), 0) / COUNT(DISTINCT sd.DocumentID)
                        ELSE 0 
                    END as CurrentAvgOrder
                FROM SalesDocuments sd
                INNER JOIN DocumentTypes dt ON sd.DocumentTypeID = dt.DocumentTypeID
                WHERE YEAR(sd.DocumentDate) = ? 
                AND MONTH(sd.DocumentDate) = ?
                AND sd.Status IN ('APPROVED', 'DELIVERED', 'PAID', 'COMPLETED')
                AND dt.Category = 'SALES'
            """
            
            current_metrics = await db_manager.execute_query(
                current_month_query, 
                (current_year, current_month), 
                fetch="one"
            )
            
            # Métricas del mes anterior para comparación
            prev_month = current_month - 1 if current_month > 1 else 12
            prev_year = current_year if current_month > 1 else current_year - 1
            
            prev_month_query = """
                SELECT 
                    ISNULL(SUM(sd.Total), 0) as PrevMonthSales,
                    COUNT(DISTINCT sd.DocumentID) as PrevMonthOrders,
                    CASE 
                        WHEN COUNT(DISTINCT sd.DocumentID) > 0 
                        THEN ISNULL(SUM(sd.Total), 0) / COUNT(DISTINCT sd.DocumentID)
                        ELSE 0 
                    END as PrevAvgOrder
                FROM SalesDocuments sd
                INNER JOIN DocumentTypes dt ON sd.DocumentTypeID = dt.DocumentTypeID
                WHERE YEAR(sd.DocumentDate) = ? 
                AND MONTH(sd.DocumentDate) = ?
                AND sd.Status IN ('APPROVED', 'DELIVERED', 'PAID', 'COMPLETED')
                AND dt.Category = 'SALES'
            """
            
            prev_metrics = await db_manager.execute_query(
                prev_month_query, 
                (prev_year, prev_month), 
                fetch="one"
            )
            
            # Ventas año a la fecha
            ytd_query = """
                SELECT ISNULL(SUM(sd.Total), 0) as YTDSales
                FROM SalesDocuments sd
                INNER JOIN DocumentTypes dt ON sd.DocumentTypeID = dt.DocumentTypeID
                WHERE YEAR(sd.DocumentDate) = ?
                AND sd.Status IN ('APPROVED', 'DELIVERED', 'PAID', 'COMPLETED')
                AND dt.Category = 'SALES'
            """
            
            ytd_result = await db_manager.execute_query(ytd_query, (current_year,), fetch="one")
            
            # Métricas básicas
            basic_metrics_query = """
                SELECT 
                    (SELECT COUNT(*) FROM Customers WHERE IsActive = 1) as TotalCustomers,
                    (SELECT COUNT(*) FROM Products WHERE IsActive = 1) as TotalProducts
            """
            
            basic_metrics = await db_manager.execute_query(basic_metrics_query, fetch="one")
            
            # Calcular porcentajes de cambio
            def calculate_change_pct(current, previous):
                if previous and previous > 0:
                    return ((current - previous) / previous) * 100
                return None
            
            sales_change = calculate_change_pct(
                current_metrics['CurrentMonthSales'], 
                prev_metrics['PrevMonthSales']
            )
            orders_change = calculate_change_pct(
                current_metrics['CurrentMonthOrders'], 
                prev_metrics['PrevMonthOrders']
            )
            avg_order_change = calculate_change_pct(
                current_metrics['CurrentAvgOrder'], 
                prev_metrics['PrevAvgOrder']
            )
            
            # Ventas mensuales ordenadas por calendario (12 meses hacia atrás)
            monthly_sales_query = """
                SELECT 
                    YEAR(sd.DocumentDate) as SalesYear,
                    MONTH(sd.DocumentDate) as SalesMonth,
                    DATENAME(MONTH, sd.DocumentDate) as MonthName,
                    SUM(sd.Total) as TotalSales
                FROM SalesDocuments sd
                INNER JOIN DocumentTypes dt ON sd.DocumentTypeID = dt.DocumentTypeID
                WHERE sd.DocumentDate >= DATEADD(MONTH, -12, GETDATE())
                AND sd.Status IN ('APPROVED', 'DELIVERED', 'PAID', 'COMPLETED')
                AND dt.Category = 'SALES'
                GROUP BY YEAR(sd.DocumentDate), MONTH(sd.DocumentDate), DATENAME(MONTH, sd.DocumentDate)
                ORDER BY SalesYear, SalesMonth
            """
            
            monthly_sales_data = await db_manager.execute_query(monthly_sales_query)
            
            # Ventas por tipo
            sales_by_type_query = """
                SELECT 
                    dt.TypeName as OrderType,
                    SUM(sd.Total) as TotalSales
                FROM SalesDocuments sd
                INNER JOIN DocumentTypes dt ON sd.DocumentTypeID = dt.DocumentTypeID
                WHERE YEAR(sd.DocumentDate) = ?
                AND sd.Status IN ('APPROVED', 'DELIVERED', 'PAID', 'COMPLETED')
                AND dt.Category = 'SALES'
                GROUP BY dt.TypeName
                ORDER BY TotalSales DESC
            """
            
            sales_by_type = await db_manager.execute_query(sales_by_type_query, (current_year,))
            
            # Top agentes
            top_agents_query = """
                SELECT TOP 5
                    u.UserCode as AgentCode,
                    u.UserName as AgentName,
                    SUM(sd.Total) as TotalSales,
                    COUNT(DISTINCT sd.DocumentID) as TotalOrders
                FROM SalesDocuments sd
                INNER JOIN Users u ON sd.AgentID = u.UserID
                INNER JOIN DocumentTypes dt ON sd.DocumentTypeID = dt.DocumentTypeID
                WHERE YEAR(sd.DocumentDate) = ?
                AND sd.Status IN ('APPROVED', 'DELIVERED', 'PAID', 'COMPLETED')
                AND dt.Category = 'SALES'
                GROUP BY u.UserCode, u.UserName
                ORDER BY TotalSales DESC
            """
            
            top_agents = await db_manager.execute_query(top_agents_query, (current_year,))
            
            # Top productos
            top_products_query = """
                SELECT TOP 5
                    p.ProductCode,
                    p.ProductName,
                    SUM(sdd.Quantity) as TotalQuantity,
                    SUM(sdd.LineTotal) as TotalSales
                FROM SalesDocuments sd
                INNER JOIN SalesDocumentDetails sdd ON sd.DocumentID = sdd.DocumentID
                INNER JOIN Products p ON sdd.ProductID = p.ProductID
                INNER JOIN DocumentTypes dt ON sd.DocumentTypeID = dt.DocumentTypeID
                WHERE YEAR(sd.DocumentDate) = ?
                AND sd.Status IN ('APPROVED', 'DELIVERED', 'PAID', 'COMPLETED')
                AND dt.Category = 'SALES'
                AND p.Industry = 'SUGAR_PROCESSING'
                GROUP BY p.ProductCode, p.ProductName
                ORDER BY TotalSales DESC
            """
            
            top_products = await db_manager.execute_query(top_products_query, (current_year,))
            
            # Productos con bajo rendimiento
            worst_products_query = """
                SELECT TOP 5
                    p.ProductCode,
                    p.ProductName,
                    SUM(sdd.Quantity) as TotalQuantity,
                    SUM(sdd.LineTotal) as TotalSales,
                    AVG(sdd.MarginPercentage) as AvgMargin
                FROM SalesDocuments sd
                INNER JOIN SalesDocumentDetails sdd ON sd.DocumentID = sdd.DocumentID
                INNER JOIN Products p ON sdd.ProductID = p.ProductID
                INNER JOIN DocumentTypes dt ON sd.DocumentTypeID = dt.DocumentTypeID
                WHERE YEAR(sd.DocumentDate) = ?
                AND sd.Status IN ('APPROVED', 'DELIVERED', 'PAID', 'COMPLETED')
                AND dt.Category = 'SALES'
                AND p.Industry = 'SUGAR_PROCESSING'
                GROUP BY p.ProductCode, p.ProductName
                HAVING SUM(sdd.LineTotal) > 0
                ORDER BY AVG(sdd.MarginPercentage) ASC
            """
            
            worst_products = await db_manager.execute_query(worst_products_query, (current_year,))
            
            # Construir respuesta
            return DashboardMetricsResponse(
                current_month_sales=self._format_currency_to_millions(current_metrics['CurrentMonthSales']),
                current_month_orders=current_metrics['CurrentMonthOrders'],
                current_avg_order=current_metrics['CurrentAvgOrder'],
                ytd_sales=self._format_currency_to_millions(ytd_result['YTDSales']),
                total_customers=basic_metrics['TotalCustomers'],
                total_products=basic_metrics['TotalProducts'],
                sales_change_pct=sales_change,
                orders_change_pct=orders_change,
                avg_order_change_pct=avg_order_change,
                monthly_sales=[
                    {
                        'month_name': row['MonthName'],
                        'total_sales': float(row['TotalSales']) if row['TotalSales'] else 0,
                        'year': row['SalesYear'],
                        'month': row['SalesMonth']
                    }
                    for row in monthly_sales_data
                ],
                sales_by_type=[
                    {
                        'order_type': row['OrderType'],
                        'total_sales': float(row['TotalSales']) if row['TotalSales'] else 0
                    }
                    for row in sales_by_type
                ],
                top_agents=[
                    {
                        'agent_code': row['AgentCode'],
                        'agent_name': row['AgentName'],
                        'total_sales': float(row['TotalSales']) if row['TotalSales'] else 0,
                        'total_orders': row['TotalOrders']
                    }
                    for row in top_agents
                ],
                top_products=[
                    {
                        'product_code': row['ProductCode'],
                        'product_name': row['ProductName'],
                        'total_quantity': float(row['TotalQuantity']) if row['TotalQuantity'] else 0,
                        'total_sales': float(row['TotalSales']) if row['TotalSales'] else 0
                    }
                    for row in top_products
                ],
                worst_products=[
                    {
                        'product_code': row['ProductCode'],
                        'product_name': row['ProductName'],
                        'total_quantity': float(row['TotalQuantity']) if row['TotalQuantity'] else 0,
                        'total_sales': float(row['TotalSales']) if row['TotalSales'] else 0,
                        'avg_margin': float(row['AvgMargin']) if row['AvgMargin'] else 0
                    }
                    for row in worst_products
                ]
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            raise

    async def get_monthly_comparison(
        self, 
        year: Optional[int] = None, 
        month: Optional[int] = None,
        product_category: Optional[str] = None
    ) -> List[MonthlyComparisonResponse]:
        """Get monthly comparison data"""
        try:
            if not year:
                year = datetime.now().year
            if not month:
                month = datetime.now().month
                
            # Use the stored procedure we created
            procedure_params = (year, month, product_category)
            results = await db_manager.execute_procedure("GenerateMonthlyReport", procedure_params)
            
            # The procedure returns multiple result sets, we want the comparison data
            if isinstance(results, list) and len(results) > 1:
                comparison_data = results[1]  # Second result set should be comparisons
            else:
                comparison_data = results if isinstance(results, list) else []
            
            return [
                MonthlyComparisonResponse(
                    product_id=row['ProductID'],
                    product_code=row['ProductCode'],
                    product_name=row['ProductName'],
                    category_name=row['CategoryName'],
                    product_type=row['ProductType'],
                    current_year=year,
                    current_month=month,
                    current_month_name=row.get('MonthName', ''),
                    current_quantity=row.get('TotalQuantity', 0),
                    current_sales=row.get('TotalSales', 0),
                    current_margin=row.get('TotalMargin', 0),
                    current_margin_pct=row.get('AvgMarginPercentage', 0),
                    current_customers=row.get('UniqueCustomers', 0),
                    current_orders=row.get('DocumentCount', 0),
                    previous_year=year if month > 1 else year - 1,
                    previous_month=month - 1 if month > 1 else 12,
                    previous_month_name='',  # We'll calculate this
                    previous_quantity=0,  # These would come from comparison logic
                    previous_sales=0,
                    previous_margin=0,
                    previous_margin_pct=0,
                    previous_customers=0,
                    previous_orders=0,
                    quantity_change_percentage=None,
                    sales_change_percentage=None,
                    margin_change_percentage=None,
                    quantity_difference=0,
                    sales_difference=0,
                    margin_difference=0,
                    performance_category='STABLE'
                )
                for row in comparison_data
            ]
            
        except Exception as e:
            logger.error(f"Error getting monthly comparison: {e}")
            raise

    async def get_daily_profitability(
        self, 
        start_date: date, 
        end_date: date,
        product_id: Optional[int] = None
    ) -> List[DailyProfitabilityResponse]:
        """Get daily profitability analysis"""
        try:
            # Use the stored procedure we created
            procedure_params = (start_date, end_date, product_id)
            results = await db_manager.execute_procedure("GetDailyProfitabilityAnalysis", procedure_params)
            
            daily_data = results if isinstance(results, list) else []
            
            return [
                DailyProfitabilityResponse(
                    sale_date=row['SaleDate'],
                    week_day=row['WeekDay'],
                    product_code=row['ProductCode'],
                    product_name=row['ProductName'],
                    category_name=row['CategoryName'],
                    order_count=row['OrderCount'],
                    total_quantity=row['TotalQuantity'],
                    total_sales=row['TotalSales'],
                    total_margin=row['TotalMargin'],
                    avg_margin_percentage=row['AvgMarginPercentage'],
                    total_cost=row['TotalCost'],
                    avg_selling_price=row['AvgSellingPrice'],
                    avg_cost_price=row['AvgCostPrice'],
                    unique_customers=row['UniqueCustomers'],
                    profit_per_kg=row['ProfitPerKg'],
                    previous_day_sales=row.get('PreviousDaySales'),
                    day_over_day_growth=row.get('DayOverDayGrowth')
                )
                for row in daily_data
            ]
            
        except Exception as e:
            logger.error(f"Error getting daily profitability: {e}")
            raise

    async def get_profit_per_kg_analysis(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        product_category: Optional[str] = None
    ) -> List[ProfitPerKgAnalysisResponse]:
        """Get profit per kg analysis for sugar products"""
        try:
            if not start_date:
                start_date = date.today().replace(day=1)  # First day of current month
            if not end_date:
                end_date = date.today()
                
            query = """
                SELECT 
                    p.ProductID,
                    p.ProductCode,
                    p.ProductName,
                    pc.CategoryName,
                    pt.TypeName as ProductType,
                    AVG(
                        CASE 
                            WHEN sdd.Quantity > 0 THEN sdd.Margin / sdd.Quantity 
                            ELSE 0 
                        END
                    ) as AvgProfitPerKg,
                    MIN(
                        CASE 
                            WHEN sdd.Quantity > 0 THEN sdd.Margin / sdd.Quantity 
                            ELSE 0 
                        END
                    ) as MinProfitPerKg,
                    MAX(
                        CASE 
                            WHEN sdd.Quantity > 0 THEN sdd.Margin / sdd.Quantity 
                            ELSE 0 
                        END
                    ) as MaxProfitPerKg,
                    SUM(sdd.Quantity) as TotalKgSold,
                    SUM(sdd.Margin) as TotalProfit,
                    COUNT(DISTINCT CAST(sd.DocumentDate as DATE)) as TotalSalesDays,
                    COUNT(DISTINCT CASE WHEN sdd.Margin > 0 THEN CAST(sd.DocumentDate as DATE) END) as ProfitableDays
                FROM SalesDocuments sd
                INNER JOIN SalesDocumentDetails sdd ON sd.DocumentID = sdd.DocumentID
                INNER JOIN Products p ON sdd.ProductID = p.ProductID
                INNER JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
                INNER JOIN ProductTypes pt ON p.ProductTypeID = pt.ProductTypeID
                INNER JOIN DocumentTypes dt ON sd.DocumentTypeID = dt.DocumentTypeID
                WHERE sd.DocumentDate >= ?
                AND sd.DocumentDate <= ?
                AND sd.Status IN ('APPROVED', 'DELIVERED', 'PAID', 'COMPLETED')
                AND dt.Category = 'SALES'
                AND p.Industry = 'SUGAR_PROCESSING'
            """
            
            params = [start_date, end_date]
            
            if product_category:
                query += " AND pc.CategoryName = ?"
                params.append(product_category)
            
            query += """
                GROUP BY p.ProductID, p.ProductCode, p.ProductName, pc.CategoryName, pt.TypeName
                HAVING SUM(sdd.Quantity) > 0
                ORDER BY AvgProfitPerKg DESC
            """
            
            results = await db_manager.execute_query(query, tuple(params))
            
            return [
                ProfitPerKgAnalysisResponse(
                    product_id=row['ProductID'],
                    product_code=row['ProductCode'],
                    product_name=row['ProductName'],
                    category_name=row['CategoryName'],
                    product_type=row['ProductType'],
                    start_date=start_date,
                    end_date=end_date,
                    avg_profit_per_kg=row['AvgProfitPerKg'],
                    min_profit_per_kg=row['MinProfitPerKg'],
                    max_profit_per_kg=row['MaxProfitPerKg'],
                    total_kg_sold=row['TotalKgSold'],
                    total_profit=row['TotalProfit'],
                    profitable_days=row['ProfitableDays'] or 0,
                    total_sales_days=row['TotalSalesDays'] or 0,
                    profitability_ratio=(
                        row['ProfitableDays'] / row['TotalSalesDays'] 
                        if row['TotalSalesDays'] and row['TotalSalesDays'] > 0 
                        else 0
                    ),
                    trend_direction='STABLE',  # Would need more complex analysis
                    volatility_score=0,        # Would need historical data analysis
                    rank_by_profit_per_kg=None,
                    percentile_profit_per_kg=None
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting profit per kg analysis: {e}")
            raise