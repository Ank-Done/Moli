#!/usr/bin/env python3
"""
Probar agregando los productos faltantes más importantes
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.database import DatabaseConfig

def test_productos_faltantes():
    db = DatabaseConfig()
    
    # Productos faltantes importantes identificados
    productos_extra = ['MREGR27', 'MREGR22', 'PREP115', 'PREP118', 'MGSMDLZ', 'RSERMAQ03']
    
    productos_originales = ['MESCO25', 'MESCO30', 'MESPU07', 'MREGR26', 'MREGR30', 'MREP613', 'MREP614', 'MREP620',
    'PAL0007', 'PAL0008', 'PAL0009', 'PBSMZ04', 'PBSMZ05', 'PBSMZ06', 'PBSMZ08', 'PBSMZ09',
    'PBSMZ11', 'PBSMZ14', 'PCAGF02', 'PCAGF03', 'PCAGF04', 'PCFAI03', 'PCFAM03', 'PCFAZ03',
    'PCFMO03', 'PCFMO05', 'PCFNA03', 'PCFNE03', 'PCFRS03', 'PCFVA03', 'PCFVE03', 'PCFVI03',
    'PCFVL03', 'PCGAI03', 'PCGAM03', 'PCGAZ03', 'PCGMO03', 'PCGNA03', 'PCGNE03', 'PCGRF03',
    'PCGRO03', 'PCGRS03', 'PCGVA03', 'PCGVE03', 'PCGVI03', 'PCGVL01', 'PCGVL03', 'PESCO25',
    'PESEM17', 'PESGR07', 'PESGR10', 'PESGR21', 'PESGR22', 'PESP607', 'PESP610', 'PG3EN01',
    'PG3EN08', 'PM5EN04', 'PREBS07', 'PRECE01', 'PRECE02', 'PRECS01', 'PREEF26', 'PREEM17',
    'PREFS11', 'PREFS12', 'PREGG12', 'PREGR07', 'PREGR10', 'PREGR23', 'PREGR24', 'PREGR25',
    'PRELG02', 'PREMC11', 'PREO407', 'PREP107', 'PREP108', 'PREP112', 'PREP113', 'PREP607',
    'PBAR002', 'PCMNE01', 'PREP111', 'PCFVV03', 'MAREGR11', 'RMREP614', 'PESEM11', 'MREP621',
    'MREP622', 'RREGR10', 'RPREP607', 'CSER026', 'PREGR27', 'PREGR29', 'PBSMZ22', 'RMREP620',
    'CSER208', 'PESEM12', 'AREGR10', 'AE1GR01', 'AR1GR10', 'ABEGR01', 'PBAR003', 'MAM5ESCNI',
    'PESGG12', 'RPREBS07', 'RPBSMZ08', 'PRECCN2', 'MGSMDLZ', 'ZTAR003', 'ZTAR004', 'ZTAR005',
    'CSER209', 'MGL01', 'PREEF27', 'FEUR10', 'JS109', 'EX45', 'SEÑ1600', 'PCGEAZ1', 'MREGR23',
    'ZEMP006', 'MAREGR15', 'PESCO40', 'PPIL001', 'ZBES010', 'ZBES005', 'ZBESM907', 'ZBRE010',
    'ZBRE005', 'PPIL002', 'PPIL003', 'ZSAC004', 'MAM5CESGR2', 'RSERMAQ04', 'RSERMAQ05',
    'RSERMAQ06', 'PILCJA01', 'PILCJA02', 'FLSER001', 'LBACE01', 'ZEDU007']
    
    # Probar diferentes combinaciones
    combinaciones = [
        {
            'nombre': 'ORIGINALES + TOP 3 FALTANTES',
            'productos': productos_originales + ['MREGR27', 'MREGR22', 'PREP115']
        },
        {
            'nombre': 'ORIGINALES + TOP 6 FALTANTES', 
            'productos': productos_originales + productos_extra
        },
        {
            'nombre': 'SOLO TOP 10 PRODUCTOS REALES',
            'productos': ['MREGR27', 'MREGR26', 'MREGR22', 'MREP620', 'PESGR10', 'PREP115', 'PESGR07', 'PREGR10', 'PREBS07', 'PREP607']
        },
        {
            'nombre': 'TODOS LOS PRODUCTOS REALES (sin filtro de lista)',
            'productos': None  # None significa sin filtro de productos
        }
    ]
    
    # Datos objetivo
    objetivo = {
        1: 30171996, 2: 33361032, 3: 40209833, 4: 37833346, 5: 34543474, 6: 26346728,
        7: 25033047, 8: 29797605, 9: 26659536, 10: 27055758, 11: 27674870, 12: 21711893
    }
    
    print("=== PROBANDO PRODUCTOS FALTANTES PARA 90% PRECISIÓN ===\n")
    
    for combo in combinaciones:
        print(f"🧪 {combo['nombre']}")
        
        if combo['productos'] is None:
            # Sin filtro de productos - todos los que tienen facturas
            where_productos = ""
        else:
            productos_str = "','".join(combo['productos'])
            where_productos = f"AND p.CCODIGOPRODUCTO IN ('{productos_str}')"
        
        query = f"""
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
                    -- Agregar conversiones para productos sin factor identificado
                    WHEN p.CCODIGOPRODUCTO = 'MGSMDLZ' THEN m.CUNIDADES * 1  -- X KG = asumimos 1kg por unidad
                    WHEN p.CCODIGOPRODUCTO = 'PREP118' AND p.CNOMBREPRODUCTO LIKE '%16 KG%' THEN m.CUNIDADES * 16
                    WHEN p.CCODIGOPRODUCTO = 'PREEF27' AND p.CNOMBREPRODUCTO LIKE '%907 KG%' THEN m.CUNIDADES * 907
                    WHEN p.CNOMBREPRODUCTO LIKE '%16 KG%' OR p.CNOMBREPRODUCTO LIKE '%16KG%' THEN m.CUNIDADES * 16
                    ELSE 0
                END
            ) AS KilosTotales
        FROM admMovimientos m
        JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
        JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
        WHERE 
            m.CIDDOCUMENTODE = 4
            AND YEAR(m.CFECHA) BETWEEN 2022 AND 2025
            AND dm.CMODULO = 1
            {where_productos}
        GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA)
        ORDER BY Anio, Mes
        """
        
        try:
            df = db.execute_query(query)
            
            if df.empty:
                print("   ❌ Sin datos\n")
                continue
                
            total_por_mes = df.groupby('Mes')['KilosTotales'].sum().to_dict()
            
            total_error = 0
            total_esperado = sum(objetivo.values())
            
            for mes in range(1, 13):
                obtenido = int(total_por_mes.get(mes, 0))
                esperado = objetivo[mes]
                error = abs(obtenido - esperado)
                total_error += error
            
            precision = 100 - (total_error/total_esperado*100)
            
            print(f"   📊 Precisión: {precision:.2f}%")
            print(f"   📈 Productos incluidos: {len(combo['productos']) if combo['productos'] else 'TODOS'}")
            
            # Si logramos 90%+, mostrar detalles
            if precision >= 90:
                print("   🎯 ¡OBJETIVO ALCANZADO! Detalles por mes:")
                meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                for mes in range(1, 13):
                    obtenido = int(total_por_mes.get(mes, 0))
                    esperado = objetivo[mes]
                    error_pct = abs(obtenido - esperado) / esperado * 100
                    print(f"      {meses[mes-1]}: {obtenido:,} vs {esperado:,} ({error_pct:.1f}%)")
                print(f"   ✅ ESTA ES LA COMBINACIÓN GANADORA!")
                return combo
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    return None

if __name__ == "__main__":
    resultado = test_productos_faltantes()
    if resultado:
        print(f"\n🏆 SOLUCIÓN ENCONTRADA: {resultado['nombre']}")
    else:
        print("\n❌ No se encontró combinación con 90%+ precisión")