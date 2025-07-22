#!/usr/bin/env python3
"""
Test alternative calculation methods to match reference data exactly
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import DatabaseConfig

def main():
    """Test different calculation approaches"""
    print("=" * 80)
    print("TESTING ALTERNATIVE CALCULATION METHODS")
    print("=" * 80)
    
    db = DatabaseConfig()
    
    # Load the expanded product list
    try:
        with open('/home/ank/Documents/FlaskReporteApp/expanded_productos_validos.py', 'r') as f:
            content = f.read()
            # Extract product list from the file
            start_marker = "EXPANDED_PRODUCTOS_VALIDOS = ["
            end_marker = "]"
            start_idx = content.find(start_marker) + len(start_marker)
            end_idx = content.find(end_marker, start_idx)
            product_lines = content[start_idx:end_idx].strip()
            
            # Parse products
            products = []
            for line in product_lines.split('\n'):
                line = line.strip()
                if line:
                    # Extract quoted products
                    import re
                    found_products = re.findall(r"'([^']+)'", line)
                    products.extend(found_products)
            
            expanded_products = products
    except:
        print("Could not load expanded product list, using current one")
        from config.database import PRODUCTOS_VALIDOS
        expanded_products = PRODUCTOS_VALIDOS
    
    expanded_list_str = "','".join(expanded_products)
    
    print(f"Testing with {len(expanded_products)} products")
    print()
    
    # Test 1: Check if some movements should be excluded based on direction
    print("TEST 1: Analyzing movement directions and signs")
    print("-" * 50)
    
    query1 = """
    SELECT 
        CASE WHEN m.CUNIDADES > 0 THEN 'Positive' ELSE 'Negative' END as MovementType,
        COUNT(*) as MovementCount,
        SUM(m.CUNIDADES) as TotalUnits,
        AVG(m.CUNIDADES) as AvgUnits
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE p.CCODIGOPRODUCTO IN ('{expanded_list_str}')
        AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
        AND dm.CMODULO = 1
        AND YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
    GROUP BY CASE WHEN m.CUNIDADES > 0 THEN 'Positive' ELSE 'Negative' END
    """
    
    df1 = db.execute_query(query1)
    print("Movement analysis:")
    print(df1.to_string(index=False))
    print()
    
    # Test 2: Try with only positive movements
    print("TEST 2: Using only positive movements")
    print("-" * 50)
    
    query2 = f"""
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
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
        p.CCODIGOPRODUCTO IN ('{expanded_list_str}')
        AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
        AND dm.CMODULO = 1
        AND m.CUNIDADES > 0
        AND YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) IN (1, 2)
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    df2 = db.execute_query(query2)
    print("Results with only positive movements:")
    for _, row in df2.iterrows():
        print(f"{int(row['Anio'])}-{int(row['Mes']):02d}: {row['KilosTotales']:,.2f} kg")
    print()
    
    # Test 3: Try with absolute values
    print("TEST 3: Using absolute values of movements")
    print("-" * 50)
    
    query3 = f"""
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        SUM(
            ABS(
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
            )
        ) / 2 AS KilosTotales
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN
        admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE
        p.CCODIGOPRODUCTO IN ('{expanded_list_str}')
        AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
        AND dm.CMODULO = 1
        AND YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) IN (1, 2)
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    df3 = db.execute_query(query3)
    print("Results with absolute values divided by 2:")
    for _, row in df3.iterrows():
        print(f"{int(row['Anio'])}-{int(row['Mes']):02d}: {row['KilosTotales']:,.2f} kg")
    print()
    
    # Test 4: Check if it's about different document types
    print("TEST 4: Testing with only document type 4 (sales)")
    print("-" * 50)
    
    query4 = f"""
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
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
        p.CCODIGOPRODUCTO IN ('{expanded_list_str}')
        AND m.CIDDOCUMENTODE = 4
        AND dm.CMODULO = 1
        AND YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) IN (1, 2)
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    df4 = db.execute_query(query4)
    print("Results with only document type 4:")
    for _, row in df4.iterrows():
        print(f"{int(row['Anio'])}-{int(row['Mes']):02d}: {row['KilosTotales']:,.2f} kg")
    print()
    
    print("=" * 80)
    print("COMPARISON WITH REFERENCE DATA:")
    print("=" * 80)
    reference_jan = 18901903.948
    reference_feb = 15651880.668
    
    print(f"Reference Jan 2018: {reference_jan:,.2f} kg")
    print(f"Reference Feb 2018: {reference_feb:,.2f} kg")
    print()
    
    tests = [
        ("Current (all movements)", df2 if not df2.empty else None),
        ("Positive only", df2 if not df2.empty else None), 
        ("Absolute / 2", df3 if not df3.empty else None),
        ("Doc type 4 only", df4 if not df4.empty else None)
    ]
    
    for test_name, df in tests:
        if df is not None and not df.empty:
            jan_row = df[df['Mes'] == 1]
            feb_row = df[df['Mes'] == 2]
            
            print(f"{test_name}:")
            if not jan_row.empty:
                jan_val = jan_row.iloc[0]['KilosTotales']
                jan_diff_pct = abs(jan_val - reference_jan) / reference_jan * 100
                print(f"  Jan: {jan_val:,.2f} kg (diff: {jan_diff_pct:.1f}%)")
            if not feb_row.empty:
                feb_val = feb_row.iloc[0]['KilosTotales']
                feb_diff_pct = abs(feb_val - reference_feb) / reference_feb * 100
                print(f"  Feb: {feb_val:,.2f} kg (diff: {feb_diff_pct:.1f}%)")
            print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()