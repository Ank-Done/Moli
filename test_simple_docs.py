#!/usr/bin/env python3
"""
Probar diferentes combinaciones de documentos
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.database import DatabaseConfig

def test_documentos():
    db = DatabaseConfig()
    
    # Tu consulta original (SOLO documentos 3 y 4)
    query_original = """
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
        ) AS KilosTotales
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN
        admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE
        (m.CIDDOCUMENTODE = 3 OR m.CIDDOCUMENTODE = 4)
        AND dm.CMODULO = 1
        AND p.CCODIGOPRODUCTO IN (
            'MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620',
            'PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09',
            'PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03',
            'PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03',
            'PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03',
            'PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25',
            'PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01',
            'PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17',
            'PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25',
            'PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607',
            'PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621',
            'MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620',
            'CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI',
            'PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005',
            'CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23',
            'ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010',
            'ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05',
            'RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007'
        )
        AND YEAR(m.CFECHA) IN (2022, 2023, 2024, 2025) 
    GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA)
    ORDER BY Anio, Mes
    """
    
    print("=== PROBANDO SOLO DOCUMENTOS 3 (REMISIÓN) Y 4 (FACTURA) ===")
    df_original = db.execute_query(query_original)
    
    # Mostrar resultados por año para comparar con Excel
    for year in [2022, 2023, 2024, 2025]:
        year_data = df_original[df_original['Anio'] == year]
        total_year = year_data['KilosTotales'].sum()
        print(f"Año {year}: {total_year:,.0f} kilos")
        
        if year == 2022:
            print("  Enero:", year_data[year_data['Mes'] == 1]['KilosTotales'].iloc[0] if len(year_data[year_data['Mes'] == 1]) > 0 else 0)
            print("  Esperado Enero 2022: 5,705,013")
            
    # Datos esperados del Excel para comparar
    esperados_totales = {
        2022: 100141548,
        2023: 119396055,
        2024: 98514360, 
        2025: 42347154
    }
    
    print("\n=== COMPARACIÓN TOTALES POR AÑO ===")
    for year in [2022, 2023, 2024, 2025]:
        year_data = df_original[df_original['Anio'] == year]
        actual = year_data['KilosTotales'].sum()
        esperado = esperados_totales[year]
        diferencia = actual - esperado
        porcentaje = (diferencia / esperado) * 100 if esperado > 0 else 0
        
        print(f"{year}: Actual={actual:,.0f}, Esperado={esperado:,.0f}, Diff={diferencia:,.0f} ({porcentaje:.1f}%)")

if __name__ == "__main__":
    test_documentos()