#!/usr/bin/env python3
"""
Explore real columns in admOLIENDAS_Y_ALIMENTO
"""
import pyodbc

connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=admOLIENDAS_Y_ALIMENTO;UID=SA;PWD=Mar120305!;TrustServerCertificate=yes"

print("🔍 Explorando columnas reales...")
print("=" * 60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Explore admMovimientos columns
    print("\n📊 COLUMNAS COMPLETAS DE admMovimientos:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'admMovimientos'
        ORDER BY ORDINAL_POSITION
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    # Sample data from admMovimientos
    print(f"\n📝 MUESTRA DE DATOS admMovimientos:")
    cursor.execute("SELECT TOP 5 * FROM admMovimientos")
    sample_data = cursor.fetchall()
    print(f"   Total registros: {len(sample_data)}")
    
    # Check for date columns
    date_columns = [col[0] for col in columns if 'fecha' in col[0].lower() or 'date' in col[0].lower()]
    print(f"\n📅 COLUMNAS DE FECHA en admMovimientos: {date_columns}")
    
    # Explore admAgentes columns
    print("\n👤 COLUMNAS COMPLETAS DE admAgentes:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'admAgentes'
        ORDER BY ORDINAL_POSITION
    """)
    
    agent_columns = cursor.fetchall()
    for col in agent_columns:
        print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    # Sample agents
    print(f"\n📝 MUESTRA DE AGENTES:")
    cursor.execute("SELECT TOP 5 * FROM admAgentes")
    agents = cursor.fetchall()
    for agent in agents:
        print(f"   • {agent}")
    
    # Explore admConceptos columns
    print("\n📋 COLUMNAS COMPLETAS DE admConceptos:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'admConceptos'
        ORDER BY ORDINAL_POSITION
    """)
    
    concept_columns = cursor.fetchall()
    for col in concept_columns:
        print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    # Sample concepts
    print(f"\n📝 MUESTRA DE CONCEPTOS:")
    cursor.execute("SELECT TOP 5 * FROM admConceptos")
    concepts = cursor.fetchall()
    for concept in concepts:
        print(f"   • {concept}")
    
    # Explore admDocumentos for document types
    print("\n📄 COLUMNAS COMPLETAS DE admDocumentos:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'admDocumentos'
        ORDER BY ORDINAL_POSITION
    """)
    
    doc_columns = cursor.fetchall()
    for col in doc_columns:
        print(f"   • {col[0]} ({col[1]}) - Null: {col[2]}")
    
    # Sample documents
    print(f"\n📝 MUESTRA DE DOCUMENTOS:")
    cursor.execute("SELECT TOP 5 * FROM admDocumentos")
    documents = cursor.fetchall()
    for doc in documents:
        print(f"   • {doc}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ EXPLORACIÓN COMPLETADA")
    
except Exception as e:
    print(f"❌ Error: {e}")