#!/usr/bin/env python3
"""
Test connection to Cyberia database specifically
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Probando conexión a Cyberia...")
print("=" * 50)

try:
    conn = pyodbc.connect(connection_string)
    print("✅ CONEXIÓN EXITOSA a Cyberia")
    
    cursor = conn.cursor()
    
    # Verificar tablas disponibles
    print("\n📋 Tablas disponibles:")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"   • {table[0]}")
    
    # Verificar si existen las tablas que necesitamos
    required_tables = ['productos', 'ventas', 'clientes', 'categorias']
    print(f"\n🔍 Verificando tablas requeridas: {required_tables}")
    
    for table in required_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table}: {count} registros")
        except Exception as e:
            print(f"   ❌ {table}: {e}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Sugerencias:")
    print("   • Verifica que SQL Server esté corriendo")
    print("   • Verifica que la base de datos 'Cyberia' exista")
    print("   • Verifica que el usuario 'SA' tenga permisos")
    print("   • Verifica que el servidor esté en 'localhost'")