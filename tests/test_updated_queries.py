#!/usr/bin/env python3
"""
Test updated queries with correct column names
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Probando consultas actualizadas...")
print("=" * 60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Consulta de métricas del dashboard
    print("\n📊 MÉTRICAS DEL DASHBOARD:")
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT p.ProductID) as total_products,
            COALESCE(SUM(CASE WHEN MONTH(so.OrderDate) = 7 AND YEAR(so.OrderDate) = 2024 THEN sod.LineTotal ELSE 0 END), 0) as current_month_sales,
            COUNT(CASE WHEN MONTH(so.OrderDate) = 7 AND YEAR(so.OrderDate) = 2024 THEN 1 END) as current_month_orders,
            COALESCE(SUM(CASE WHEN YEAR(so.OrderDate) = 2024 THEN sod.LineTotal ELSE 0 END), 0) as ytd_sales,
            COALESCE(AVG(CASE WHEN MONTH(so.OrderDate) = 7 AND YEAR(so.OrderDate) = 2024 THEN sod.LineTotal END), 0) as current_avg_order
        FROM Products p
        LEFT JOIN SalesOrderDetails sod ON p.ProductID = sod.ProductID
        LEFT JOIN SalesOrders so ON sod.OrderID = so.OrderID
        WHERE p.IsActive = 1
    """)
    
    metrics = cursor.fetchone()
    print(f"   • Productos Activos: {metrics[0]}")
    print(f"   • Ventas Julio 2024: ${metrics[1]:,.2f}")
    print(f"   • Órdenes Julio 2024: {metrics[2]}")
    print(f"   • Ventas YTD 2024: ${metrics[3]:,.2f}")
    print(f"   • Orden Promedio Julio: ${metrics[4]:,.2f}")
    
    # Consulta de productos
    print("\n📦 TOP 5 PRODUCTOS:")
    cursor.execute("""
        SELECT TOP 5
            p.ProductCode,
            p.ProductName,
            COALESCE(SUM(sod.LineTotal), 0) as total_sales,
            pc.CategoryName
        FROM Products p
        LEFT JOIN SalesOrderDetails sod ON p.ProductID = sod.ProductID
        LEFT JOIN SalesOrders so ON sod.OrderID = so.OrderID AND YEAR(so.OrderDate) = 2024
        LEFT JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
        WHERE p.IsActive = 1
        GROUP BY p.ProductCode, p.ProductName, pc.CategoryName
        ORDER BY total_sales DESC
    """)
    
    products = cursor.fetchall()
    for product in products:
        print(f"   • {product[0]} - {product[1]} [{product[3]}] - ${product[2]:,.2f}")
    
    # Consulta de ventas
    print("\n💰 VENTAS RECIENTES:")
    cursor.execute("""
        SELECT TOP 5
            so.OrderNumber,
            c.CompanyName,
            p.ProductCode + ' - ' + p.ProductName as producto,
            CAST(sod.Quantity as VARCHAR) + ' ' + COALESCE(um.UnitName, 'Unidad') as cantidad,
            sod.UnitPrice,
            sod.LineTotal,
            so.Status
        FROM SalesOrders so
        INNER JOIN SalesOrderDetails sod ON so.OrderID = sod.OrderID
        INNER JOIN Products p ON sod.ProductID = p.ProductID
        INNER JOIN Customers c ON so.CustomerID = c.CustomerID
        LEFT JOIN UnitsOfMeasure um ON p.UnitOfMeasureID = um.UnitOfMeasureID
        WHERE YEAR(so.OrderDate) = 2024
        ORDER BY so.OrderDate DESC
    """)
    
    sales = cursor.fetchall()
    for sale in sales:
        print(f"   • {sale[0]} - {sale[1]} - {sale[2]} - {sale[3]} - ${sale[4]:,.2f} - ${sale[5]:,.2f} - {sale[6]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ TODAS LAS CONSULTAS ACTUALIZADAS FUNCIONAN")
    
except Exception as e:
    print(f"❌ Error: {e}")