#!/usr/bin/env python3
"""
Análisis detallado de productos y conversiones de peso para encontrar el 90%
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.database import DatabaseConfig

def analisis_detallado():
    db = DatabaseConfig()
    
    print("=== ANÁLISIS DETALLADO PARA 90% PRECISIÓN ===\n")
    
    # 1. Primero verificar qué productos realmente tienen movimientos con FACTURAS
    print("🔍 1. PRODUCTOS CON FACTURAS (2022-2025):")
    query_productos = """
    SELECT 
        p.CCODIGOPRODUCTO,
        p.CNOMBREPRODUCTO,
        COUNT(*) as movimientos,
        SUM(m.CUNIDADES) as unidades_totales,
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
        ) AS kilos_totales
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE 
        m.CIDDOCUMENTODE = 4
        AND YEAR(m.CFECHA) BETWEEN 2022 AND 2025
        AND dm.CMODULO = 1
    GROUP BY p.CCODIGOPRODUCTO, p.CNOMBREPRODUCTO
    ORDER BY kilos_totales DESC
    """
    
    df_productos = db.execute_query(query_productos)
    print(f"   Total productos con facturas: {len(df_productos)}")
    print("   Top 10 productos por kilos:")
    
    for _, row in df_productos.head(10).iterrows():
        codigo = row['CCODIGOPRODUCTO'].strip()
        nombre = row['CNOMBREPRODUCTO'].strip()[:50]
        kilos = int(row['kilos_totales'])
        print(f"   {codigo:<15} {kilos:>12,} kg - {nombre}")
    
    # 2. Verificar si hay productos que no se están considerando
    print(f"\n🔍 2. VERIFICANDO COBERTURA DE PRODUCTOS:")
    
    productos_config = ['MESCO25', 'MESCO30', 'MESPU07', 'MREGR26', 'MREGR30', 'MREP613', 'MREP614', 'MREP620',
                       'PAL0007', 'PAL0008', 'PAL0009', 'PBSMZ04', 'PBSMZ05', 'PBSMZ06', 'PBSMZ08', 'PBSMZ09',
                       'PBSMZ11', 'PBSMZ14', 'PCAGF02', 'PCAGF03', 'PCAGF04']  # Solo algunos para la prueba
    
    productos_encontrados = set(row['CCODIGOPRODUCTO'].strip() for _, row in df_productos.iterrows())
    productos_config_set = set(productos_config)
    
    faltantes = productos_config_set - productos_encontrados
    extras = productos_encontrados - productos_config_set
    
    print(f"   Productos configurados que NO tienen facturas: {len(faltantes)}")
    if faltantes:
        print(f"   Faltantes: {', '.join(list(faltantes)[:5])}")
    
    print(f"   Productos con facturas NO configurados: {len(extras)}")
    if extras:
        print(f"   Extras: {', '.join(list(extras)[:5])}")
    
    # 3. Probar diferentes factores de conversión para productos problemáticos
    print(f"\n🔍 3. ANÁLISIS DE CONVERSIONES DE PESO:")
    
    # Consultar productos con nombres que podrían tener problemas de conversión
    query_conversiones = """
    SELECT DISTINCT
        p.CCODIGOPRODUCTO,
        p.CNOMBREPRODUCTO,
        SUM(m.CUNIDADES) as unidades_2022_2025,
        CASE
            WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN 1
            WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN 25
            WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN 50
            WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN 0.907
            WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN 0.5
            WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN 5
            WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN 2
            WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN 20
            WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN 26
            WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN 27
            WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN 22.68
            WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN 900
            WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN 1000
            ELSE 0
        END as factor_conversion
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE 
        m.CIDDOCUMENTODE = 4
        AND YEAR(m.CFECHA) BETWEEN 2022 AND 2025
        AND dm.CMODULO = 1
    GROUP BY p.CCODIGOPRODUCTO, p.CNOMBREPRODUCTO
    ORDER BY unidades_2022_2025 DESC
    """
    
    df_conversiones = db.execute_query(query_conversiones)
    
    print("   Productos con factor 0 (SIN CONVERSIÓN):")
    sin_conversion = df_conversiones[df_conversiones['factor_conversion'] == 0]
    
    if not sin_conversion.empty:
        for _, row in sin_conversion.iterrows():
            codigo = row['CCODIGOPRODUCTO'].strip()
            nombre = row['CNOMBREPRODUCTO'].strip()
            unidades = int(row['unidades_2022_2025'])
            print(f"   ⚠️  {codigo:<15} {unidades:>8,} units - {nombre}")
    else:
        print("   ✅ Todos los productos tienen conversión")
    
    # 4. Probar incluyendo productos sin conversión con factor 1
    print(f"\n🧪 4. PROBANDO INCLUIR PRODUCTOS SIN CONVERSIÓN (factor=1):")
    
    query_test = """
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
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
                ELSE m.CUNIDADES * 1  -- CAMBIO: en lugar de 0, usar 1
            END
        ) AS KilosTotales
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE 
        m.CIDDOCUMENTODE = 4
        AND YEAR(m.CFECHA) BETWEEN 2022 AND 2025
        AND dm.CMODULO = 1
    GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA)
    ORDER BY Anio, Mes
    """
    
    df_test = db.execute_query(query_test)
    
    objetivo = {
        1: 30171996, 2: 33361032, 3: 40209833, 4: 37833346, 5: 34543474, 6: 26346728,
        7: 25033047, 8: 29797605, 9: 26659536, 10: 27055758, 11: 27674870, 12: 21711893
    }
    
    total_por_mes = df_test.groupby('Mes')['KilosTotales'].sum().to_dict()
    total_error = 0
    
    for mes in range(1, 13):
        obtenido = int(total_por_mes.get(mes, 0))
        esperado = objetivo[mes]
        error = abs(obtenido - esperado)
        total_error += error
    
    precision = 100 - (total_error/sum(objetivo.values())*100)
    print(f"   📊 Precisión con ELSE=1: {precision:.2f}%")
    
    if precision >= 90:
        print("   🎯 ¡OBJETIVO ALCANZADO! ✅")
        return True
    
    return False

if __name__ == "__main__":
    if analisis_detallado():
        print("\n🎉 ¡ENCONTRAMOS LA SOLUCIÓN DE 90%+!")
    else:
        print("\n🔍 Necesitamos seguir investigando...")