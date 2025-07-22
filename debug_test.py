#!/usr/bin/env python3
"""
Script de debugging para probar la aplicación Flask paso a paso
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.models.reportes import ReporteVentas

def test_connection():
    print("=== TESTING FLASK APP DEBUG ===\n")
    
    try:
        print("1. Probando conexión básica...")
        reporte = ReporteVentas()
        
        print("2. Obteniendo productos disponibles...")
        productos = reporte.get_productos_disponibles()
        print(f"   ✓ Productos encontrados: {len(productos)}")
        if productos:
            print(f"   Ejemplo: {productos[0]}")
        
        print("3. Obteniendo años disponibles...")
        anos = reporte.get_anos_disponibles()
        print(f"   ✓ Años encontrados: {anos}")
        
        print("4. Probando consulta de ventas sin filtros...")
        datos = reporte.get_ventas_por_periodo()
        print(f"   ✓ Registros obtenidos: {len(datos)}")
        
        if not datos.empty:
            print("   Primeros 5 registros:")
            print(datos.head().to_string(index=False))
            
            print("\n   Tipos de datos:")
            print(datos.dtypes)
        else:
            print("   ⚠️  No se encontraron datos")
        
        print("5. Probando estadísticas...")
        estadisticas = reporte.get_resumen_estadisticas()
        print(f"   ✓ Estadísticas: {estadisticas}")
        
        print("\n✅ DEBUGGING COMPLETADO - Todo parece estar funcionando")
        
    except Exception as e:
        print(f"❌ ERROR en debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()