#!/usr/bin/env python3
"""
Explore admOLIENDAS_Y_ALIMENTO database
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=admOLIENDAS_Y_ALIMENTO;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Explorando base de datos admOLIENDAS_Y_ALIMENTO...")
print("=" * 70)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Get all tables
    print("\n📋 TABLAS DISPONIBLES:")
    cursor.execute("""
        SELECT TABLE_NAME, TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    
    tables = cursor.fetchall()
    for table in tables:
        print(f"   • {table[0]}")
    
    # Check specific tables for sales/agents/categories
    relevant_tables = ['admMovimientos', 'admAgentes', 'admClientes', 'admProductos', 'admConceptos']
    
    for table_name in relevant_tables:
        print(f"\n📊 ESTRUCTURA DE {table_name}:")
        try:
            cursor.execute(f"""
                SELECT TOP 3 COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
                
            # Sample data
            print(f"\n📝 MUESTRA DE DATOS DE {table_name}:")
            cursor.execute(f"SELECT TOP 3 * FROM {table_name}")
            sample_data = cursor.fetchall()
            print(f"   Registros encontrados: {len(sample_data)}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Check admMovimientos for sales data
    print(f"\n💰 ANÁLISIS DE admMovimientos:")
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_movimientos,
                MIN(CFECHA) as fecha_minima,
                MAX(CFECHA) as fecha_maxima,
                COUNT(DISTINCT CIDCONCEPTO) as conceptos_unicos,
                COUNT(DISTINCT CIDAGENTE) as agentes_unicos,
                COUNT(DISTINCT CIDCLIENTE) as clientes_unicos
            FROM admMovimientos
        """)
        
        stats = cursor.fetchone()
        print(f"   • Total movimientos: {stats[0]}")
        print(f"   • Fecha mínima: {stats[1]}")
        print(f"   • Fecha máxima: {stats[2]}")
        print(f"   • Conceptos únicos: {stats[3]}")
        print(f"   • Agentes únicos: {stats[4]}")
        print(f"   • Clientes únicos: {stats[5]}")
        
        # Check by year
        print(f"\n📅 MOVIMIENTOS POR AÑO:")
        cursor.execute("""
            SELECT 
                YEAR(CFECHA) as año,
                COUNT(*) as movimientos,
                SUM(CTOTAL) as total_importe
            FROM admMovimientos
            GROUP BY YEAR(CFECHA)
            ORDER BY año DESC
        """)
        
        years = cursor.fetchall()
        for year in years:
            print(f"   • {year[0]}: {year[1]} movimientos - ${year[2]:,.2f}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check admAgentes
    print(f"\n👤 ANÁLISIS DE admAgentes:")
    try:
        cursor.execute("""
            SELECT TOP 10
                CCODIGOAGENTE,
                CNOMBREAGENTE,
                CTIPO
            FROM admAgentes
            WHERE CESTATUS = 1
        """)
        
        agents = cursor.fetchall()
        print(f"   Agentes encontrados: {len(agents)}")
        for agent in agents:
            print(f"   • {agent[0]} - {agent[1]} - Tipo: {agent[2]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check admConceptos
    print(f"\n📋 ANÁLISIS DE admConceptos:")
    try:
        cursor.execute("""
            SELECT TOP 10
                CCODIGOCONCEPTO,
                CNOMBRECONCEPTO,
                CTIPO
            FROM admConceptos
            WHERE CESTATUS = 1
        """)
        
        concepts = cursor.fetchall()
        print(f"   Conceptos encontrados: {len(concepts)}")
        for concept in concepts:
            print(f"   • {concept[0]} - {concept[1]} - Tipo: {concept[2]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ EXPLORACIÓN COMPLETADA")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Intentando explorar otra base de datos...")
    
    # Try different database name
    try:
        connection_string2 = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=admOLIENDAS_Y_ALIMENTOS;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"
        conn2 = pyodbc.connect(connection_string2)
        cursor2 = conn2.cursor()
        
        print("\n🔍 Explorando admOLIENDAS_Y_ALIMENTOS...")
        cursor2.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        table_count = cursor2.fetchone()[0]
        print(f"   Tablas encontradas: {table_count}")
        
        cursor2.close()
        conn2.close()
        
    except Exception as e2:
        print(f"❌ Error en segunda DB: {e2}")
        print("Usando la base de datos Cyberia para implementar gráficas...")