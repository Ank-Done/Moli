#!/usr/bin/env python3
"""
Crear consulta PIVOT para igualar los datos del Excel
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.database import DatabaseConfig

def test_consulta_pivot():
    db = DatabaseConfig()
    
    # Consulta PIVOT similar al Excel
    query = """
    WITH VentasBase AS (
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
            -- SOLO Remisiones (3) y Facturas (4)
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
        GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA)
    ),
    Devoluciones AS (
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
            ) AS KilosDevueltos
        FROM 
            admMovimientos m
        JOIN 
            admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
        JOIN
            admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
        WHERE
            -- SOLO Devoluciones (5 y 6)
            (m.CIDDOCUMENTODE = 5 OR m.CIDDOCUMENTODE = 6)
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
        GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA)
    )
    SELECT
        CASE 
            WHEN v.Mes = 1 THEN 'Enero'
            WHEN v.Mes = 2 THEN 'Febrero'
            WHEN v.Mes = 3 THEN 'Marzo'
            WHEN v.Mes = 4 THEN 'Abril'
            WHEN v.Mes = 5 THEN 'Mayo'
            WHEN v.Mes = 6 THEN 'Junio'
            WHEN v.Mes = 7 THEN 'Julio'
            WHEN v.Mes = 8 THEN 'Agosto'
            WHEN v.Mes = 9 THEN 'Septiembre'
            WHEN v.Mes = 10 THEN 'Octubre'
            WHEN v.Mes = 11 THEN 'Noviembre'
            WHEN v.Mes = 12 THEN 'Diciembre'
        END AS Mes,
        ISNULL([2022], 0) as [2022],
        ISNULL([2023], 0) as [2023],
        ISNULL([2024], 0) as [2024],
        ISNULL([2025], 0) as [2025],
        ISNULL([2022], 0) + ISNULL([2023], 0) + ISNULL([2024], 0) + ISNULL([2025], 0) as TotalResult
    FROM (
        SELECT 
            v.Mes,
            v.Anio,
            (v.KilosTotales - ISNULL(d.KilosDevueltos, 0)) AS KilosNetos
        FROM VentasBase v
        LEFT JOIN Devoluciones d ON v.Anio = d.Anio AND v.Mes = d.Mes
        WHERE v.Anio IN (2022, 2023, 2024, 2025)
    ) AS SourceTable
    PIVOT (
        SUM(KilosNetos)
        FOR Anio IN ([2022], [2023], [2024], [2025])
    ) AS PivotTable
    ORDER BY 
        CASE 
            WHEN Mes = 'Enero' THEN 1
            WHEN Mes = 'Febrero' THEN 2
            WHEN Mes = 'Marzo' THEN 3
            WHEN Mes = 'Abril' THEN 4
            WHEN Mes = 'Mayo' THEN 5
            WHEN Mes = 'Junio' THEN 6
            WHEN Mes = 'Julio' THEN 7
            WHEN Mes = 'Agosto' THEN 8
            WHEN Mes = 'Septiembre' THEN 9
            WHEN Mes = 'Octubre' THEN 10
            WHEN Mes = 'Noviembre' THEN 11
            WHEN Mes = 'Diciembre' THEN 12
        END
    """
    
    print("=== EJECUTANDO CONSULTA PIVOT PARA IGUALAR EXCEL ===")
    df = db.execute_query(query)
    print(f"Registros obtenidos: {len(df)}")
    
    if len(df) > 0:
        print("\n=== COMPARACIÓN CON TUS DATOS ESPERADOS ===")
        print("Mes\t\t2022\t\t2023\t\t2024\t\t2025\t\tTotal")
        print("-" * 80)
        
        # Datos esperados del Excel
        esperados = {
            'Enero': {'2022': 5705013, '2023': 10863887, '2024': 5912697, '2025': 7690399},
            'Febrero': {'2022': 6895281, '2023': 10354801, '2024': 7700084, '2025': 8410865},
            'Marzo': {'2022': 10389368, '2023': 12475490, '2024': 9570645, '2025': 7774331},
        }
        
        for _, row in df.iterrows():
            mes = row['Mes']
            print(f"{mes:<12}\t{int(row['2022']):<12}\t{int(row['2023']):<12}\t{int(row['2024']):<12}\t{int(row['2025']):<12}\t{int(row['TotalResult'])}")
            
            # Verificar primeros 3 meses
            if mes in esperados:
                esp = esperados[mes]
                actual_2022 = int(row['2022'])
                actual_2023 = int(row['2023']) 
                actual_2024 = int(row['2024'])
                actual_2025 = int(row['2025'])
                
                print(f"  Esperado:\t{esp['2022']:<12}\t{esp['2023']:<12}\t{esp['2024']:<12}\t{esp['2025']:<12}")
                print(f"  Diferencia:\t{actual_2022-esp['2022']:<12}\t{actual_2023-esp['2023']:<12}\t{actual_2024-esp['2024']:<12}\t{actual_2025-esp['2025']:<12}")
                print()

if __name__ == "__main__":
    test_consulta_pivot()