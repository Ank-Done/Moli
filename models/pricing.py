"""
Pricing service for managing dynamic pricing system
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from config.database import db_manager
from schemas.pricing import (
    PriceResponse, PriceUpdate, CurrentPriceResponse,
    PriceHistoryResponse, PricingRuleResponse, MarketPriceResponse
)

logger = logging.getLogger(__name__)

class PricingService:
    """Service for managing dynamic pricing"""
    
    async def get_current_prices(
        self, 
        product_id: Optional[int] = None,
        price_type: Optional[str] = None,
        industry: Optional[str] = None
    ) -> List[CurrentPriceResponse]:
        """Get current active prices"""
        try:
            query = """
                WITH CurrentPrices AS (
                    SELECT 
                        dp.PriceID,
                        dp.ProductID,
                        dp.PriceType,
                        dp.Price,
                        dp.EffectiveDate,
                        dp.ExpirationDate,
                        dp.IsActive,
                        dp.CreatedDate,
                        dp.ModifiedDate,
                        dp.Notes,
                        p.ProductCode,
                        p.ProductName,
                        p.Industry,
                        pc.CategoryName,
                        ROW_NUMBER() OVER (
                            PARTITION BY dp.ProductID, dp.PriceType 
                            ORDER BY dp.EffectiveDate DESC
                        ) as rn
                    FROM DynamicPricing dp
                    INNER JOIN Products p ON dp.ProductID = p.ProductID
                    INNER JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
                    WHERE dp.IsActive = 1
                    AND dp.EffectiveDate <= GETDATE()
                    AND (dp.ExpirationDate IS NULL OR dp.ExpirationDate > GETDATE())
                )
                SELECT 
                    PriceID, ProductID, PriceType, Price, EffectiveDate, ExpirationDate,
                    IsActive, CreatedDate, ModifiedDate, Notes,
                    ProductCode, ProductName, Industry, CategoryName
                FROM CurrentPrices 
                WHERE rn = 1
            """
            
            params = []
            
            if product_id:
                query += " AND ProductID = ?"
                params.append(product_id)
            
            if price_type:
                query += " AND PriceType = ?"
                params.append(price_type)
                
            if industry:
                query += " AND Industry = ?"
                params.append(industry)
            
            query += " ORDER BY ProductCode, PriceType"
            
            results = await db_manager.execute_query(query, tuple(params) if params else None)
            
            return [
                CurrentPriceResponse(
                    price_id=row['PriceID'],
                    product_id=row['ProductID'],
                    product_code=row['ProductCode'],
                    product_name=row['ProductName'],
                    category_name=row['CategoryName'],
                    industry=row['Industry'],
                    price_type=row['PriceType'],
                    current_price=row['Price'],
                    effective_date=row['EffectiveDate'],
                    expiration_date=row['ExpirationDate'],
                    is_active=bool(row['IsActive']),
                    last_updated=row['ModifiedDate'] or row['CreatedDate'],
                    notes=row['Notes']
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting current prices: {e}")
            raise

    async def update_price(
        self, 
        product_id: int, 
        price_data: PriceUpdate,
        user_id: int
    ) -> CurrentPriceResponse:
        """Update product price"""
        try:
            # Use the UpdateProductPrice stored procedure
            procedure_params = (
                product_id,
                price_data.price_type,
                price_data.new_price,
                price_data.effective_date,
                price_data.expiration_date,
                user_id,
                price_data.notes
            )
            
            result = await db_manager.execute_procedure("UpdateProductPrice", procedure_params)
            
            # Get the updated price
            updated_prices = await self.get_current_prices(
                product_id=product_id, 
                price_type=price_data.price_type
            )
            
            if updated_prices:
                return updated_prices[0]
            else:
                raise Exception("Failed to retrieve updated price")
                
        except Exception as e:
            logger.error(f"Error updating price for product {product_id}: {e}")
            raise

    async def get_price_history(
        self,
        product_id: int,
        price_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50
    ) -> List[PriceHistoryResponse]:
        """Get price history for a product"""
        try:
            query = """
                SELECT 
                    dp.PriceID,
                    dp.ProductID,
                    dp.PriceType,
                    dp.Price,
                    dp.EffectiveDate,
                    dp.ExpirationDate,
                    dp.IsActive,
                    dp.CreatedDate,
                    dp.ModifiedDate,
                    dp.Notes,
                    p.ProductCode,
                    p.ProductName,
                    u.UserName as UpdatedBy
                FROM DynamicPricing dp
                INNER JOIN Products p ON dp.ProductID = p.ProductID
                LEFT JOIN Users u ON dp.UpdatedBy = u.UserID
                WHERE dp.ProductID = ?
            """
            
            params = [product_id]
            
            if price_type:
                query += " AND dp.PriceType = ?"
                params.append(price_type)
            
            if start_date:
                query += " AND dp.EffectiveDate >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND dp.EffectiveDate <= ?"
                params.append(end_date)
            
            query += f" ORDER BY dp.EffectiveDate DESC, dp.CreatedDate DESC OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
            
            results = await db_manager.execute_query(query, tuple(params))
            
            return [
                PriceHistoryResponse(
                    price_id=row['PriceID'],
                    product_id=row['ProductID'],
                    product_code=row['ProductCode'],
                    product_name=row['ProductName'],
                    price_type=row['PriceType'],
                    price=row['Price'],
                    effective_date=row['EffectiveDate'],
                    expiration_date=row['ExpirationDate'],
                    is_active=bool(row['IsActive']),
                    created_date=row['CreatedDate'],
                    updated_by=row['UpdatedBy'],
                    notes=row['Notes']
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting price history for product {product_id}: {e}")
            raise

    async def get_market_prices(
        self,
        industry: str = "SUGAR_PROCESSING",
        date_range: int = 30
    ) -> List[MarketPriceResponse]:
        """Get market price analysis"""
        try:
            query = """
                WITH MarketPrices AS (
                    SELECT 
                        p.ProductID,
                        p.ProductCode,
                        p.ProductName,
                        pc.CategoryName,
                        pt.TypeName as ProductType,
                        AVG(CASE WHEN dp.PriceType = 'SALE' THEN dp.Price END) as AvgSalePrice,
                        MIN(CASE WHEN dp.PriceType = 'SALE' THEN dp.Price END) as MinSalePrice,
                        MAX(CASE WHEN dp.PriceType = 'SALE' THEN dp.Price END) as MaxSalePrice,
                        AVG(CASE WHEN dp.PriceType = 'COST' THEN dp.Price END) as AvgCostPrice,
                        COUNT(DISTINCT CASE WHEN dp.PriceType = 'SALE' THEN dp.PriceID END) as PriceUpdates,
                        MAX(CASE WHEN dp.PriceType = 'SALE' THEN dp.EffectiveDate END) as LastPriceUpdate
                    FROM Products p
                    INNER JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
                    INNER JOIN ProductTypes pt ON p.ProductTypeID = pt.ProductTypeID
                    INNER JOIN DynamicPricing dp ON p.ProductID = dp.ProductID
                    WHERE p.Industry = ?
                    AND dp.EffectiveDate >= DATEADD(DAY, -?, GETDATE())
                    AND p.IsActive = 1
                    GROUP BY p.ProductID, p.ProductCode, p.ProductName, pc.CategoryName, pt.TypeName
                )
                SELECT 
                    ProductID, ProductCode, ProductName, CategoryName, ProductType,
                    AvgSalePrice, MinSalePrice, MaxSalePrice, AvgCostPrice,
                    PriceUpdates, LastPriceUpdate,
                    CASE 
                        WHEN AvgSalePrice > 0 AND AvgCostPrice > 0 
                        THEN ((AvgSalePrice - AvgCostPrice) / AvgSalePrice) * 100
                        ELSE 0 
                    END as MarginPercentage,
                    CASE 
                        WHEN MaxSalePrice > MinSalePrice AND MinSalePrice > 0
                        THEN ((MaxSalePrice - MinSalePrice) / MinSalePrice) * 100
                        ELSE 0 
                    END as PriceVolatility
                FROM MarketPrices
                ORDER BY AvgSalePrice DESC
            """
            
            results = await db_manager.execute_query(query, (industry, date_range))
            
            return [
                MarketPriceResponse(
                    product_id=row['ProductID'],
                    product_code=row['ProductCode'],
                    product_name=row['ProductName'],
                    category_name=row['CategoryName'],
                    product_type=row['ProductType'],
                    avg_sale_price=row['AvgSalePrice'] or 0,
                    min_sale_price=row['MinSalePrice'] or 0,
                    max_sale_price=row['MaxSalePrice'] or 0,
                    avg_cost_price=row['AvgCostPrice'] or 0,
                    margin_percentage=row['MarginPercentage'] or 0,
                    price_volatility=row['PriceVolatility'] or 0,
                    price_updates_count=row['PriceUpdates'] or 0,
                    last_price_update=row['LastPriceUpdate'],
                    market_position='STABLE',  # Would need more complex analysis
                    competitiveness_score=0    # Would need competitor data
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting market prices: {e}")
            raise

    async def bulk_update_prices(
        self,
        price_updates: List[Dict[str, Any]],
        user_id: int
    ) -> List[CurrentPriceResponse]:
        """Bulk update prices"""
        try:
            updated_prices = []
            
            for update_data in price_updates:
                price_update = PriceUpdate(
                    price_type=update_data['price_type'],
                    new_price=update_data['new_price'],
                    effective_date=update_data.get('effective_date', date.today()),
                    expiration_date=update_data.get('expiration_date'),
                    notes=update_data.get('notes')
                )
                
                updated_price = await self.update_price(
                    product_id=update_data['product_id'],
                    price_data=price_update,
                    user_id=user_id
                )
                updated_prices.append(updated_price)
            
            return updated_prices
            
        except Exception as e:
            logger.error(f"Error bulk updating prices: {e}")
            raise

    async def get_pricing_suggestions(
        self,
        product_id: int,
        target_margin: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get pricing suggestions based on costs and market data"""
        try:
            # Get current cost and market data
            query = """
                SELECT 
                    p.ProductID,
                    p.ProductCode,
                    p.ProductName,
                    p.StandardCost,
                    p.StandardMargin,
                    (SELECT TOP 1 Price FROM DynamicPricing dp 
                     WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'COST' 
                     AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) as CurrentCostPrice,
                    (SELECT TOP 1 Price FROM DynamicPricing dp 
                     WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' 
                     AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) as CurrentSalePrice,
                    (SELECT AVG(sdd.UnitPrice) FROM SalesDocumentDetails sdd
                     INNER JOIN SalesDocuments sd ON sdd.DocumentID = sd.DocumentID
                     WHERE sdd.ProductID = p.ProductID 
                     AND sd.DocumentDate >= DATEADD(DAY, -30, GETDATE())) as RecentAvgSalePrice
                FROM Products p
                WHERE p.ProductID = ?
            """
            
            result = await db_manager.execute_query(query, (product_id,), fetch="one")
            
            if not result:
                return {}
            
            current_cost = result['CurrentCostPrice'] or result['StandardCost'] or 0
            current_sale = result['CurrentSalePrice'] or 0
            recent_avg_sale = result['RecentAvgSalePrice'] or 0
            target_margin_pct = target_margin or result['StandardMargin'] or 20
            
            # Calculate suggestions
            suggested_sale_price = current_cost / (1 - (target_margin_pct / 100))
            
            suggestions = {
                'product_id': product_id,
                'product_code': result['ProductCode'],
                'product_name': result['ProductName'],
                'current_cost_price': current_cost,
                'current_sale_price': current_sale,
                'recent_avg_sale_price': recent_avg_sale,
                'target_margin_percentage': target_margin_pct,
                'suggested_sale_price': suggested_sale_price,
                'current_margin_percentage': (
                    ((current_sale - current_cost) / current_sale) * 100 
                    if current_sale > 0 else 0
                ),
                'price_adjustment_needed': suggested_sale_price - current_sale,
                'price_adjustment_percentage': (
                    ((suggested_sale_price - current_sale) / current_sale) * 100 
                    if current_sale > 0 else 0
                ),
                'market_position': (
                    'ABOVE_MARKET' if current_sale > recent_avg_sale else 
                    'BELOW_MARKET' if current_sale < recent_avg_sale else 
                    'AT_MARKET'
                ) if recent_avg_sale > 0 else 'NO_MARKET_DATA'
            }
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting pricing suggestions for product {product_id}: {e}")
            raise