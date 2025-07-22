#!/usr/bin/env python3
"""
Probar solo los TOP 10 productos de mayor volumen para encontrar el equilibrio
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.database import DatabaseConfig

def test_top10_productos():
    db = DatabaseConfig()
    
    # Solo los 10 productos de mayor volumen identificados
    productos_top10 = ['MREGR27', 'MREGR26', 'MREGR22', 'MREP620', 'PESGR10', 
                       'PREP115', 'PESGR07', 'PREGR10', 'PREBS07', 'PREP607']
    
    productos_str = "','" .join(productos_top10)
    
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
                -- Conversiones específicas para productos identificados sin patrón
                WHEN p.CCODIGOPRODUCTO = 'PREP115' AND p.CNOMBREPRODUCTO LIKE '%50 LIBRAS%' THEN m.CUNIDADES * 22.68
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
        AND p.CCODIGOPRODUCTO IN ('{productos_str}')
    GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA)
    ORDER BY Anio, Mes
    """
    
    print("=== PRUEBA SOLO TOP 10 PRODUCTOS DE MAYOR VOLUMEN ===\n")
    
    # Datos objetivo
    objetivo = {
        1: 30171996, 2: 33361032, 3: 40209833, 4: 37833346, 5: 34543474, 6: 26346728,
        7: 25033047, 8: 29797605, 9: 26659536, 10: 27055758, 11: 27674870, 12: 21711893
    }
    
    df = db.execute_query(query)
    
    if df.empty:
        print("❌ Sin datos")
        return
        
    total_por_mes = df.groupby('Mes')['KilosTotales'].sum().to_dict()
    
    total_error = 0
    total_esperado = sum(objetivo.values())
    
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    print("📊 COMPARACIÓN MES A MES (Solo TOP 10 productos):")
    print("-" * 80)
    print(f"{'Mes':<5} {'Obtenido':<15} {'Esperado':<15} {'Diferencia':<15} {'Error %':<8}")
    print("-" * 80)
    
    for mes in range(1, 13):
        obtenido = int(total_por_mes.get(mes, 0))
        esperado = objetivo[mes]
        diferencia = obtenido - esperado
        error_abs = abs(diferencia)
        error_pct = (error_abs / esperado * 100) if esperado > 0 else 0
        total_error += error_abs
        
        signo = "+" if diferencia >= 0 else ""
        print(f"{meses[mes-1]:<5} {obtenido:,}".ljust(15) + 
              f"{esperado:,}".ljust(15) + 
              f"{signo}{diferencia:,}".ljust(15) + 
              f"{error_pct:.1f}%")
    
    precision = 100 - (total_error/total_esperado*100)
    
    print("-" * 80)
    print(f"📈 RESUMEN:")
    print(f"   Precisión: {precision:.2f}%")
    print(f"   Error total: {total_error:,} kg")
    
    # Mostrar detalle de cada producto
    print(f"\n🔍 DETALLE POR PRODUCTO:")
    query_detalle = f"""
    SELECT 
        p.CCODIGOPRODUCTO,
        p.CNOMBREPRODUCTO,
        SUM(m.CUNIDADES) as unidades_totales,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CCODIGOPRODUCTO = 'PREP115' AND p.CNOMBREPRODUCTO LIKE '%50 LIBRAS%' THEN m.CUNIDADES * 22.68
                ELSE m.CUNIDADES
            END
        ) AS kilos_totales
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    WHERE 
        m.CIDDOCUMENTODE = 4
        AND YEAR(m.CFECHA) BETWEEN 2022 AND 2025
        AND dm.CMODULO = 1
        AND p.CCODIGOPRODUCTO IN ('{productos_str}')
    GROUP BY p.CCODIGOPRODUCTO, p.CNOMBREPRODUCTO
    ORDER BY kilos_totales DESC
    """
    
    df_detalle = db.execute_query(query_detalle)
    for _, row in df_detalle.iterrows():
        codigo = row['CCODIGOPRODUCTO'].strip()
        nombre = row['CNOMBREPRODUCTO'].strip()[:60]
        kilos = int(row['kilos_totales'])
        unidades = int(row['unidades_totales'])
        print(f"   {codigo:<12} {kilos:>12,} kg ({unidades:,} unidades) - {nombre}")
    
    if precision >= 90:
        print(f"\n🎯 ¡OBJETIVO ALCANZADO! {precision:.2f}% de precisión")
        return True
    
    return False

if __name__ == "__main__":
    if test_top10_productos():
        print("\n🎉 ¡ENCONTRAMOS LA CONFIGURACIÓN CORRECTA!")
    else:
        print("\n🔍 Necesitamos ajustar más...")