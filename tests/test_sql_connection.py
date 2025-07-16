#!/usr/bin/env python3
"""
Test SQL Server connection with different configurations
"""
import pyodbc
import sys

# Configuraciones a probar
configs = [
    {
        'name': 'FreeTDS',
        'connection_string': "DRIVER={FreeTDS};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!"
    },
    {
        'name': 'ODBC Driver 17',
        'connection_string': "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!"
    },
    {
        'name': 'SQL Server',
        'connection_string': "DRIVER={SQL Server};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!"
    },
    {
        'name': 'SQL Server Native Client',
        'connection_string': "DRIVER={SQL Server Native Client 11.0};SERVER=localhost;DATABASE=Cyberia;UID=SA;PWD=Mar120305!"
    }
]

print("🔍 Probando conexiones a SQL Server...")
print("=" * 50)

for config in configs:
    print(f"\n📋 Probando {config['name']}...")
    try:
        conn = pyodbc.connect(config['connection_string'])
        print(f"✅ {config['name']}: CONEXIÓN EXITOSA")
        
        # Probar una consulta simple
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        print(f"   📊 Versión: {version[0][:50]}...")
        
        # Verificar tablas
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        table_count = cursor.fetchone()
        print(f"   📋 Tablas encontradas: {table_count[0]}")
        
        cursor.close()
        conn.close()
        
        # Si llegamos aquí, esta configuración funciona
        print(f"🎯 USAR ESTA CONFIGURACIÓN: {config['name']}")
        break
        
    except Exception as e:
        print(f"❌ {config['name']}: {e}")

print("\n" + "=" * 50)
print("🔧 Drivers disponibles:")
for driver in pyodbc.drivers():
    print(f"   • {driver}")