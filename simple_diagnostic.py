#!/usr/bin/env python3
"""
Simple diagnostic script to understand the query discrepancies
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import DatabaseConfig

def main():
    """Main diagnostic function"""
    print("=" * 80)
    print("SIMPLE DIAGNOSTIC: Understanding Query Discrepancies")
    print("=" * 80)
    
    db = DatabaseConfig()
    
    # 1. Check raw movement totals for Jan 2018
    print("1. RAW MOVEMENTS FOR JAN 2018:")
    query1 = """
    SELECT 
        COUNT(*) as TotalMovements,
        SUM(m.CUNIDADES) as TotalUnits
    FROM admMovimientos m
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
    """
    df1 = db.execute_query(query1)
    print(f"   Total movements: {df1.iloc[0]['TotalMovements']:,}")
    print(f"   Total units: {df1.iloc[0]['TotalUnits']:,.2f}")
    print()
    
    # 2. Check with document type filter
    print("2. WITH DOCUMENT TYPE FILTER (3,4):")
    query2 = """
    SELECT 
        COUNT(*) as TotalMovements,
        SUM(m.CUNIDADES) as TotalUnits
    FROM admMovimientos m
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
        AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
    """
    df2 = db.execute_query(query2)
    print(f"   Total movements: {df2.iloc[0]['TotalMovements']:,}")
    print(f"   Total units: {df2.iloc[0]['TotalUnits']:,.2f}")
    print()
    
    # 3. Check with document and module filter
    print("3. WITH DOCUMENT TYPE AND MODULE FILTER:")
    query3 = """
    SELECT 
        COUNT(*) as TotalMovements,
        SUM(m.CUNIDADES) as TotalUnits
    FROM admMovimientos m
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
        AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
        AND dm.CMODULO = 1
    """
    df3 = db.execute_query(query3)
    print(f"   Total movements: {df3.iloc[0]['TotalMovements']:,}")
    print(f"   Total units: {df3.iloc[0]['TotalUnits']:,.2f}")
    print()
    
    # 4. Check with all filters except product filtering
    print("4. WITH ALL FILTERS EXCEPT PRODUCT LIST:")
    query4 = """
    SELECT 
        COUNT(*) as TotalMovements,
        SUM(m.CUNIDADES) as TotalUnits,
        SUM(CASE
            WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' THEN m.CUNIDADES * 1
            WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' THEN m.CUNIDADES * 25
            WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' THEN m.CUNIDADES * 50
            WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
            WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
            WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
            WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
            WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
            WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
            WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
            ELSE 0
        END) as KilosCalculated
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
        AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
        AND dm.CMODULO = 1
    """
    df4 = db.execute_query(query4)
    print(f"   Total movements: {df4.iloc[0]['TotalMovements']:,}")
    print(f"   Total units: {df4.iloc[0]['TotalUnits']:,.2f}")
    print(f"   Calculated kilos: {df4.iloc[0]['KilosCalculated']:,.2f}")
    print()
    
    # 5. Show top products by volume in Jan 2018
    print("5. TOP 10 PRODUCTS BY UNITS IN JAN 2018:")
    query5 = """
    SELECT TOP 10
        p.CCODIGOPRODUCTO,
        p.CNOMBREPRODUCTO,
        SUM(m.CUNIDADES) as TotalUnits,
        COUNT(*) as Movements
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE YEAR(m.CFECHA) = 2018 AND MONTH(m.CFECHA) = 1
        AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
        AND dm.CMODULO = 1
    GROUP BY p.CCODIGOPRODUCTO, p.CNOMBREPRODUCTO
    ORDER BY TotalUnits DESC
    """
    df5 = db.execute_query(query5)
    for _, row in df5.iterrows():
        print(f"   {row['CCODIGOPRODUCTO']:10} | {row['TotalUnits']:10,.0f} units | {row['CNOMBREPRODUCTO'][:50]}")
    print()
    
    # 6. Check how many of the top products are in PRODUCTOS_VALIDOS
    print("6. CHECKING IF TOP PRODUCTS ARE IN PRODUCTOS_VALIDOS LIST:")
    from config.database import PRODUCTOS_VALIDOS
    
    for _, row in df5.head(10).iterrows():
        codigo = row['CCODIGOPRODUCTO'].strip()
        status = "✅ INCLUDED" if codigo in PRODUCTOS_VALIDOS else "❌ EXCLUDED"
        print(f"   {codigo:10} | {status}")
    print()
    
    # 7. Run the exact current query for comparison
    print("7. CURRENT QUERY RESULT FOR JAN 2018:")
    from app.models.reportes import ReporteVentas
    from datetime import date
    
    reporte = ReporteVentas()
    df_current = reporte.get_ventas_por_periodo(date(2018, 1, 1), date(2018, 1, 31))
    
    if not df_current.empty:
        jan_2018 = df_current[(df_current['Anio'] == 2018) & (df_current['Mes'] == 1)]
        if not jan_2018.empty:
            print(f"   Current query result: {jan_2018.iloc[0]['KilosTotales']:,.2f} kg")
        else:
            print("   No data found for Jan 2018 in current query")
    else:
        print("   Current query returned no data")
    
    print()
    print("=" * 80)
    print("ANALYSIS SUMMARY:")
    print("=" * 80)
    print("The huge discrepancy suggests one or more of these issues:")
    print("1. Product filtering is too restrictive (excluding major products)")
    print("2. Weight calculation patterns don't match actual product names")
    print("3. Product exclusion rules are removing too many products")
    print("4. There might be different document types in the reference data")
    print()
    print("NEXT STEPS:")
    print("1. Check if major volume products are included in PRODUCTOS_VALIDOS")
    print("2. Verify weight calculation patterns match product naming")
    print("3. Consider removing or modifying product exclusion rules")
    print("4. Compare document types between current query and reference source")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()