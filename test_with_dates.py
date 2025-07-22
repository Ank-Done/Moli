#!/usr/bin/env python3
"""
Probar que la aplicación use EXACTAMENTE tu consulta con filtros de fecha
"""

import sys
sys.path.append('.')

from app.models.reportes import ReporteVentas
from datetime import date

# Probar método directo
reporte = ReporteVentas()

print("=== SIN FILTROS ===")
df_sin = reporte.get_ventas_por_periodo()
print(f"Total registros: {len(df_sin)}")
if not df_sin.empty:
    enero_2018 = df_sin[(df_sin['Anio'] == 2018) & (df_sin['Mes'] == 1)]
    if not enero_2018.empty:
        print(f"Enero 2018: {enero_2018.iloc[0]['ToneladasTotales']:.6f} toneladas")

print("\n=== CON FILTROS ENERO 2018 ===")
df_con = reporte.get_ventas_por_periodo(date(2018, 1, 1), date(2018, 1, 31))
print(f"Total registros: {len(df_con)}")
for _, row in df_con.iterrows():
    print(f"{int(row['Anio'])}-{int(row['Mes']):02d}: {row['ToneladasTotales']:.6f} toneladas")