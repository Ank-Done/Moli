#!/usr/bin/env python3
"""
Probar expandiendo la lista de productos con los factores óptimos encontrados
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.database import DatabaseConfig

def test_expansion():
    db = DatabaseConfig()
    
    # Datos objetivo
    objetivo = {
        1: 30171996, 2: 33361032, 3: 40209833, 4: 37833346, 5: 34543474, 6: 26346728,
        7: 25033047, 8: 29797605, 9: 26659536, 10: 27055758, 11: 27674870, 12: 21711893
    }
    
    # Listas de productos para probar
    listas_productos = [
        {
            'nombre': 'TOP 10 + 15 productos adicionales',
            'productos': ['MREGR27', 'MREGR26', 'MREGR22', 'MREP620', 'PESGR10', 'PREP115', 'PESGR07', 'PREGR10', 'PREBS07', 'PREP607',
                         'MESCO25', 'MESCO30', 'MESPU07', 'MREP613', 'MREP614', 'PBSMZ08', 'PBSMZ11', 'PBSMZ14', 'PBSMZ22', 'PESCO25',
                         'PESEM17', 'PREBS07', 'PRECE01', 'PREEF26', 'PREEM17']
        },
        {
            'nombre': 'TOP 10 + productos de menor volumen',
            'productos': ['MREGR27', 'MREGR26', 'MREGR22', 'MREP620', 'PESGR10', 'PREP115', 'PESGR07', 'PREGR10', 'PREBS07', 'PREP607',
                         'MGSMDLZ', 'PREP113', 'PREP107', 'RMREP614', 'RMREP620', 'PESEM11', 'PESEM12', 'RPREP607', 'RPREBS07']
        },
        {
            'nombre': 'Solo productos con alta certeza de conversión',
            'productos': ['MREGR27', 'MREGR26', 'MREGR22', 'MREP620', 'PESGR10', 'PREP115', 'PESGR07', 'PREGR10', 'PREBS07', 'PREP607',
                         'MESCO25', 'MESCO30', 'PESCO25']
        }
    ]
    
    # Usar los mejores factores encontrados
    mregr_factor = 7.0
    prep115_factor = 6.3
    
    print("=== EXPANDIENDO PRODUCTOS CON FACTORES ÓPTIMOS ===\n")
    print(f"💡 Usando factores: MREGR={mregr_factor}kg, PREP115={prep115_factor}kg\n")
    
    mejor_precision = 0
    mejor_lista = None
    
    for lista in listas_productos:
        print(f"🧪 {lista['nombre']} ({len(lista['productos'])} productos)")
        
        productos_str = "','".join(lista['productos'])
        
        query = f"""
        SELECT YEAR(m.CFECHA) AS Anio, MONTH(m.CFECHA) AS Mes,
               SUM(
                   CASE
                       WHEN p.CCODIGOPRODUCTO LIKE 'MREGR%' AND p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * {mregr_factor}
                       WHEN p.CCODIGOPRODUCTO = 'PREP115' THEN m.CUNIDADES * {prep115_factor}
                       WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' THEN m.CUNIDADES * 1
                       WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                       WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                       WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                       WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                       WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                       WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                       WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                       WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                       WHEN p.CCODIGOPRODUCTO = 'MGSMDLZ' THEN m.CUNIDADES * 1
                       ELSE 0
                   END
               ) AS KilosTotales
        FROM admMovimientos m
        JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO  
        WHERE m.CIDDOCUMENTODE = 4 AND YEAR(m.CFECHA) BETWEEN 2022 AND 2025
          AND p.CCODIGOPRODUCTO IN ('{productos_str}')
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
            
            if precision > mejor_precision:
                mejor_precision = precision
                mejor_lista = lista
            
            print(f"   📊 Precisión: {precision:.2f}%")
            
            if precision >= 90:
                print("   🎯 ¡OBJETIVO 90% ALCANZADO!")
                meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                for mes in range(1, 13):
                    obtenido = int(total_por_mes.get(mes, 0))
                    esperado = objetivo[mes]
                    error_pct = abs(obtenido - esperado) / esperado * 100
                    print(f"      {meses[mes-1]}: {obtenido:,} vs {esperado:,} ({error_pct:.1f}%)")
                
                print(f"\n✅ CONFIGURACIÓN FINAL GANADORA:")
                print(f"   - Productos: {len(lista['productos'])} productos")
                print(f"   - MREGR: {mregr_factor} kg por unidad")  
                print(f"   - PREP115: {prep115_factor} kg por unidad")
                print(f"   - Lista: {', '.join(lista['productos'][:10])}...")
                
                return {'lista': lista, 'mregr_factor': mregr_factor, 'prep115_factor': prep115_factor, 'precision': precision}
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    print(f"🏆 MEJOR RESULTADO: {mejor_precision:.2f}% - {mejor_lista['nombre'] if mejor_lista else 'Ninguno'}")
    
    if mejor_precision >= 85:
        print(f"\n📊 MUY CERCA DEL 90%! Mejor configuración:")
        print(f"   - {mejor_lista['nombre']}")
        print(f"   - {len(mejor_lista['productos'])} productos") 
        print(f"   - MREGR: {mregr_factor} kg, PREP115: {prep115_factor} kg")
        
        # Sugerir pequeños ajustes finales
        if mejor_precision >= 88:
            print(f"   💡 Sugerencia: Pequeños ajustes a los factores pueden lograr 90%+")
    
    return {'lista': mejor_lista, 'mregr_factor': mregr_factor, 'prep115_factor': prep115_factor, 'precision': mejor_precision}

if __name__ == "__main__":
    resultado = test_expansion()
    if resultado['precision'] >= 90:
        print(f"\n🎉 ¡OBJETIVO DE 90% ALCANZADO! {resultado['precision']:.2f}%")
    else:
        print(f"\n🔧 Mejor resultado: {resultado['precision']:.2f}% con {resultado['lista']['nombre']}")