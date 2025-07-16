"""
Product service for interacting with normalized product tables
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from config.database import db_manager
from schemas.products import (
    ProductResponse, ProductCreate, ProductUpdate, ProductFilter,
    ProductSearchResponse, ProductSuggestionResponse, FilterOptionsResponse,
    CategoryTreeResponse, ProductCategoryResponse, ProductTypeResponse,
    SugarProductAttributesResponse, LogisticsServiceAttributesResponse
)

logger = logging.getLogger(__name__)

class ProductService:
    """Service for managing products with normalized data structure"""
    
    async def get_products(self, filters: ProductFilter) -> List[ProductResponse]:
        """Get products with filters"""
        try:
            query = """
                SELECT 
                    p.ProductID, p.ProductCode, p.ProductName, p.Industry, p.Unit,
                    p.StandardCost, p.StandardMargin, p.IsActive, p.CreatedDate, p.ModifiedDate,
                    
                    -- Product Type
                    pt.ProductTypeID, pt.TypeCode, pt.TypeName, pt.Industry as PT_Industry, pt.Description as PT_Description,
                    
                    -- Category
                    pc.CategoryID, pc.CategoryCode, pc.CategoryName, pc.ParentCategoryID,
                    pc.Industry as PC_Industry, pc.Level, pc.Path, pc.Description as PC_Description,
                    
                    -- Sugar Attributes
                    sa.SugarType, sa.GranuleSize, sa.PurityLevel, sa.ColorGrade,
                    sa.PackagingType, sa.PackagingSize, sa.ShelfLifeDays,
                    
                    -- Logistics Attributes
                    la.ServiceType, la.ServiceSubtype, la.UnitType,
                    la.MinimumQuantity, la.MaximumQuantity, la.SetupTime,
                    
                    -- Current Pricing
                    (SELECT TOP 1 Price FROM DynamicPricing dp 
                     WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' 
                     AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) as CurrentSalePrice,
                     
                    (SELECT TOP 1 Price FROM DynamicPricing dp 
                     WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'COST' 
                     AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) as CurrentCostPrice
                     
                FROM Products p
                INNER JOIN ProductTypes pt ON p.ProductTypeID = pt.ProductTypeID
                INNER JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
                LEFT JOIN SugarProductAttributes sa ON p.ProductID = sa.ProductID
                LEFT JOIN LogisticsServiceAttributes la ON p.ProductID = la.ProductID
                WHERE 1=1
            """
            
            params = []
            
            if filters.industry:
                query += " AND p.Industry = ?"
                params.append(filters.industry)
            
            if filters.category_id:
                query += " AND p.CategoryID = ?"
                params.append(filters.category_id)
            
            if filters.is_active is not None:
                query += " AND p.IsActive = ?"
                params.append(1 if filters.is_active else 0)
            
            if filters.min_price:
                query += " AND (SELECT TOP 1 Price FROM DynamicPricing dp WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) >= ?"
                params.append(filters.min_price)
                
            if filters.max_price:
                query += " AND (SELECT TOP 1 Price FROM DynamicPricing dp WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) <= ?"
                params.append(filters.max_price)
            
            query += " ORDER BY p.ProductName"
            query += f" OFFSET {filters.offset} ROWS FETCH NEXT {filters.limit} ROWS ONLY"
            
            results = await db_manager.execute_query(query, tuple(params) if params else None)
            
            return [self._map_product_result(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            raise

    async def get_product_by_id(self, product_id: int) -> Optional[ProductResponse]:
        """Get product by ID"""
        try:
            query = """
                SELECT 
                    p.ProductID, p.ProductCode, p.ProductName, p.Industry, p.Unit,
                    p.StandardCost, p.StandardMargin, p.IsActive, p.CreatedDate, p.ModifiedDate,
                    
                    -- Product Type
                    pt.ProductTypeID, pt.TypeCode, pt.TypeName, pt.Industry as PT_Industry, pt.Description as PT_Description,
                    
                    -- Category
                    pc.CategoryID, pc.CategoryCode, pc.CategoryName, pc.ParentCategoryID,
                    pc.Industry as PC_Industry, pc.Level, pc.Path, pc.Description as PC_Description,
                    
                    -- Sugar Attributes
                    sa.SugarType, sa.GranuleSize, sa.PurityLevel, sa.ColorGrade,
                    sa.PackagingType, sa.PackagingSize, sa.ShelfLifeDays,
                    
                    -- Logistics Attributes
                    la.ServiceType, la.ServiceSubtype, la.UnitType,
                    la.MinimumQuantity, la.MaximumQuantity, la.SetupTime,
                    
                    -- Current Pricing
                    (SELECT TOP 1 Price FROM DynamicPricing dp 
                     WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' 
                     AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) as CurrentSalePrice,
                     
                    (SELECT TOP 1 Price FROM DynamicPricing dp 
                     WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'COST' 
                     AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) as CurrentCostPrice
                     
                FROM Products p
                INNER JOIN ProductTypes pt ON p.ProductTypeID = pt.ProductTypeID
                INNER JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
                LEFT JOIN SugarProductAttributes sa ON p.ProductID = sa.ProductID
                LEFT JOIN LogisticsServiceAttributes la ON p.ProductID = la.ProductID
                WHERE p.ProductID = ?
            """
            
            result = await db_manager.execute_query(query, (product_id,), fetch="one")
            
            if not result:
                return None
                
            return self._map_product_result(result)
            
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            raise

    async def search_products(
        self,
        query: Optional[str] = None,
        industry: Optional[str] = None,
        category: Optional[str] = None,
        price_range: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        limit: int = 20,
        offset: int = 0
    ) -> ProductSearchResponse:
        """Advanced product search"""
        try:
            # Build search query
            search_query = """
                WITH ProductSearch AS (
                    SELECT 
                        p.ProductID, p.ProductCode, p.ProductName, p.Industry, p.Unit,
                        p.StandardCost, p.StandardMargin, p.IsActive, p.CreatedDate, p.ModifiedDate,
                        pt.ProductTypeID, pt.TypeCode, pt.TypeName, pt.Industry as PT_Industry, pt.Description as PT_Description,
                        pc.CategoryID, pc.CategoryCode, pc.CategoryName, pc.ParentCategoryID,
                        pc.Industry as PC_Industry, pc.Level, pc.Path, pc.Description as PC_Description,
                        sa.SugarType, sa.GranuleSize, sa.PurityLevel, sa.ColorGrade,
                        sa.PackagingType, sa.PackagingSize, sa.ShelfLifeDays,
                        la.ServiceType, la.ServiceSubtype, la.UnitType,
                        la.MinimumQuantity, la.MaximumQuantity, la.SetupTime,
                        
                        -- Current Pricing
                        (SELECT TOP 1 Price FROM DynamicPricing dp 
                         WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' 
                         AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) as CurrentSalePrice,
                         
                        (SELECT TOP 1 Price FROM DynamicPricing dp 
                         WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'COST' 
                         AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) as CurrentCostPrice
                         
                    FROM Products p
                    INNER JOIN ProductTypes pt ON p.ProductTypeID = pt.ProductTypeID
                    INNER JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
                    LEFT JOIN SugarProductAttributes sa ON p.ProductID = sa.ProductID
                    LEFT JOIN LogisticsServiceAttributes la ON p.ProductID = la.ProductID
                    WHERE p.IsActive = 1
            """
            
            params = []
            
            # Text search
            if query:
                search_query += " AND (p.ProductName LIKE ? OR p.ProductCode LIKE ?)"
                search_term = f"%{query}%"
                params.extend([search_term, search_term])
            
            # Industry filter
            if industry:
                search_query += " AND p.Industry = ?"
                params.append(industry)
            
            # Category filter
            if category:
                search_query += " AND pc.Path LIKE ?"
                params.append(f"%{category}%")
            
            # Price filters
            if min_price:
                search_query += " AND (SELECT TOP 1 Price FROM DynamicPricing dp WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) >= ?"
                params.append(min_price)
                
            if max_price:
                search_query += " AND (SELECT TOP 1 Price FROM DynamicPricing dp WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) <= ?"
                params.append(max_price)
            
            search_query += ")"
            
            # Add sorting
            sort_column = {
                'name': 'ProductName',
                'price': 'CurrentSalePrice',
                'popularity': 'ProductName',  # Default to name for now
                'code': 'ProductCode'
            }.get(sort_by, 'ProductName')
            
            sort_direction = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM ({search_query}) as SearchResults"
            count_result = await db_manager.execute_query(count_query, tuple(params) if params else None, fetch="one")
            total_results = count_result['total'] if count_result else 0
            
            # Get paginated results
            paginated_query = f"""
                SELECT * FROM ({search_query}) as SearchResults 
                ORDER BY {sort_column} {sort_direction}
                OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY
            """
            
            results = await db_manager.execute_query(paginated_query, tuple(params) if params else None)
            
            products = [self._map_product_result(row) for row in results]
            
            total_pages = (total_results + limit - 1) // limit
            page = (offset // limit) + 1
            
            return ProductSearchResponse(
                products=products,
                total_results=total_results,
                page=page,
                page_size=limit,
                total_pages=total_pages,
                filters_applied={
                    'query': query,
                    'industry': industry,
                    'category': category,
                    'price_range': price_range,
                    'min_price': min_price,
                    'max_price': max_price,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            )
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            raise

    async def get_suggestions(self, query: str, limit: int = 10) -> List[ProductSuggestionResponse]:
        """Get product suggestions for autocomplete"""
        try:
            search_query = """
                SELECT TOP (?)
                    p.ProductID, p.ProductCode, p.ProductName,
                    pc.CategoryName,
                    (SELECT TOP 1 Price FROM DynamicPricing dp 
                     WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' 
                     AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC) as SalePrice
                FROM Products p
                INNER JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
                WHERE p.IsActive = 1 
                AND (p.ProductName LIKE ? OR p.ProductCode LIKE ?)
                ORDER BY 
                    CASE 
                        WHEN p.ProductCode LIKE ? THEN 1
                        WHEN p.ProductName LIKE ? THEN 2
                        ELSE 3
                    END,
                    p.ProductName
            """
            
            search_term = f"%{query}%"
            exact_start_term = f"{query}%"
            
            results = await db_manager.execute_query(
                search_query, 
                (limit, search_term, search_term, exact_start_term, exact_start_term)
            )
            
            suggestions = []
            for row in results:
                suggestions.append(ProductSuggestionResponse(
                    product_id=row['ProductID'],
                    product_code=row['ProductCode'],
                    product_name=row['ProductName'],
                    sale_price=row['SalePrice'] or 0,
                    category=row['CategoryName'],
                    display_text=f"{row['ProductCode']} - {row['ProductName']}" if row['ProductCode'] else row['ProductName']
                ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            raise

    async def get_categories(self) -> List[CategoryTreeResponse]:
        """Get hierarchical categories"""
        try:
            query = """
                SELECT 
                    CategoryID, CategoryCode, CategoryName, ParentCategoryID,
                    Industry, Level, Path, Description
                FROM ProductCategories
                WHERE IsActive = 1
                ORDER BY Level, CategoryName
            """
            
            results = await db_manager.execute_query(query)
            
            # Build hierarchical structure
            categories_map = {}
            root_categories = []
            
            for row in results:
                category = CategoryTreeResponse(
                    category_id=row['CategoryID'],
                    category_info=ProductCategoryResponse(
                        category_id=row['CategoryID'],
                        category_code=row['CategoryCode'],
                        category_name=row['CategoryName'],
                        parent_category_id=row['ParentCategoryID'],
                        industry=row['Industry'],
                        level=row['Level'],
                        path=row['Path'],
                        description=row['Description']
                    ),
                    children=[],
                    product_count=0
                )
                
                categories_map[row['CategoryID']] = category
                
                if row['ParentCategoryID'] is None:
                    root_categories.append(category)
                else:
                    parent = categories_map.get(row['ParentCategoryID'])
                    if parent:
                        parent.children.append(category)
            
            return root_categories
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise

    async def get_filter_options(self) -> FilterOptionsResponse:
        """Get filter options for UI"""
        try:
            # Get categories
            categories_query = """
                SELECT CategoryCode, CategoryName, Path
                FROM ProductCategories
                WHERE IsActive = 1
                ORDER BY CategoryName
            """
            categories = await db_manager.execute_query(categories_query)
            
            # Get price ranges (calculate from current dynamic pricing)
            price_ranges_query = """
                SELECT 
                    CASE 
                        WHEN CurrentPrice = 0 THEN 'SIN_PRECIO'
                        WHEN CurrentPrice <= 100 THEN 'ECONOMICO'
                        WHEN CurrentPrice <= 500 THEN 'MEDIO'
                        WHEN CurrentPrice <= 2000 THEN 'PREMIUM'
                        ELSE 'ULTRA_PREMIUM'
                    END as PriceRange,
                    COUNT(*) as ProductCount
                FROM (
                    SELECT p.ProductID,
                        ISNULL((SELECT TOP 1 Price FROM DynamicPricing dp 
                                WHERE dp.ProductID = p.ProductID AND dp.PriceType = 'SALE' 
                                AND dp.IsActive = 1 ORDER BY dp.EffectiveDate DESC), 0) as CurrentPrice
                    FROM Products p
                    WHERE p.IsActive = 1
                ) PriceData
                GROUP BY 
                    CASE 
                        WHEN CurrentPrice = 0 THEN 'SIN_PRECIO'
                        WHEN CurrentPrice <= 100 THEN 'ECONOMICO'
                        WHEN CurrentPrice <= 500 THEN 'MEDIO'
                        WHEN CurrentPrice <= 2000 THEN 'PREMIUM'
                        ELSE 'ULTRA_PREMIUM'
                    END
                ORDER BY 
                    CASE 
                        WHEN PriceRange = 'ECONOMICO' THEN 1
                        WHEN PriceRange = 'MEDIO' THEN 2
                        WHEN PriceRange = 'PREMIUM' THEN 3
                        WHEN PriceRange = 'ULTRA_PREMIUM' THEN 4
                        ELSE 5
                    END
            """
            price_ranges = await db_manager.execute_query(price_ranges_query)
            
            # Get product types
            product_types_query = """
                SELECT TypeCode, TypeName, Industry
                FROM ProductTypes
                ORDER BY TypeName
            """
            product_types = await db_manager.execute_query(product_types_query)
            
            return FilterOptionsResponse(
                categories=[
                    {
                        'code': cat['CategoryCode'],
                        'name': cat['CategoryName'], 
                        'path': cat['Path']
                    }
                    for cat in categories
                ],
                price_ranges=[
                    {
                        'range': pr['PriceRange'],
                        'product_count': pr['ProductCount']
                    }
                    for pr in price_ranges
                ],
                keyword_types=[],  # Will implement later if needed
                industries=['SUGAR_PROCESSING', 'LOGISTICS', 'SUPPLIES'],
                product_types=[
                    {
                        'code': pt['TypeCode'],
                        'name': pt['TypeName'],
                        'industry': pt['Industry']
                    }
                    for pt in product_types
                ]
            )
            
        except Exception as e:
            logger.error(f"Error getting filter options: {e}")
            raise

    def _map_product_result(self, row: dict) -> ProductResponse:
        """Map database row to ProductResponse"""
        try:
            # Calculate current margin percentage
            current_margin_pct = None
            if row.get('CurrentSalePrice') and row.get('CurrentCostPrice'):
                sale_price = float(row['CurrentSalePrice'])
                cost_price = float(row['CurrentCostPrice'])
                if sale_price > 0:
                    current_margin_pct = ((sale_price - cost_price) / sale_price) * 100
            
            product = ProductResponse(
                product_id=row['ProductID'],
                product_code=row['ProductCode'],
                product_name=row['ProductName'],
                industry=row['Industry'],
                unit=row['Unit'],
                standard_cost=row['StandardCost'],
                standard_margin=row['StandardMargin'],
                is_active=bool(row['IsActive']),
                created_date=row['CreatedDate'],
                modified_date=row['ModifiedDate'],
                current_sale_price=row.get('CurrentSalePrice'),
                current_cost_price=row.get('CurrentCostPrice'),
                current_margin_percentage=current_margin_pct,
                
                product_type=ProductTypeResponse(
                    product_type_id=row['ProductTypeID'],
                    type_code=row['TypeCode'],
                    type_name=row['TypeName'],
                    industry=row['PT_Industry'],
                    description=row['PT_Description']
                ),
                
                category=ProductCategoryResponse(
                    category_id=row['CategoryID'],
                    category_code=row['CategoryCode'],
                    category_name=row['CategoryName'],
                    parent_category_id=row['ParentCategoryID'],
                    industry=row['PC_Industry'],
                    level=row['Level'],
                    path=row['Path'],
                    description=row['PC_Description']
                )
            )
            
            # Add sugar attributes if present
            if row.get('SugarType'):
                product.sugar_attributes = SugarProductAttributesResponse(
                    sugar_type=row['SugarType'],
                    granule_size=row['GranuleSize'],
                    purity_level=row['PurityLevel'],
                    color_grade=row['ColorGrade'],
                    packaging_type=row['PackagingType'],
                    packaging_size=row['PackagingSize'],
                    shelf_life_days=row['ShelfLifeDays']
                )
            
            # Add logistics attributes if present
            if row.get('ServiceType'):
                product.logistics_attributes = LogisticsServiceAttributesResponse(
                    service_type=row['ServiceType'],
                    service_subtype=row['ServiceSubtype'],
                    unit_type=row['UnitType'],
                    minimum_quantity=row['MinimumQuantity'],
                    maximum_quantity=row['MaximumQuantity'],
                    setup_time=row['SetupTime']
                )
            
            return product
            
        except Exception as e:
            logger.error(f"Error mapping product result: {e}")
            raise

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create new product"""
        try:
            # Use the CreateProduct stored procedure
            procedure_params = (
                product_data.product_code,
                product_data.product_name,
                product_data.industry,
                product_data.product_type_id,
                product_data.category_id,
                product_data.unit,
                product_data.standard_cost,
                product_data.standard_margin,
                product_data.notes
            )
            
            result = await db_manager.execute_procedure("CreateProduct", procedure_params)
            
            # Get the new product ID from result
            if result and len(result) > 0:
                product_id = result[0].get('ProductID') if isinstance(result[0], dict) else result[0][0]
                return await self.get_product_by_id(product_id)
            else:
                raise Exception("Failed to create product")
                
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise

    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[ProductResponse]:
        """Update existing product"""
        try:
            # Use the UpdateProduct stored procedure
            procedure_params = (
                product_id,
                product_data.product_name,
                product_data.category_id,
                product_data.unit,
                product_data.standard_cost,
                product_data.standard_margin,
                product_data.is_active,
                product_data.notes
            )
            
            await db_manager.execute_procedure("UpdateProduct", procedure_params)
            
            # Return the updated product
            return await self.get_product_by_id(product_id)
                
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            raise

    async def delete_product(self, product_id: int) -> bool:
        """Delete product (soft delete)"""
        try:
            # Soft delete by setting IsActive = 0
            query = """
                UPDATE Products 
                SET IsActive = 0, ModifiedDate = GETDATE()
                WHERE ProductID = ?
            """
            
            await db_manager.execute_query(query, (product_id,))
            return True
                
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            raise