#!/usr/bin/env python3
"""
Debug sales joins
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Depurando uniones de ventas...")
print("=" * 60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Check if there are any sales at all
    print("\n💰 VERIFICANDO VENTAS BÁSICAS:")
    cursor.execute("""
        SELECT COUNT(*) as total_sales
        FROM SalesOrders so
        WHERE YEAR(so.OrderDate) >= 2020
    """)
    
    total_sales = cursor.fetchone()[0]
    print(f"   Total de ventas desde 2020: {total_sales}")
    
    # Check SalesOrderDetails
    print("\n💰 VERIFICANDO DETALLES DE VENTAS:")
    cursor.execute("""
        SELECT COUNT(*) as total_details
        FROM SalesOrderDetails
    """)
    
    total_details = cursor.fetchone()[0]
    print(f"   Total de detalles de ventas: {total_details}")
    
    # Check the join between SalesOrders and SalesOrderDetails
    print("\n💰 VERIFICANDO UNIÓN ORDERS-DETAILS:")
    cursor.execute("""
        SELECT COUNT(*) as joined_count
        FROM SalesOrders so
        INNER JOIN SalesOrderDetails sod ON so.OrderID = sod.OrderID
        WHERE YEAR(so.OrderDate) >= 2020
    """)
    
    joined_count = cursor.fetchone()[0]
    print(f"   Registros unidos Orders-Details: {joined_count}")
    
    # Check products in sales
    print("\n💰 VERIFICANDO PRODUCTOS EN VENTAS:")
    cursor.execute("""
        SELECT COUNT(*) as products_in_sales
        FROM SalesOrders so
        INNER JOIN SalesOrderDetails sod ON so.OrderID = sod.OrderID
        INNER JOIN Products p ON sod.ProductID = p.ProductID
        WHERE YEAR(so.OrderDate) >= 2020
    """)
    
    products_in_sales = cursor.fetchone()[0]
    print(f"   Productos en ventas: {products_in_sales}")
    
    # Check what products actually sold
    print("\n💰 PRODUCTOS QUE REALMENTE SE VENDIERON:")
    cursor.execute("""
        SELECT TOP 10
            p.ProductCode,
            p.ProductName,
            COUNT(*) as times_sold,
            SUM(sod.LineTotal) as total_revenue
        FROM SalesOrders so
        INNER JOIN SalesOrderDetails sod ON so.OrderID = sod.OrderID
        INNER JOIN Products p ON sod.ProductID = p.ProductID
        WHERE YEAR(so.OrderDate) >= 2020
        GROUP BY p.ProductCode, p.ProductName
        ORDER BY total_revenue DESC
    """)
    
    sold_products = cursor.fetchall()
    print(f"   Productos vendidos únicos: {len(sold_products)}")
    for product in sold_products:
        print(f"   • {product[0]} - {product[1]} - {product[2]} veces - ${product[3]}")
    
    # Check sample of actual sales records
    print("\n💰 MUESTRA DE REGISTROS DE VENTAS:")
    cursor.execute("""
        SELECT TOP 5
            so.OrderNumber,
            so.OrderDate,
            c.CompanyName,
            p.ProductCode,
            sod.Quantity,
            sod.UnitPrice,
            sod.LineTotal
        FROM SalesOrders so
        INNER JOIN SalesOrderDetails sod ON so.OrderID = sod.OrderID
        INNER JOIN Products p ON sod.ProductID = p.ProductID
        INNER JOIN Customers c ON so.CustomerID = c.CustomerID
        WHERE YEAR(so.OrderDate) >= 2020
        ORDER BY so.OrderDate DESC
    """)
    
    sample_sales = cursor.fetchall()
    for sale in sample_sales:
        print(f"   • {sale[0]} - {sale[1]} - {sale[2]} - {sale[3]} - ${sale[6]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")