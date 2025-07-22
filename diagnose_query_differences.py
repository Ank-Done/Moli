#!/usr/bin/env python3
"""
Diagnostic script to identify differences between current query and expected results

This script analyzes the database structure and data to understand why the current
query results are significantly different from the reference data.
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import DatabaseConfig

def print_header():
    """Print diagnostic header"""
    print("=" * 80)
    print("SQL Query Diagnostic Script")
    print("=" * 80)
    print(f"Analysis run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def analyze_raw_movements(db):
    """Analyze raw movement data for January 2018"""
    print("1. ANALYZING RAW MOVEMENTS DATA FOR JANUARY 2018")
    print("-" * 60)
    
    query = """
    SELECT 
        COUNT(*) as TotalMovements,
        SUM(m.CUNIDADES) as TotalUnits,
        MIN(m.CFECHA) as MinDate,
        MAX(m.CFECHA) as MaxDate
    FROM admMovimientos m
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
    """
    
    df = db.execute_query(query)
    print("Raw movements in Jan 2018:")
    print(df.to_string(index=False))
    print()

def analyze_document_types(db):
    """Analyze different document types"""
    print("2. ANALYZING DOCUMENT TYPES")
    print("-" * 60)
    
    query = """
    SELECT 
        m.CIDDOCUMENTODE,
        dm.CNOMBREDOCUMENTO,
        dm.CMODULO,
        COUNT(*) as MovementCount,
        SUM(m.CUNIDADES) as TotalUnits
    FROM admMovimientos m
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
    GROUP BY m.CIDDOCUMENTODE, dm.CNOMBREDOCUMENTO, dm.CMODULO
    ORDER BY MovementCount DESC
    """
    
    df = db.execute_query(query)
    print("Document types in Jan 2018:")
    print(df.to_string(index=False))
    print()

def analyze_product_filtering(db):
    """Analyze which products are being included/excluded"""
    print("3. ANALYZING PRODUCT FILTERING")
    print("-" * 60)
    
    # Check products in valid list vs all products
    query = """
    SELECT 
        'In PRODUCTOS_VALIDOS' as ProductGroup,
        COUNT(DISTINCT p.CCODIGOPRODUCTO) as ProductCount,
        COUNT(*) as MovementCount,
        SUM(m.CUNIDADES) as TotalUnits
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
        AND p.CCODIGOPRODUCTO IN (
            'MESCO25', 'MESCO30', 'MESPU07', 'MREGR26', 'MREGR30', 'MREP613', 'MREP614', 'MREP620',
            'PAL0007', 'PAL0008', 'PAL0009', 'PBSMZ04', 'PBSMZ05', 'PBSMZ06', 'PBSMZ08', 'PBSMZ09',
            'PBSMZ11', 'PBSMZ14', 'PCAGF02', 'PCAGF03', 'PCAGF04', 'PCFAI03', 'PCFAM03', 'PCFAZ03'
        )
    
    UNION ALL
    
    SELECT 
        'All Products' as ProductGroup,
        COUNT(DISTINCT p.CCODIGOPRODUCTO) as ProductCount,
        COUNT(*) as MovementCount,
        SUM(m.CUNIDADES) as TotalUnits
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
    """
    
    df = db.execute_query(query)
    print("Product filtering impact:")
    print(df.to_string(index=False))
    print()

def analyze_excluded_products(db):
    """Analyze products excluded by CIDDOCUMENTODE = 5 or 6"""
    print("4. ANALYZING EXCLUDED PRODUCTS")
    print("-" * 60)
    
    query = """
    SELECT 
        'Products with CIDDOCUMENTODE=5' as ExclusionType,
        COUNT(DISTINCT p.CCODIGOPRODUCTO) as ProductCount
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    WHERE m.CIDDOCUMENTODE = 5
    
    UNION ALL
    
    SELECT 
        'Products with CIDDOCUMENTODE=6' as ExclusionType,
        COUNT(DISTINCT p.CCODIGOPRODUCTO) as ProductCount
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    WHERE m.CIDDOCUMENTODE = 6
    """
    
    df = db.execute_query(query)
    print("Excluded products:")
    print(df.to_string(index=False))
    print()

def analyze_weight_calculations(db):
    """Analyze how weight calculations are working"""
    print("5. ANALYZING WEIGHT CALCULATIONS")
    print("-" * 60)
    
    query = """
    SELECT TOP 10
        p.CCODIGOPRODUCTO,
        p.CNOMBREPRODUCTO,
        m.CUNIDADES,
        CASE
            WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
            WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
            WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
            WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
            WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
            ELSE 0
        END AS CalculatedKilos
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
        AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
    ORDER BY m.CUNIDADES DESC
    """
    
    df = db.execute_query(query)
    print("Weight calculation examples:")
    print(df.to_string(index=False))
    print()

def run_simplified_query(db):
    """Run a simplified version of the query without exclusions"""
    print("6. RUNNING SIMPLIFIED QUERY WITHOUT EXCLUSIONS")
    print("-" * 60)
    
    query = """
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        COUNT(*) as MovementCount,
        COUNT(DISTINCT p.CCODIGOPRODUCTO) as ProductCount,
        SUM(m.CUNIDADES) as TotalUnits,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) AS KilosTotales
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    WHERE
        YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) IN (1, 2)
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    df = db.execute_query(query)
    print("Simplified query results (no filters):")
    print(df.to_string(index=False))
    print()

