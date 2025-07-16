#!/usr/bin/env python3
"""
Test corrected queries
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Probando consultas corregidas...")
print("=" * 60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Test products query
    print("\n📦 PRODUCTOS CON PRECIOS REALES:")
    cursor.execute("""
        SELECT TOP 10
            p.ProductID,
            p.ProductCode,
            p.ProductName,
            pc.CategoryName,
            um.UnitName,
            p.SalePrice,
            p.IsActive,
            COALESCE(SUM(sod.Quantity), 0) as total_quantity,
            COALESCE(SUM(sod.LineTotal), 0) as total_sales
        FROM Products p
        LEFT JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
        LEFT JOIN UnitsOfMeasure um ON p.UnitOfMeasureID = um.UnitID
        LEFT JOIN SalesOrderDetails sod ON p.ProductID = sod.ProductID
        LEFT JOIN SalesOrders so ON sod.OrderID = so.OrderID AND YEAR(so.OrderDate) >= 2020
        WHERE p.IsActive = 1 AND p.ProductCode NOT LIKE '(Ninguno)%' AND p.SalePrice > 0
        GROUP BY p.ProductID, p.ProductCode, p.ProductName, pc.CategoryName, um.UnitName, p.SalePrice, p.IsActive
        ORDER BY total_sales DESC
    """)
    
    products = cursor.fetchall()
    print(f"   Productos encontrados: {len(products)}")
    for product in products:
        print(f"   • {product[1]} - {product[2]} - ${product[5]} - Ventas: ${product[8]}")
    
    # Test sales query
    print("\n💰 VENTAS REALES:")
    cursor.execute("""
        SELECT TOP 10
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
        LEFT JOIN UnitsOfMeasure um ON p.UnitOfMeasureID = um.UnitID
        WHERE YEAR(so.OrderDate) >= 2020 AND p.ProductCode NOT LIKE '(Ninguno)%'
        ORDER BY so.OrderDate DESC
    """)
    
    sales = cursor.fetchall()
    print(f"   Ventas encontradas: {len(sales)}")
    for sale in sales:
        print(f"   • {sale[0]} - {sale[1]} - {sale[2]} - ${sale[5]}")
    
    # Test dashboard metrics
    print("\n📊 MÉTRICAS DEL DASHBOARD:")
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT p.ProductID) as total_products,
            COALESCE(SUM(CASE WHEN MONTH(so.OrderDate) = 7 AND YEAR(so.OrderDate) = 2025 THEN sod.LineTotal ELSE 0 END), 0) as current_month_sales,
            COUNT(CASE WHEN MONTH(so.OrderDate) = 7 AND YEAR(so.OrderDate) = 2025 THEN 1 END) as current_month_orders,
            COALESCE(SUM(CASE WHEN YEAR(so.OrderDate) = 2025 THEN sod.LineTotal ELSE 0 END), 0) as ytd_sales,
            COALESCE(AVG(CASE WHEN MONTH(so.OrderDate) = 7 AND YEAR(so.OrderDate) = 2025 THEN sod.LineTotal END), 0) as current_avg_order
        FROM Products p
        LEFT JOIN SalesOrderDetails sod ON p.ProductID = sod.ProductID
        LEFT JOIN SalesOrders so ON sod.OrderID = so.OrderID
        WHERE p.IsActive = 1 AND p.ProductCode NOT LIKE '(Ninguno)%'
    """)
    
    metrics = cursor.fetchone()
    print(f"   • Productos Filtrados: {metrics[0]}")
    print(f"   • Ventas Julio 2025: ${metrics[1]:,.2f}")
    print(f"   • Órdenes Julio 2025: {metrics[2]}")
    print(f"   • Ventas YTD 2025: ${metrics[3]:,.2f}")
    print(f"   • Orden Promedio: ${metrics[4]:,.2f}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ CONSULTAS CORREGIDAS FUNCIONAN")
    
except Exception as e:
    print(f"❌ Error: {e}")