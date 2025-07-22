#!/usr/bin/env python3
"""
Script para probar los filtros de fecha
"""

import pyodbc
import pandas as pd
from datetime import datetime, date

def test_date_filters():
    """Prueba filtros de fecha"""
    
    # Conexión a la base de datos
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=192.168.1.103;"
        "DATABASE=adMOLIENDAS_Y_ALIMENTO;"
        "UID=sa;"
        "PWD=Mar120305!;"
        "TrustServerCertificate=yes;"
        "Encrypt=no;"
    )
    
    conn = pyodbc.connect(connection_string)
    
    print("=== PRUEBA 1: CONSULTA SIN FILTROS ===")
    query_sin_filtros = """
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        COUNT(*) as TotalRegistros,
        MIN(m.CFECHA) as FechaMinima,
        MAX(m.CFECHA) as FechaMaxima
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN
        admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE
        p.CCODIGOPRODUCTO IN ('MESCO25','MESCO30','MESPU07')
        AND m.CIDDOCUMENTODE = 4
        OR m.CIDDOCUMENTODE = 3
        AND dm.CMODULO = 1
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    df = pd.read_sql(query_sin_filtros, conn)
    print(f"Filas sin filtros: {len(df)}")
    if not df.empty:
        print(f"Años disponibles: {df['Anio'].min()} - {df['Anio'].max()}")
        print("Primeras 5 filas:")
        print(df.head())
    
    print("\n=== PRUEBA 2: CONSULTA CON FILTROS DE FECHA AGREGADOS AL FINAL ===")
    fecha_inicio = date(2022, 1, 1)
    fecha_fin = date(2022, 12, 31)
    
    query_con_filtros_final = f"""
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        COUNT(*) as TotalRegistros,
        MIN(m.CFECHA) as FechaMinima,
        MAX(m.CFECHA) as FechaMaxima
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN
        admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE
        p.CCODIGOPRODUCTO IN ('MESCO25','MESCO30','MESPU07')
        AND m.CIDDOCUMENTODE = 4
        OR m.CIDDOCUMENTODE = 3
        AND dm.CMODULO = 1
        AND m.CFECHA >= '{fecha_inicio}' AND m.CFECHA <= '{fecha_fin}'
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    df2 = pd.read_sql(query_con_filtros_final, conn)
    print(f"Filas con filtros al final: {len(df2)}")
    if not df2.empty:
        print("Resultados:")
        print(df2)
    
    print("\n=== PRUEBA 3: CONSULTA CON FILTROS DE FECHA INTEGRADOS CORRECTAMENTE ===")
    query_con_filtros_integrados = f"""
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        COUNT(*) as TotalRegistros,
        MIN(m.CFECHA) as FechaMinima,
        MAX(m.CFECHA) as FechaMaxima
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN
        admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE
        p.CCODIGOPRODUCTO IN ('MESCO25','MESCO30','MESPU07')
        AND m.CFECHA >= '{fecha_inicio}' AND m.CFECHA <= '{fecha_fin}'
        AND m.CIDDOCUMENTODE = 4
        OR m.CIDDOCUMENTODE = 3
        AND dm.CMODULO = 1
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    df3 = pd.read_sql(query_con_filtros_integrados, conn)
    print(f"Filas con filtros integrados: {len(df3)}")
    if not df3.empty:
        print("Resultados:")
        print(df3)
    
    conn.close()

if __name__ == "__main__":
    test_date_filters()