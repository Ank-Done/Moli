#!/usr/bin/env python3
"""
Script para probar los filtros de fecha corregidos
"""

import sys
sys.path.append('.')

from app.models.reportes import ReporteVentas
from datetime import date

def test_date_filters_fixed():
    """Prueba filtros de fecha con la estructura corregida"""
    
    reporte = ReporteVentas()
    
    print("=== PRUEBA 1: SIN FILTROS DE FECHA ===")
    df_sin_filtros = reporte.get_ventas_por_periodo()
    print(f"Total de registros sin filtros: {len(df_sin_filtros)}")
    if not df_sin_filtros.empty:
        print(f"Rango de años: {df_sin_filtros['Anio'].min()} - {df_sin_filtros['Anio'].max()}")
        print("Primeros 3 registros:")
        print(df_sin_filtros.head(3))
    
    print("\n=== PRUEBA 2: CON FILTROS DE FECHA (2022) ===")
    fecha_inicio = date(2022, 1, 1)
    fecha_fin = date(2022, 12, 31)
    
    df_con_filtros = reporte.get_ventas_por_periodo(fecha_inicio, fecha_fin)
    print(f"Total de registros con filtros 2022: {len(df_con_filtros)}")
    if not df_con_filtros.empty:
        print(f"Años en resultados: {df_con_filtros['Anio'].unique()}")
        print("Todos los registros de 2022:")
        for _, row in df_con_filtros.iterrows():
            print(f"{int(row['Anio'])}-{int(row['Mes']):02d}: {row['ToneladasTotales']:.6f} toneladas")
    else:
        print("¡NO SE ENCONTRARON DATOS PARA 2022!")
    
    print("\n=== PRUEBA 3: FILTRO MES ESPECÍFICO (2018-01) ===")
    fecha_inicio_mes = date(2018, 1, 1)
    fecha_fin_mes = date(2018, 1, 31)
    
    df_mes_especifico = reporte.get_ventas_por_periodo(fecha_inicio_mes, fecha_fin_mes)
    print(f"Total de registros enero 2018: {len(df_mes_especifico)}")
    if not df_mes_especifico.empty:
        for _, row in df_mes_especifico.iterrows():
            print(f"{int(row['Anio'])}-{int(row['Mes']):02d}: {row['ToneladasTotales']:.6f} toneladas")
            # Comparar con datos de referencia
            if row['Anio'] == 2018 and row['Mes'] == 1:
                ref_toneladas = 18901.903948
                precision = (min(ref_toneladas, row['ToneladasTotales']) / max(ref_toneladas, row['ToneladasTotales'])) * 100
                print(f"  Referencia: {ref_toneladas:.6f} toneladas")
                print(f"  Coincidencia: {precision:.2f}%")
    else:
        print("¡NO SE ENCONTRARON DATOS PARA ENERO 2018!")

if __name__ == "__main__":
    test_date_filters_fixed()