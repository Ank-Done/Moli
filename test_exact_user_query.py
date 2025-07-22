#!/usr/bin/env python3
"""
Script para probar la consulta SQL EXACTA del usuario tal como la proporcionó
"""

import pyodbc
import pandas as pd

def test_exact_user_query():
    """Ejecuta la consulta SQL EXACTA del usuario sin cambios"""
    
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
    
    # CONSULTA EXACTA DEL USUARIO - SIN CAMBIOS
    query = """
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%907 KG%' OR p.CNOMBREPRODUCTO LIKE '%2 LBS%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) AS KilosTotales,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) / 1000.0 AS ToneladasTotales
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN
        admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE
        p.CCODIGOPRODUCTO IN ('MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620','PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09','PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03','PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03','PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03','PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25','PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01','PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17','PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25','PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607','PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621','MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620','CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI','PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005','CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23','ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010','ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05','RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007')
        AND m.CIDDOCUMENTODE = 4
        OR m.CIDDOCUMENTODE = 3
        AND dm.CMODULO = 1
        -- Excluir productos que tengan movimientos con CIDDOCUMENTODE = 6
        AND p.CCODIGOPRODUCTO NOT IN (
            SELECT DISTINCT p2.CCODIGOPRODUCTO
            FROM admMovimientos m2
            JOIN admProductos p2 ON m2.CIDPRODUCTO = p2.CIDPRODUCTO
            WHERE m2.CIDDOCUMENTODE = 6
        )
        AND p.CCODIGOPRODUCTO NOT IN (
            SELECT DISTINCT p2.CCODIGOPRODUCTO
            FROM admMovimientos m2
            JOIN admProductos p2 ON m2.CIDPRODUCTO = p2.CIDPRODUCTO
            WHERE m2.CIDDOCUMENTODE = 5
        )
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print("RESULTADOS DE LA CONSULTA EXACTA DEL USUARIO:")
    print("============================================")
    for _, row in df.iterrows():
        print(f"{int(row['Anio'])}\t{int(row['Mes'])}\t{row['KilosTotales']:.6f}\t{row['ToneladasTotales']:.6f}")
    
    print(f"\nTotal de filas: {len(df)}")
    if not df.empty:
        print(f"Rango de años: {df['Anio'].min()} - {df['Anio'].max()}")
    
    # Comparar algunos valores específicos con los datos de referencia
    print("\nCOMPARACIÓN CON DATOS DE REFERENCIA:")
    print("===================================")
    
    # Datos de referencia proporcionados por el usuario (primeros)
    ref_data = [
        (2018, 1, 18901903.948, 18901.903948),
        (2018, 2, 15651880.668, 15651.880668),
        (2018, 3, 16464462.321, 16464.462321),
        (2020, 1, 19847863.427, 19847.863427),
        (2022, 1, 12700020.256, 12700.020256),
        (2024, 1, 6833776.354, 6833.770005)
    ]
    
    for ref_anio, ref_mes, ref_kilos, ref_toneladas in ref_data:
        query_row = df[(df['Anio'] == ref_anio) & (df['Mes'] == ref_mes)]
        if not query_row.empty:
            q_kilos = query_row.iloc[0]['KilosTotales']
            q_toneladas = query_row.iloc[0]['ToneladasTotales']
            
            if ref_kilos > 0:
                precision_kg = (min(ref_kilos, q_kilos) / max(ref_kilos, q_kilos)) * 100
                precision_ton = (min(ref_toneladas, q_toneladas) / max(ref_toneladas, q_toneladas)) * 100
            else:
                precision_kg = precision_ton = 0
                
            print(f"{ref_anio}-{ref_mes:02d}:")
            print(f"  Referencia: {ref_kilos:.2f} kg, {ref_toneladas:.6f} ton")
            print(f"  Query:      {q_kilos:.2f} kg, {q_toneladas:.6f} ton")
            print(f"  Coincidencia: {precision_kg:.2f}% kg, {precision_ton:.2f}% ton")
            if abs(ref_kilos - q_kilos) < 1.0:
                print("  ✓ COINCIDENCIA PERFECTA!")
            print()
        else:
            print(f"{ref_anio}-{ref_mes:02d}: NO ENCONTRADO EN RESULTADOS")
            print()

if __name__ == "__main__":
    test_exact_user_query()