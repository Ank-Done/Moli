#!/usr/bin/env python3
"""
Debug OrderID mismatch
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Depurando problemas de OrderID...")
print("=" * 60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Check sample OrderIDs from SalesOrders
    print("\n📋 SAMPLE OrderIDs en SalesOrders:")
    cursor.execute("""
        SELECT TOP 5 OrderID, OrderNumber, OrderDate
        FROM SalesOrders
        ORDER BY OrderDate DESC
    """)
    
    orders = cursor.fetchall()
    for order in orders:
        print(f"   • OrderID: {order[0]}, OrderNumber: {order[1]}, Date: {order[2]}")
    
    # Check sample OrderIDs from SalesOrderDetails
    print("\n📋 SAMPLE OrderIDs en SalesOrderDetails:")
    cursor.execute("""
        SELECT TOP 5 OrderID, ProductID, Quantity, UnitPrice
        FROM SalesOrderDetails
    """)
    
    details = cursor.fetchall()
    for detail in details:
        print(f"   • OrderID: {detail[0]}, ProductID: {detail[1]}, Quantity: {detail[2]}, Price: {detail[3]}")
    
    # Check for OrderID overlap
    print("\n📋 VERIFICANDO OVERLAP DE OrderIDs:")
    cursor.execute("""
        SELECT COUNT(*) as overlap_count
        FROM SalesOrders so
        INNER JOIN SalesOrderDetails sod ON so.OrderID = sod.OrderID
    """)
    
    overlap = cursor.fetchone()[0]
    print(f"   OrderIDs que coinciden: {overlap}")
    
    # Check min/max OrderIDs in both tables
    print("\n📋 RANGOS DE OrderIDs:")
    cursor.execute("""
        SELECT 
            'SalesOrders' as table_name,
            MIN(OrderID) as min_id,
            MAX(OrderID) as max_id,
            COUNT(*) as record_count
        FROM SalesOrders
        UNION ALL
        SELECT 
            'SalesOrderDetails' as table_name,
            MIN(OrderID) as min_id,
            MAX(OrderID) as max_id,
            COUNT(*) as record_count
        FROM SalesOrderDetails
    """)
    
    ranges = cursor.fetchall()
    for range_info in ranges:
        print(f"   • {range_info[0]}: Min={range_info[1]}, Max={range_info[2]}, Count={range_info[3]}")
    
    # Check if there are other ID columns we should use
    print("\n📋 COLUMNAS DE IDENTIFICACIÓN:")
    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'SalesOrders' AND COLUMN_NAME LIKE '%ID%'
    """)
    
    so_columns = cursor.fetchall()
    print(f"   SalesOrders ID columns: {[col[0] for col in so_columns]}")
    
    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'SalesOrderDetails' AND COLUMN_NAME LIKE '%ID%'
    """)
    
    sod_columns = cursor.fetchall()
    print(f"   SalesOrderDetails ID columns: {[col[0] for col in sod_columns]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")