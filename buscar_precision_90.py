#!/usr/bin/env python3
"""
Buscar combinaciones que logren 90%+ de precisión
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.database import DatabaseConfig

def buscar_precision_90():
    db = DatabaseConfig()
    
    # Consulta base flexible
    consulta_base = """
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
        p.CCODIGOPRODUCTO IN {productos}
        AND dm.CMODULO = 1
        {condicion_documentos}
        {filtros_adicionales}
    GROUP BY 
        YEAR(m.CFECHA),
        MONTH(m.CFECHA)
    ORDER BY 
        Anio,
        Mes
    """
    
    productos_lista = """(('MESCO25'),
    ('MESCO30'),
    ('MESPU07'),
    ('MREGR26'),
    ('MREGR30'),
    ('MREP613'),
    ('MREP614'),
    ('MREP620'),
    ('PAL0007'),
    ('PAL0008'),
    ('PAL0009'),
    ('PBSMZ04'),
    ('PBSMZ05'),
    ('PBSMZ06'),
    ('PBSMZ08'),
    ('PBSMZ09'),
    ('PBSMZ11'),
    ('PBSMZ14'),
    ('PCAGF02'),
    ('PCAGF03'),
    ('PCAGF04'),
    ('PCFAI03'),
    ('PCFAM03'),
    ('PCFAZ03'),
    ('PCFMO03'),
    ('PCFMO05'),
    ('PCFNA03'),
    ('PCFNE03'),
    ('PCFRS03'),
    ('PCFVA03'),
    ('PCFVE03'),
    ('PCFVI03'),
    ('PCFVL03'),
    ('PCGAI03'),
    ('PCGAM03'),
    ('PCGAZ03'),
    ('PCGMO03'),
    ('PCGNA03'),
    ('PCGNE03'),
    ('PCGRF03'),
    ('PCGRO03'),
    ('PCGRS03'),
    ('PCGVA03'),
    ('PCGVE03'),
    ('PCGVI03'),
    ('PCGVL01'),
    ('PCGVL03'),
    ('PESCO25'),
    ('PESEM17'),
    ('PESGR07'),
    ('PESGR10'),
    ('PESGR21'),
    ('PESGR22'),
    ('PESP607'),
    ('PESP610'),
    ('PG3EN01'),
    ('PG3EN08'),
    ('PM5EN04'),
    ('PREBS07'),
    ('PRECE01'),
    ('PRECE02'),
    ('PRECS01'),
    ('PREEF26'),
    ('PREEM17'),
    ('PREFS11'),
    ('PREFS12'),
    ('PREGG12'),
    ('PREGR07'),
    ('PREGR10'),
    ('PREGR23'),
    ('PREGR24'),
    ('PREGR25'),
    ('PRELG02'),
    ('PREMC11'),
    ('PREO407'),
    ('PREP107'),
    ('PREP108'),
    ('PREP112'),
    ('PREP113'),
    ('PREP607'),
    ('PBAR002'),
    ('PCMNE01'),
    ('PREP111'),
    ('PCFVV03'),
    ('MAREGR11'),
    ('RMREP614'),
    ('PESEM11'),
    ('MREP621'),
    ('MREP622'),
    ('RREGR10'),
    ('RPREP607'),
    ('CSER026'),
    ('PREGR27'),
    ('PREGR29'),
    ('PBSMZ22'),
    ('RMREP620'),
    ('CSER208'),
    ('PESEM12'),
    ('AREGR10'),
    ('AE1GR01'),
    ('AR1GR10'),
    ('ABEGR01'),
    ('PBAR003'),
    ('MAM5ESCNI'),
    ('PESGG12'),
    ('RPREBS07'),
    ('RPBSMZ08'),
    ('PRECCN2'),
    ('MGSMDLZ'),
    ('ZTAR003'),
    ('ZTAR004'),
    ('ZTAR005'),
    ('CSER209'),
    ('MGL01'),
    ('PREEF27'),
    ('FEUR10'),
    ('JS109'),
    ('EX45'),
    ('SEÑ1600'),
    ('PCGEAZ1'),
    ('MREGR23'),
    ('ZEMP006'),
    ('MAREGR15'),
    ('PESCO40'),
    ('PPIL001'),
    ('ZBES010'),
    ('ZBES005'),
    ('ZBESM907'),
    ('ZBRE010'),
    ('ZBRE005'),
    ('PPIL002'),
    ('PPIL003'),
    ('ZSAC004'),
    ('MAM5CESGR2'),
    ('RSERMAQ04'),
    ('RSERMAQ05'),
    ('RSERMAQ06'),
    ('PILCJA01'),
    ('PILCJA02'),
    ('FLSER001'),
    ('LBACE01'),
    ('ZEDU007'))"""

    # Datos objetivo
    objetivo = {
        1: 30171996, 2: 33361032, 3: 40209833, 4: 37833346, 5: 34543474, 6: 26346728,
        7: 25033047, 8: 29797605, 9: 26659536, 10: 27055758, 11: 27674870, 12: 21711893
    }

    # Nuevas combinaciones avanzadas
    combinaciones_avanzadas = [
        {
            'nombre': 'FACTURAS + REMISIONES (3,4)',
            'condicion': 'AND (m.CIDDOCUMENTODE = 3 OR m.CIDDOCUMENTODE = 4)',
            'filtros': ''
        },
        {
            'nombre': 'FACTURAS - NOTAS CREDITO',
            'condicion': 'AND m.CIDDOCUMENTODE = 4',
            'filtros': '''AND p.CCODIGOPRODUCTO NOT IN (
                SELECT DISTINCT p2.CCODIGOPRODUCTO
                FROM admMovimientos m2
                JOIN admProductos p2 ON m2.CIDPRODUCTO = p2.CIDPRODUCTO
                WHERE m2.CIDDOCUMENTODE = 7
            )'''
        },
        {
            'nombre': 'FACTURAS con FECHAS ESPECIFICAS',
            'condicion': 'AND m.CIDDOCUMENTODE = 4',
            'filtros': "AND m.CFECHA >= '2022-01-01'"
        },
        {
            'nombre': 'FACTURAS + NOTAS VENTA - CREDITOS',
            'condicion': 'AND (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 35)',
            'filtros': '''AND p.CCODIGOPRODUCTO NOT IN (
                SELECT DISTINCT p2.CCODIGOPRODUCTO
                FROM admMovimientos m2
                JOIN admProductos p2 ON m2.CIDPRODUCTO = p2.CIDPRODUCTO
                WHERE m2.CIDDOCUMENTODE IN (7, 22)
            )'''
        },
        {
            'nombre': 'VENTAS SIN DEVOLUCIONES AMPLIADAS',
            'condicion': 'AND (m.CIDDOCUMENTODE IN (3, 4, 35))',
            'filtros': '''AND p.CCODIGOPRODUCTO NOT IN (
                SELECT DISTINCT p2.CCODIGOPRODUCTO
                FROM admMovimientos m2
                JOIN admProductos p2 ON m2.CIDPRODUCTO = p2.CIDPRODUCTO
                WHERE m2.CIDDOCUMENTODE IN (5, 6, 7, 20, 21, 22, 36)
            )'''
        },
        {
            'nombre': 'SOLO MOVIMIENTOS POSITIVOS',
            'condicion': 'AND m.CIDDOCUMENTODE = 4',
            'filtros': 'AND m.CUNIDADES > 0'
        },
        {
            'nombre': 'FACTURAS SIN SERVICIOS MAQUILA',
            'condicion': 'AND m.CIDDOCUMENTODE = 4',
            'filtros': "AND p.CCODIGOPRODUCTO NOT LIKE '%RSERMAQ%' AND p.CCODIGOPRODUCTO NOT LIKE '%MAQUILA%'"
        },
        {
            'nombre': 'COMBINACION BALANCEADA (F+R-D)',
            'condicion': 'AND (m.CIDDOCUMENTODE = 3 OR m.CIDDOCUMENTODE = 4)',
            'filtros': '''AND p.CCODIGOPRODUCTO NOT IN (
                SELECT DISTINCT p2.CCODIGOPRODUCTO
                FROM admMovimientos m2
                JOIN admProductos p2 ON m2.CIDPRODUCTO = p2.CIDPRODUCTO
                WHERE m2.CIDDOCUMENTODE IN (5, 6, 7)
            )'''
        }
    ]

    print("=== BÚSQUEDA DE 90%+ PRECISIÓN ===\n")
    
    mejor_precision = 0
    mejor_combo = None
    
    for combo in combinaciones_avanzadas:
        print(f"🧪 {combo['nombre']}")
        
        query = consulta_base.format(
            productos=productos_lista,
            condicion_documentos=combo['condicion'],
            filtros_adicionales=combo['filtros']
        )
        
        try:
            df = db.execute_query(query)
            
            # Filtrar 2022-2025
            df_filtrado = df[df['Anio'].isin([2022, 2023, 2024, 2025])]
            
            if df_filtrado.empty:
                print("   ❌ Sin datos para 2022-2025\n")
                continue
                
            total_por_mes = df_filtrado.groupby('Mes')['KilosTotales'].sum().to_dict()
            
            total_error = 0
            total_esperado = sum(objetivo.values())
            
            for mes in range(1, 13):
                obtenido = int(total_por_mes.get(mes, 0))
                esperado = objetivo[mes]
                error = abs(obtenido - esperado)
                total_error += error
            
            precision = 100 - (total_error/total_esperado*100)
            
            if precision > mejor_precision:
                mejor_precision = precision
                mejor_combo = combo
            
            print(f"   📊 Precisión: {precision:.2f}%")
            print(f"   📈 Error total: {total_error:,} kg")
            
            # Si logramos 90%+, mostrar detalles
            if precision >= 90:
                print("   🎯 ¡OBJETIVO ALCANZADO! Detalles:")
                meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                for mes in range(1, 13):
                    obtenido = int(total_por_mes.get(mes, 0))
                    esperado = objetivo[mes]
                    error = abs(obtenido - esperado) / esperado * 100
                    print(f"      {meses[mes-1]}: {obtenido:,} vs {esperado:,} ({error:.1f}% error)")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    print(f"🏆 MEJOR RESULTADO: {mejor_precision:.2f}% - {mejor_combo['nombre'] if mejor_combo else 'Ninguno'}")

if __name__ == "__main__":
    buscar_precision_90()