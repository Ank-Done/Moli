#!/usr/bin/env python3
"""
Test real data from Cyberia database
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Probando consultas reales a Cyberia...")
print("=" * 60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Consulta de productos
    print("\n📦 PRODUCTOS (primeros 10):")
    cursor.execute("""
        SELECT TOP 10
            p.CIDPRODUCTO,
            p.CCODIGOPRODUCTO,
            p.CNOMBREPRODUCTO,
            pc.CNOMBRE as categoria,
            p.CPRECIO1
        FROM Products p
        LEFT JOIN ProductCategories pc ON p.CIDCATEGORIA = pc.CIDCATEGORIA
        WHERE p.CESTATUS = 1
        ORDER BY p.CCODIGOPRODUCTO
    """)
    
    products = cursor.fetchall()
    for product in products:
        print(f"   • {product[1]} - {product[2]} [{product[3]}] - ${product[4]}")
    
    # Consulta de clientes
    print(f"\n👥 CLIENTES (primeros 10):")
    cursor.execute("""
        SELECT TOP 10
            CIDCLIENTE,
            CCODIGOCLIENTE,
            CRAZONSOCIAL
        FROM Customers
        WHERE CESTATUS = 1
        ORDER BY CCODIGOCLIENTE
    """)
    
    customers = cursor.fetchall()
    for customer in customers:
        print(f"   • {customer[1]} - {customer[2]}")
    
    # Consulta de ventas
    print(f"\n💰 VENTAS (primeras 10):")
    cursor.execute("""
        SELECT TOP 10
            so.CIDDOCUMENTO,
            c.CRAZONSOCIAL,
            p.CCODIGOPRODUCTO,
            sod.CUNIDADES,
            sod.CPRECIO,
            so.CFECHA
        FROM SalesOrders so
        INNER JOIN SalesOrderDetails sod ON so.CIDDOCUMENTO = sod.CIDDOCUMENTO
        INNER JOIN Products p ON sod.CIDPRODUCTO = p.CIDPRODUCTO
        INNER JOIN Customers c ON so.CIDCLIENTE = c.CIDCLIENTE
        WHERE YEAR(so.CFECHA) = 2024
        ORDER BY so.CFECHA DESC
    """)
    
    sales = cursor.fetchall()
    for sale in sales:
        print(f"   • {sale[0]} - {sale[1]} - {sale[2]} - {sale[3]} unidades - ${sale[4]} - {sale[5]}")
    
    # Consulta de métricas
    print(f"\n📊 MÉTRICAS DEL DASHBOARD:")
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT p.CIDPRODUCTO) as total_products,
            COUNT(DISTINCT c.CIDCLIENTE) as total_customers,
            COALESCE(SUM(CASE WHEN MONTH(so.CFECHA) = 7 AND YEAR(so.CFECHA) = 2024 THEN sod.CPRECIO * sod.CUNIDADES ELSE 0 END), 0) as july_sales,
            COALESCE(SUM(CASE WHEN YEAR(so.CFECHA) = 2024 THEN sod.CPRECIO * sod.CUNIDADES ELSE 0 END), 0) as ytd_sales
        FROM Products p
        CROSS JOIN Customers c
        LEFT JOIN SalesOrderDetails sod ON p.CIDPRODUCTO = sod.CIDPRODUCTO
        LEFT JOIN SalesOrders so ON sod.CIDDOCUMENTO = so.CIDDOCUMENTO
        WHERE p.CESTATUS = 1 AND c.CESTATUS = 1
    """)
    
    metrics = cursor.fetchone()
    print(f"   • Productos Activos: {metrics[0]}")
    print(f"   • Clientes Activos: {metrics[1]}")
    print(f"   • Ventas Julio 2024: ${metrics[2]:,.2f}")
    print(f"   • Ventas YTD 2024: ${metrics[3]:,.2f}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ TODAS LAS CONSULTAS FUNCIONAN CORRECTAMENTE")
    
except Exception as e:
    print(f"❌ Error: {e}")