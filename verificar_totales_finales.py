#!/usr/bin/env python3
"""
Verificar totales finales con SOLO FACTURAS vs tabla objetivo
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.models.reportes import ReporteVentas

def verificar_totales():
    reporte = ReporteVentas()
    df = reporte.get_ventas_por_periodo()
    
    # Filtrar 2022-2025
    df_2022_2025 = df[df['Anio'].isin([2022, 2023, 2024, 2025])]
    
    # Datos objetivo de tu tabla Excel
    objetivo = {
        1: 30171996,   # Enero: 5,705,013 + 10,863,887 + 5,912,697 + 7,690,399
        2: 33361032,   # Febrero
        3: 40209833,   # Marzo  
        4: 37833346,   # Abril
        5: 34543474,   # Mayo
        6: 26346728,   # Junio
        7: 25033047,   # Julio
        8: 29797605,   # Agosto
        9: 26659536,   # Septiembre
        10: 27055758,  # Octubre
        11: 27674870,  # Noviembre
        12: 21711893   # Diciembre
    }
    
    print("=== VERIFICACIÓN TOTALES FINALES (SOLO FACTURAS) ===\n")
    
    # Agrupar por mes sumando todos los años
    total_por_mes = df_2022_2025.groupby('Mes')['KilosTotales'].sum().to_dict()
    
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    total_error = 0
    total_esperado = sum(objetivo.values())
    total_obtenido = sum(total_por_mes.values())
    
    print("📊 COMPARACIÓN MES A MES:")
    print("-" * 80)
    print(f"{'Mes':<12} {'Obtenido':<15} {'Esperado':<15} {'Diferencia':<15} {'Error %':<8}")
    print("-" * 80)
    
    for mes in range(1, 13):
        obtenido = int(total_por_mes.get(mes, 0))
        esperado = objetivo[mes]
        diferencia = obtenido - esperado
        error_abs = abs(diferencia)
        porcentaje_error = (error_abs / esperado * 100) if esperado > 0 else 0
        total_error += error_abs
        
        signo = "+" if diferencia >= 0 else ""
        print(f"{meses[mes-1]:<12} {obtenido:,}".ljust(15) + 
              f"{esperado:,}".ljust(15) + 
              f"{signo}{diferencia:,}".ljust(15) + 
              f"{porcentaje_error:.1f}%")
    
    print("-" * 80)
    print(f"{'TOTALES':<12} {total_obtenido:,}".ljust(15) + 
          f"{total_esperado:,}".ljust(15) + 
          f"{total_obtenido - total_esperado:+,}".ljust(15))
    
    print(f"\n📈 RESUMEN:")
    print(f"   Error total absoluto: {total_error:,} kg")
    print(f"   Error porcentual: {total_error/total_esperado*100:.1f}%")
    print(f"   Precisión: {100 - (total_error/total_esperado*100):.1f}%")
    
    # Mostrar datos por año para verificar
    print(f"\n📅 DATOS POR AÑO Y MES (Facturas únicamente):")
    print("-" * 50)
    for _, row in df_2022_2025.iterrows():
        print(f"{int(row['Anio'])} - {meses[int(row['Mes'])-1]:<12}: {int(row['KilosTotales']):,} kg")

if __name__ == "__main__":
    verificar_totales()