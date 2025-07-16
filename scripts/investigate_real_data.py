#!/usr/bin/env python3
"""
Investigate real data in Cyberia database
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Investigando datos reales en Cyberia...")
print("=" * 60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Check what years have sales data
    print("\n📅 AÑOS CON DATOS DE VENTAS:")
    cursor.execute("""
        SELECT YEAR(OrderDate) as year, COUNT(*) as orders
        FROM SalesOrders
        GROUP BY YEAR(OrderDate)
        ORDER BY year DESC
    """)
    
    years = cursor.fetchall()
    for year in years:
        print(f"   • {year[0]}: {year[1]} órdenes")
    
    # Check products with real prices
    print("\n💰 PRODUCTOS CON PRECIOS REALES:")
    cursor.execute("""
        SELECT TOP 10
            ProductCode,
            ProductName,
            SalePrice,
            CostPrice
        FROM Products
        WHERE IsActive = 1 AND SalePrice > 0
        ORDER BY SalePrice DESC
    """)
    
    products = cursor.fetchall()
    for product in products:
        print(f"   • {product[0]} - {product[1]} - Venta: ${product[2]} - Costo: ${product[3]}")
    
    # Check recent sales (any year)
    print("\n💰 VENTAS MÁS RECIENTES:")
    cursor.execute("""
        SELECT TOP 10
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
        ORDER BY so.OrderDate DESC
    """)
    
    sales = cursor.fetchall()
    for sale in sales:
        print(f"   • {sale[0]} - {sale[1]} - {sale[2]} - {sale[3]} - {sale[4]} - ${sale[5]} - ${sale[6]}")
    
    # Check customers
    print("\n👥 CLIENTES ACTIVOS:")
    cursor.execute("""
        SELECT TOP 10
            CustomerCode,
            CompanyName,
            IsActive
        FROM Customers
        WHERE IsActive = 1
        ORDER BY CustomerCode
    """)
    
    customers = cursor.fetchall()
    for customer in customers:
        print(f"   • {customer[0]} - {customer[1]} - Activo: {customer[2]}")
    
    # Check product categories
    print("\n📂 CATEGORÍAS DE PRODUCTOS:")
    cursor.execute("""
        SELECT CategoryName, COUNT(*) as products
        FROM ProductCategories pc
        INNER JOIN Products p ON pc.CategoryID = p.CategoryID
        WHERE p.IsActive = 1
        GROUP BY CategoryName
        ORDER BY products DESC
    """)
    
    categories = cursor.fetchall()
    for category in categories:
        print(f"   • {category[0]}: {category[1]} productos")
    
    # Check units of measure
    print("\n📏 UNIDADES DE MEDIDA:")
    cursor.execute("""
        SELECT UnitCode, UnitName, COUNT(*) as products
        FROM UnitsOfMeasure um
        INNER JOIN Products p ON um.UnitID = p.UnitOfMeasureID
        WHERE p.IsActive = 1
        GROUP BY UnitCode, UnitName
        ORDER BY products DESC
    """)
    
    units = cursor.fetchall()
    for unit in units:
        print(f"   • {unit[0]} - {unit[1]}: {unit[2]} productos")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")