def run_with_document_filter(db):
    """Run query with document type filtering"""
    print("7. RUNNING QUERY WITH DOCUMENT TYPE FILTERING")
    print("-" * 60)
    
    query = """
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        COUNT(*) as MovementCount,
        SUM(m.CUNIDADES) as TotalUnits,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) AS KilosTotales
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN
        admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE
        YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) IN (1, 2)
        AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
        AND dm.CMODULO = 1
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    df = db.execute_query(query)
    print("With document type filtering:")
    print(df.to_string(index=False))
    print()

def suggest_fixes():
    """Suggest potential fixes for the discrepancies"""
    print("8. SUGGESTED FIXES")
    print("-" * 60)
    print("Based on the analysis, here are potential issues and fixes:")
    print()
    print("POTENTIAL ISSUES:")
    print("1. Product filtering too restrictive")
    print("   - The PRODUCTOS_VALIDOS list may not include all relevant products")
    print("   - Reference data might include products not in the current filter")
    print()
    print("2. Document type filtering")
    print("   - Current query only includes CIDDOCUMENTODE = 3 or 4")
    print("   - Reference data might include other document types")
    print()
    print("3. Module filtering") 
    print("   - Query filters for CMODULO = 1 only")
    print("   - Reference data might include other modules")
    print()
    print("4. Product exclusion rules")
    print("   - Products are excluded if they have any movements with CIDDOCUMENTODE = 5 or 6")
    print("   - This might be too aggressive and exclude valid products")
    print()
    print("5. Weight calculation patterns")
    print("   - Product name patterns in CASE statements might not match all variations")
    print("   - Some products might be falling into ELSE 0 case")
    print()
    print("RECOMMENDED ACTIONS:")
    print("1. Compare the PRODUCTOS_VALIDOS list with products in reference data")
    print("2. Check if reference data includes other document types (not just 3,4)")
    print("3. Verify if module filtering (CMODULO = 1) should be removed")
    print("4. Review product exclusion logic - maybe exclude by individual movements not entire products")
    print("5. Add logging to see which products fall into ELSE 0 case")
    print("6. Check if there are products with different naming patterns")

def main():
    """Main diagnostic function"""
    print_header()
    
    try:
        db = DatabaseConfig()
        
        # Run all diagnostic queries
        analyze_raw_movements(db)
        analyze_document_types(db)
        analyze_product_filtering(db)
        analyze_excluded_products(db)
        analyze_weight_calculations(db)
        run_simplified_query(db)
        run_with_document_filter(db)
        
        suggest_fixes()
        
        print("\n" + "=" * 80)
        print("DIAGNOSTIC COMPLETED")
        print("=" * 80)
        print("Review the analysis above to identify the root cause of discrepancies.")
        
    except Exception as e:
        print(f"❌ Error running diagnostic: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()