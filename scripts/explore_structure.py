#!/usr/bin/env python3
"""
Explore real database structure
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Explorando estructura de la base de datos...")
print("=" * 60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Explorar estructura de Products
    print("\n📦 ESTRUCTURA DE TABLA Products:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'Products'
        ORDER BY ORDINAL_POSITION
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    # Explorar estructura de Customers
    print(f"\n👥 ESTRUCTURA DE TABLA Customers:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'Customers'
        ORDER BY ORDINAL_POSITION
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    # Explorar estructura de SalesOrders
    print(f"\n💰 ESTRUCTURA DE TABLA SalesOrders:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'SalesOrders'
        ORDER BY ORDINAL_POSITION
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    # Explorar estructura de SalesOrderDetails
    print(f"\n📋 ESTRUCTURA DE TABLA SalesOrderDetails:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'SalesOrderDetails'
        ORDER BY ORDINAL_POSITION
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    # Explorar estructura de ProductCategories
    print(f"\n📂 ESTRUCTURA DE TABLA ProductCategories:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'ProductCategories'
        ORDER BY ORDINAL_POSITION
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")