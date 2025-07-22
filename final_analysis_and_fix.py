#!/usr/bin/env python3
"""
Final Analysis and Fix for SQL Query Discrepancies

This script identifies the exact cause of discrepancies and provides a corrected query.
"""

import sys
import os
import pandas as pd
from datetime import datetime, date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import DatabaseConfig, PRODUCTOS_VALIDOS

def main():
    """Main analysis and fix function"""
    print("=" * 80)
    print("FINAL ANALYSIS: Root Cause and Fix")
    print("=" * 80)
    print(f"Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    db = DatabaseConfig()
    
    print("ISSUE IDENTIFIED:")
    print("-" * 40)
    print("❌ PRODUCTOS_VALIDOS list is missing major volume products!")
    print()
    print("Major missing products (from top 10 by volume in Jan 2018):")
    print("- MREGR27: 354,938 units (25 KG each = 8,873,450 kg)")
    print("- MREGR22: 297,620 units (25 KG each = 7,440,500 kg)")
    print("- PRECS02: 22,000 units (25 KG each = 550,000 kg)")
    print("- PREGR12: 15,000 units (50 KG each = 750,000 kg)")
    print("- PREBS14: 7,500 units (25 KG each = 187,500 kg)")
    print()
    print("This explains why current query shows 126,678 kg vs reference 18,901,904 kg")
    print()
    
    # Get all products that appear in the data
    print("FINDING ALL PRODUCTS IN THE DATABASE:")
    print("-" * 40)
    
    query_all_products = """
    SELECT 
        p.CCODIGOPRODUCTO,
        p.CNOMBREPRODUCTO,
        SUM(m.CUNIDADES) as TotalUnits,
        COUNT(DISTINCT CONCAT(YEAR(m.CFECHA), '-', MONTH(m.CFECHA))) as MonthsActive
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
        AND dm.CMODULO = 1
        AND YEAR(m.CFECHA) BETWEEN 2018 AND 2025
    GROUP BY p.CCODIGOPRODUCTO, p.CNOMBREPRODUCTO
    HAVING SUM(m.CUNIDADES) > 1000  -- Only products with significant volume
    ORDER BY TotalUnits DESC
    """
    
    df_all_products = db.execute_query(query_all_products)
    
    print(f"Found {len(df_all_products)} products with significant volume")
    print()
    print("Top 20 products by total volume (not in current PRODUCTOS_VALIDOS):")
    print("-" * 70)
    
    missing_products = []
    count = 0
    for _, row in df_all_products.iterrows():
        codigo = row['CCODIGOPRODUCTO'].strip()
        if codigo not in PRODUCTOS_VALIDOS:
            missing_products.append(codigo)
            print(f"{count+1:2}. {codigo:10} | {row['TotalUnits']:12,.0f} units | {row['CNOMBREPRODUCTO'][:45]}")
            count += 1
            if count >= 20:
                break
    
    print()
    print("CORRECTED PRODUCTOS_VALIDOS LIST:")
    print("-" * 40)
    print("Here's the expanded list that should be used:")
    print()
    
    # Create expanded product list
    current_products = set(PRODUCTOS_VALIDOS)
    top_missing = missing_products[:30]  # Add top 30 missing products
    expanded_products = sorted(list(current_products.union(set(top_missing))))
    
    print("EXPANDED_PRODUCTOS_VALIDOS = [")
    for i, prod in enumerate(expanded_products):
        if i % 8 == 0:
            print("    ", end="")
        print(f"'{prod}', ", end="")
        if i % 8 == 7 or i == len(expanded_products) - 1:
            print()
    print("]")
    print()
    
    # Test the corrected query
    print("TESTING CORRECTED QUERY:")
    print("-" * 40)
    
    expanded_list_str = "','".join(expanded_products)
    
    corrected_query = f"""
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%907 KG%' OR p.CNOMBREPRODUCTO LIKE '%2 LBS%' THEN m.CUNIDADES * 0.907
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
        ) AS KilosTotales,
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
        ) / 1000.0 AS ToneladasTotales
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
    
    df_corrected = db.execute_query(corrected_query)
    
    print("Corrected query results for Jan-Feb 2018:")
    print("Year\tMonth\tKilosTotales\t\tToneladasTotales")
    print("-" * 60)
    for _, row in df_corrected.iterrows():
        print(f"{int(row['Anio'])}\t{int(row['Mes'])}\t{row['KilosTotales']:,.2f}\t\t{row['ToneladasTotales']:,.6f}")
    
    print()
    print("COMPARISON WITH REFERENCE DATA:")
    print("-" * 40)
    reference_jan = 18901903.948
    reference_feb = 15651880.668
    
    if not df_corrected.empty:
        jan_result = df_corrected[df_corrected['Mes'] == 1]
        feb_result = df_corrected[df_corrected['Mes'] == 2]
        
        if not jan_result.empty:
            jan_actual = jan_result.iloc[0]['KilosTotales']
            jan_diff = abs(jan_actual - reference_jan)
            jan_pct = (jan_diff / reference_jan) * 100
            print(f"January 2018:")
            print(f"  Reference: {reference_jan:,.2f} kg")
            print(f"  Corrected: {jan_actual:,.2f} kg")
            print(f"  Difference: {jan_diff:,.2f} kg ({jan_pct:.1f}%)")
            
        if not feb_result.empty:
            feb_actual = feb_result.iloc[0]['KilosTotales']
            feb_diff = abs(feb_actual - reference_feb)
            feb_pct = (feb_diff / reference_feb) * 100
            print(f"February 2018:")
            print(f"  Reference: {reference_feb:,.2f} kg")
            print(f"  Corrected: {feb_actual:,.2f} kg")
            print(f"  Difference: {feb_diff:,.2f} kg ({feb_pct:.1f}%)")
    
    print()
    print("=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    print("1. UPDATE PRODUCTOS_VALIDOS LIST:")
    print("   - Current list has only 87 products")
    print("   - Expanded list should have ~117 products")
    print("   - This will capture the major volume products that were excluded")
    print()
    print("2. REVIEW PRODUCT EXCLUSION LOGIC:")
    print("   - Consider removing the exclusion of products with CIDDOCUMENTODE = 5 or 6")
    print("   - Or modify to exclude individual movements, not entire products")
    print()
    print("3. VALIDATE WEIGHT CALCULATIONS:")
    print("   - Some products might not match the CASE statement patterns")
    print("   - Consider adding logging to identify products falling into ELSE 0")
    print()
    print("4. TEST WITH FULL EXPANDED LIST:")
    print("   - Replace PRODUCTOS_VALIDOS in database.py with the expanded list above")
    print("   - Re-run the test script to verify results match reference data")
    print()
    
    # Save the expanded list to a file for easy copying
    with open('/home/ank/Documents/FlaskReporteApp/expanded_productos_validos.py', 'w') as f:
        f.write("# Expanded PRODUCTOS_VALIDOS list that includes major volume products\n")
        f.write("# This should replace the current PRODUCTOS_VALIDOS in config/database.py\n\n")
        f.write("EXPANDED_PRODUCTOS_VALIDOS = [\n")
        for i, prod in enumerate(expanded_products):
            if i % 8 == 0:
                f.write("    ")
            f.write(f"'{prod}', ")
            if i % 8 == 7 or i == len(expanded_products) - 1:
                f.write("\n")
        f.write("]\n")
    
    print(f"💾 Expanded product list saved to: /home/ank/Documents/FlaskReporteApp/expanded_productos_validos.py")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()