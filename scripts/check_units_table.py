#!/usr/bin/env python3
"""
Check units of measure table structure
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Verificando tabla UnitsOfMeasure...")
print("=" * 60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Check if UnitsOfMeasure table exists
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME LIKE '%Unit%' OR TABLE_NAME LIKE '%Measure%'
    """)
    
    tables = cursor.fetchall()
    print("📋 Tablas relacionadas con unidades:")
    for table in tables:
        print(f"   • {table[0]}")
    
    # Check structure if it exists
    if tables:
        table_name = tables[0][0]  # Use first table found
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        print(f"\n📦 ESTRUCTURA DE {table_name}:")
        for col in columns:
            print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    # Check what columns Products table has for units
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'Products' AND (COLUMN_NAME LIKE '%Unit%' OR COLUMN_NAME LIKE '%Measure%')
    """)
    
    unit_columns = cursor.fetchall()
    print(f"\n📦 COLUMNAS DE UNIDADES EN Products:")
    for col in unit_columns:
        print(f"   • {col[0]}")
    
    # Sample products with available data
    cursor.execute("""
        SELECT TOP 10
            ProductCode,
            ProductName,
            SalePrice,
            IsActive
        FROM Products
        WHERE IsActive = 1 AND ProductCode IS NOT NULL AND ProductCode != ''
        ORDER BY ProductCode
    """)
    
    products = cursor.fetchall()
    print(f"\n📦 PRODUCTOS DE EJEMPLO:")
    for product in products:
        print(f"   • {product[0]} - {product[1]} - ${product[2]} - Activo: {product[3]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")