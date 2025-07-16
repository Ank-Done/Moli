#!/usr/bin/env python3
"""
CYBERIA REALISTIC DEMO
Sistema de Inteligencia Empresarial para Moliendas y Alimentos
Con datos simulados realistas (sin conexión real a SQL Server por ahora)
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime, timedelta
import os
import sys
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Puerto del servidor
PORT = 8000

# Datos realistas simulados basados en el sistema real
PRODUCTOS_REALES = [
    {"product_code": "PREGR07", "product_name": "Azúcar Refinado Granulado Saco 25kg", "category": "Azúcar Refinado", "unit": "Pieza", "price": 490.00, "total_quantity": 125000, "total_sales": 4500000},
    {"product_code": "PESGR07", "product_name": "Azúcar Estándar Granulado Saco 25kg", "category": "Azúcar Estándar", "unit": "Pieza", "price": 370.00, "total_quantity": 98000, "total_sales": 3800000},
    {"product_code": "PG3EN09", "product_name": "Glucosa 43 Cubeta 27kg", "category": "Glucosa", "unit": "Kilogramo", "price": 706.00, "total_quantity": 78000, "total_sales": 2900000},
    {"product_code": "PREP107", "product_name": "Azúcar Refinado Pulverizado 10X Saco 25kg", "category": "Azúcar Refinado", "unit": "Pieza", "price": 521.00, "total_quantity": 15000, "total_sales": 1200000},
    {"product_code": "PAL0007", "product_name": "Almidón de Maíz Saco 25kg", "category": "Almidón", "unit": "Pieza", "price": 630.00, "total_quantity": 32000, "total_sales": 980000},
    {"product_code": "PESEM17", "product_name": "Azúcar Estándar Granulado C/10 Bolsas 2 LBS", "category": "Azúcar Estándar", "unit": "Paquete", "price": 149.00, "total_quantity": 2500, "total_sales": 180000},
    {"product_code": "PREGR01", "product_name": "Azúcar Refinado Granulado Saco 1kg", "category": "Azúcar Refinado", "unit": "Pieza", "price": 50.00, "total_quantity": 8500, "total_sales": 425000},
    {"product_code": "PREGR05", "product_name": "Azúcar Refinado Granulado Saco 5kg", "category": "Azúcar Refinado", "unit": "Pieza", "price": 60.00, "total_quantity": 12000, "total_sales": 720000},
    {"product_code": "PESGR01", "product_name": "Azúcar Estándar Granulado Saco 1kg", "category": "Azúcar Estándar", "unit": "Pieza", "price": 36.00, "total_quantity": 15000, "total_sales": 540000},
    {"product_code": "PESGR05", "product_name": "Azúcar Estándar Granulado Saco 5kg", "category": "Azúcar Estándar", "unit": "Pieza", "price": 36.00, "total_quantity": 18000, "total_sales": 648000},
    {"product_code": "PREP105", "product_name": "Azúcar Refinado Pulverizado 10X Saco 5kg", "category": "Azúcar Refinado", "unit": "Pieza", "price": 90.00, "total_quantity": 3500, "total_sales": 315000},
    {"product_code": "PREP110", "product_name": "Azúcar Refinado Pulverizado 10X Saco 10kg", "category": "Azúcar Refinado", "unit": "Pieza", "price": 125.00, "total_quantity": 2800, "total_sales": 350000},
    {"product_code": "PG3EN27", "product_name": "Glucosa 43 Cubeta 27kg", "category": "Glucosa", "unit": "Kilogramo", "price": 150.00, "total_quantity": 8200, "total_sales": 1230000},
    {"product_code": "PG4EN27", "product_name": "Glucosa 44 Cubeta 27kg", "category": "Glucosa", "unit": "Kilogramo", "price": 157.33, "total_quantity": 7500, "total_sales": 1180000},
    {"product_code": "PAL0001", "product_name": "Almidón de Maíz Saco 1kg", "category": "Almidón", "unit": "Pieza", "price": 30.00, "total_quantity": 5200, "total_sales": 156000},
    {"product_code": "PAL0005", "product_name": "Almidón de Maíz Saco 5kg", "category": "Almidón", "unit": "Pieza", "price": 60.00, "total_quantity": 4800, "total_sales": 288000},
    {"product_code": "PAL0010", "product_name": "Almidón de Maíz Saco 10kg", "category": "Almidón", "unit": "Pieza", "price": 100.00, "total_quantity": 3200, "total_sales": 320000},
    {"product_code": "DEXT001", "product_name": "Dextrosa Monohidrato Saco 25kg", "category": "Dextrosa", "unit": "Pieza", "price": 210.00, "total_quantity": 2100, "total_sales": 441000},
    {"product_code": "DEXT005", "product_name": "Dextrosa Monohidrato Saco 5kg", "category": "Dextrosa", "unit": "Pieza", "price": 90.00, "total_quantity": 1800, "total_sales": 162000},
    {"product_code": "FRUCT01", "product_name": "Fructosa Cristalina Saco 25kg", "category": "Fructosa", "unit": "Pieza", "price": 300.00, "total_quantity": 1200, "total_sales": 360000},
    {"product_code": "MALTO01", "product_name": "Maltodextrina Saco 25kg", "category": "Maltodextrina", "unit": "Pieza", "price": 300.00, "total_quantity": 980, "total_sales": 294000},
    {"product_code": "SORB001", "product_name": "Sorbitol Polvo Saco 25kg", "category": "Sorbitol", "unit": "Pieza", "price": 400.00, "total_quantity": 650, "total_sales": 260000},
    {"product_code": "PESEM10", "product_name": "Azúcar Estándar Granulado C/5 Bolsas 2kg", "category": "Azúcar Estándar", "unit": "Paquete", "price": 60.00, "total_quantity": 4200, "total_sales": 252000},
    {"product_code": "PRESEM5", "product_name": "Azúcar Refinado Granulado C/5 Bolsas 1kg", "category": "Azúcar Refinado", "unit": "Paquete", "price": 50.00, "total_quantity": 3800, "total_sales": 190000},
]

VENTAS_REALES = [
    {"pedido": "556773", "cliente": "Helados Eliza", "producto": "PREGR07 - Azúcar Refinado Granulado Saco 25kg", "cantidad": "2 Pieza", "precio": 490.00, "total": 980.00, "estado": "Completado"},
    {"pedido": "556774", "cliente": "Jorge Tamez", "producto": "PESGR07 - Azúcar Estándar Granulado Saco 25kg", "cantidad": "4 Pieza", "precio": 370.00, "total": 1480.00, "estado": "Completado"},
    {"pedido": "556775", "cliente": "Sergio Chaires", "producto": "PESGR07 - Azúcar Estándar Granulado Saco 25kg", "cantidad": "4 Pieza", "precio": 370.00, "total": 1480.00, "estado": "Completado"},
    {"pedido": "556784", "cliente": "Sergio Chaires", "producto": "PESGR07 - Azúcar Estándar Granulado Saco 25kg", "cantidad": "3 Pieza", "precio": 370.00, "total": 1110.00, "estado": "Completado"},
    {"pedido": "556785", "cliente": "Sergio Chaires", "producto": "PREGR07 - Azúcar Refinado Granulado Saco 25kg", "cantidad": "3 Pieza", "precio": 490.00, "total": 1470.00, "estado": "Completado"},
    {"pedido": "556786", "cliente": "Juan Manuel Rojas", "producto": "PESGR07 - Azúcar Estándar Granulado Saco 25kg", "cantidad": "2 Pieza", "precio": 375.00, "total": 750.00, "estado": "Completado"},
    {"pedido": "556787", "cliente": "David Muñoz", "producto": "PREGR07 - Azúcar Refinado Granulado Saco 25kg", "cantidad": "10 Pieza", "precio": 490.00, "total": 4900.00, "estado": "Completado"},
    {"pedido": "556793", "cliente": "Juan Huerta", "producto": "PESGR07 - Azúcar Estándar Granulado Saco 25kg", "cantidad": "1 Pieza", "precio": 370.00, "total": 370.00, "estado": "Completado"},
    {"pedido": "556794", "cliente": "Juan Huerta", "producto": "PESEM17 - Azúcar Estándar Granulado C/10 Bolsas 2 LBS", "cantidad": "1 Paquete", "precio": 149.00, "total": 149.00, "estado": "Completado"},
    {"pedido": "556795", "cliente": "Panadería Central", "producto": "PREGR07 - Azúcar Refinado Granulado Saco 25kg", "cantidad": "10 Pieza", "precio": 490.00, "total": 4900.00, "estado": "Pendiente"},
    {"pedido": "556795", "cliente": "Panadería Central", "producto": "PESGR07 - Azúcar Estándar Granulado Saco 25kg", "cantidad": "5 Pieza", "precio": 370.00, "total": 1850.00, "estado": "Pendiente"},
    {"pedido": "556795", "cliente": "Panadería Central", "producto": "PG3EN09 - Glucosa 43 Cubeta 27kg", "cantidad": "2 Kilogramo", "precio": 706.00, "total": 1412.00, "estado": "Pendiente"},
    {"pedido": "556798", "cliente": "Distribuidora Zucarmex", "producto": "PESGR07 - Azúcar Estándar Granulado Saco 25kg", "cantidad": "5 Pieza", "precio": 370.00, "total": 1850.00, "estado": "Completado"},
    {"pedido": "556798", "cliente": "Distribuidora Zucarmex", "producto": "PAL0007 - Almidón de Maíz Saco 25kg", "cantidad": "2 Pieza", "precio": 630.00, "total": 1260.00, "estado": "Completado"},
    {"pedido": "556799", "cliente": "Repostería Dulce", "producto": "PREGR07 - Azúcar Refinado Granulado Saco 25kg", "cantidad": "2 Pieza", "precio": 490.00, "total": 980.00, "estado": "Completado"},
    {"pedido": "556799", "cliente": "Repostería Dulce", "producto": "PREP107 - Azúcar Refinado Pulverizado 10X Saco 25kg", "cantidad": "1 Pieza", "precio": 521.00, "total": 521.00, "estado": "Completado"},
    {"pedido": "556802", "cliente": "Confitería Royal", "producto": "PREGR07 - Azúcar Refinado Granulado Saco 25kg", "cantidad": "8 Pieza", "precio": 490.00, "total": 3920.00, "estado": "Completado"},
    {"pedido": "556803", "cliente": "Dulces Tradicionales", "producto": "PREP107 - Azúcar Refinado Pulverizado 10X Saco 25kg", "cantidad": "3 Pieza", "precio": 521.00, "total": 1563.00, "estado": "Completado"},
    {"pedido": "556804", "cliente": "Industria Gallo", "producto": "PG3EN09 - Glucosa 43 Cubeta 27kg", "cantidad": "5 Kilogramo", "precio": 706.00, "total": 3530.00, "estado": "Completado"},
    {"pedido": "556805", "cliente": "Panadería La Moderna", "producto": "PESGR07 - Azúcar Estándar Granulado Saco 25kg", "cantidad": "15 Pieza", "precio": 370.00, "total": 5550.00, "estado": "Completado"},
    {"pedido": "556806", "cliente": "Chocolates Finos", "producto": "DEXT001 - Dextrosa Monohidrato Saco 25kg", "cantidad": "3 Pieza", "precio": 210.00, "total": 630.00, "estado": "Completado"},
    {"pedido": "556807", "cliente": "Bebidas Refrescantes", "producto": "FRUCT01 - Fructosa Cristalina Saco 25kg", "cantidad": "2 Pieza", "precio": 300.00, "total": 600.00, "estado": "Pendiente"},
    {"pedido": "556808", "cliente": "Productos Naturales", "producto": "MALTO01 - Maltodextrina Saco 25kg", "cantidad": "4 Pieza", "precio": 300.00, "total": 1200.00, "estado": "Pendiente"},
    {"pedido": "556809", "cliente": "Alimentos Saludables", "producto": "SORB001 - Sorbitol Polvo Saco 25kg", "cantidad": "2 Pieza", "precio": 400.00, "total": 800.00, "estado": "Completado"},
    {"pedido": "556810", "cliente": "Supermercado del Norte", "producto": "PESEM10 - Azúcar Estándar Granulado C/5 Bolsas 2kg", "cantidad": "20 Paquete", "precio": 60.00, "total": 1200.00, "estado": "Completado"},
    {"pedido": "556811", "cliente": "Tienda de Conveniencia", "producto": "PRESEM5 - Azúcar Refinado Granulado C/5 Bolsas 1kg", "cantidad": "15 Paquete", "precio": 50.00, "total": 750.00, "estado": "Completado"},
    {"pedido": "556812", "cliente": "Cafetería Central", "producto": "PREGR01 - Azúcar Refinado Granulado Saco 1kg", "cantidad": "25 Pieza", "precio": 50.00, "total": 1250.00, "estado": "Completado"},
    {"pedido": "556813", "cliente": "Restaurante Gourmet", "producto": "PREGR05 - Azúcar Refinado Granulado Saco 5kg", "cantidad": "8 Pieza", "precio": 60.00, "total": 480.00, "estado": "Completado"},
    {"pedido": "556814", "cliente": "Panadería Artesanal", "producto": "PAL0001 - Almidón de Maíz Saco 1kg", "cantidad": "12 Pieza", "precio": 30.00, "total": 360.00, "estado": "Completado"},
    {"pedido": "556815", "cliente": "Repostería Especializada", "producto": "PAL0005 - Almidón de Maíz Saco 5kg", "cantidad": "6 Pieza", "precio": 60.00, "total": 360.00, "estado": "Pendiente"},
    {"pedido": "556816", "cliente": "Industria Alimentaria MX", "producto": "PG4EN27 - Glucosa 44 Cubeta 27kg", "cantidad": "8 Kilogramo", "precio": 157.33, "total": 1258.64, "estado": "Completado"},
    {"pedido": "556817", "cliente": "Dulcería La Esperanza", "producto": "DEXT005 - Dextrosa Monohidrato Saco 5kg", "cantidad": "15 Pieza", "precio": 90.00, "total": 1350.00, "estado": "Completado"},
    {"pedido": "556818", "cliente": "Panificadora Industrial", "producto": "PREP110 - Azúcar Refinado Pulverizado 10X Saco 10kg", "cantidad": "12 Pieza", "precio": 125.00, "total": 1500.00, "estado": "Completado"},
    {"pedido": "556819", "cliente": "Refrescos Naturales", "producto": "FRUCT01 - Fructosa Cristalina Saco 25kg", "cantidad": "6 Pieza", "precio": 300.00, "total": 1800.00, "estado": "Completado"},
    {"pedido": "556820", "cliente": "Alimentos Dietéticos", "producto": "SORB001 - Sorbitol Polvo Saco 25kg", "cantidad": "4 Pieza", "precio": 400.00, "total": 1600.00, "estado": "Completado"},
]

class CyberiaRealisticHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        print(f"📝 Request: {path}")
        
        # API endpoints
        if path == '/api/analytics/dashboard-metrics':
            self.send_json_response(self.get_dashboard_metrics())
        elif path == '/health':
            self.send_json_response({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database": "Cyberia SQL Server (Simulado con datos reales)",
                "service": "Cyberia Realistic Demo v1.0.0"
            })
        elif path == '/api/productos':
            self.send_json_response(self.get_all_products())
        elif path == '/api/ventas':
            self.send_json_response(self.get_all_sales())
        elif path == '/productos':
            self.serve_products_page()
        elif path == '/ventas':
            self.serve_sales_page()
        # Static files
        elif path == '/' or path == '/dashboard':
            self.serve_dashboard()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        self.wfile.write(json_data.encode('utf-8'))
    
    def get_dashboard_metrics(self):
        """Obtener métricas del dashboard con datos realistas"""
        # Calcular métricas desde los datos reales
        total_sales = sum(p["total_sales"] for p in PRODUCTOS_REALES)
        total_products = len(PRODUCTOS_REALES)
        
        # Simular ventas del mes actual
        current_month_sales = total_sales * 0.12  # 12% del total anual
        current_month_orders = len([v for v in VENTAS_REALES if v["estado"] == "Completado"])
        current_avg_order = current_month_sales / current_month_orders if current_month_orders > 0 else 0
        
        return {
            "current_month_sales": self.format_currency_millions(current_month_sales),
            "current_month_orders": current_month_orders,
            "current_avg_order": current_avg_order,
            "ytd_sales": self.format_currency_millions(total_sales),
            "total_customers": 89,  # Simulado
            "total_products": total_products,
            "sales_change_pct": 12.5,  # Positivo
            "orders_change_pct": -3.2,  # Negativo
            "avg_order_change_pct": 8.1,  # Positivo
            "monthly_sales": self.get_monthly_sales(),
            "sales_by_type": self.get_sales_by_type(),
            "top_agents": self.get_top_agents(),
            "top_products": sorted(PRODUCTOS_REALES, key=lambda x: x["total_sales"], reverse=True)[:5],
            "worst_products": sorted(PRODUCTOS_REALES, key=lambda x: x["total_sales"])[:5]
        }
    
    def format_currency_millions(self, amount):
        """Formatear moneda en millones"""
        if amount is None:
            return "0"
        if amount >= 1000000:
            return f"{amount / 1000000:.1f}M"
        elif amount >= 1000:
            return f"{amount / 1000:.0f}K"
        else:
            return str(int(amount))
    
    def get_monthly_sales(self):
        """Obtener ventas mensuales simuladas"""
        months = [
            {"month_name": "Enero", "total_sales": 2800000, "year": 2024, "month": 1},
            {"month_name": "Febrero", "total_sales": 2650000, "year": 2024, "month": 2},
            {"month_name": "Marzo", "total_sales": 3200000, "year": 2024, "month": 3},
            {"month_name": "Abril", "total_sales": 2900000, "year": 2024, "month": 4},
            {"month_name": "Mayo", "total_sales": 3400000, "year": 2024, "month": 5},
            {"month_name": "Junio", "total_sales": 2750000, "year": 2024, "month": 6},
            {"month_name": "Julio", "total_sales": 0, "year": 2024, "month": 7}
        ]
        return months
    
    def get_sales_by_type(self):
        """Obtener ventas por tipo"""
        return [
            {"order_type": "Venta Directa", "total_sales": 8500000},
            {"order_type": "Distribuidor", "total_sales": 6200000},
            {"order_type": "Exportación", "total_sales": 2800000},
            {"order_type": "Mayorista", "total_sales": 1200000}
        ]
    
    def get_top_agents(self):
        """Obtener top agentes"""
        return [
            {"agent_code": "AGT001", "agent_name": "María González", "total_sales": 3500000, "total_orders": 45},
            {"agent_code": "AGT002", "agent_name": "Carlos Rivera", "total_sales": 2800000, "total_orders": 38},
            {"agent_code": "AGT003", "agent_name": "Ana López", "total_sales": 2200000, "total_orders": 32},
            {"agent_code": "AGT004", "agent_name": "José Martínez", "total_sales": 1900000, "total_orders": 28},
            {"agent_code": "AGT005", "agent_name": "Laura Sánchez", "total_sales": 1600000, "total_orders": 24}
        ]
    
    def get_all_products(self):
        """Obtener todos los productos"""
        return PRODUCTOS_REALES
    
    def get_all_sales(self):
        """Obtener todas las ventas"""
        return VENTAS_REALES
    
    def serve_dashboard(self):
        """Serve the dashboard HTML"""
        dashboard_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Sistema Cyberia Realistic</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .banner {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; text-align: center; padding: 12px; margin-bottom: 20px; border-radius: 8px; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .nav a {{ padding: 8px 16px; background: #fff; text-decoration: none; color: #333; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .nav a:hover {{ background: #e0e0e0; }}
        .nav a.active {{ background: #6366f1; color: white; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: white; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #6366f1; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .charts {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 30px; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .chart-canvas {{ position: relative; height: 300px; }}
        .info {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .status {{ display: flex; align-items: center; gap: 10px; }}
        .status-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #22c55e; }}
    </style>
</head>
<body>
    <div class="banner">🗄️ Cyberia Realistic Dashboard - Datos Simulados del Sistema Real</div>
    
    <div class="info">
        <div class="status">
            <div class="status-dot"></div>
            <span>Simulando conexión a SQL Server Cyberia - Datos basados en el sistema real de MYA</span>
        </div>
        <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
            📊 {len(PRODUCTOS_REALES)} productos reales • {len(VENTAS_REALES)} ventas simuladas • Códigos reales del sistema
        </div>
    </div>
    
    <div class="nav">
        <a href="/" class="active">Dashboard</a>
        <a href="/productos">Productos ({len(PRODUCTOS_REALES)})</a>
        <a href="/ventas">Ventas ({len(VENTAS_REALES)})</a>
        <a href="/api/productos" target="_blank">API Productos</a>
        <a href="/api/ventas" target="_blank">API Ventas</a>
    </div>
    
    <div class="metrics" id="metrics">
        <!-- Métricas se cargarán aquí -->
    </div>
    
    <div class="charts">
        <div class="chart-container">
            <h3>Tendencia de Ventas Mensuales</h3>
            <div class="chart-canvas">
                <canvas id="monthlySalesChart"></canvas>
            </div>
        </div>
        <div class="chart-container">
            <h3>Distribución por Tipo</h3>
            <div class="chart-canvas">
                <canvas id="salesTypeChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        let monthlySalesChart, salesTypeChart;
        
        async function loadDashboard() {{
            try {{
                const response = await fetch('/api/analytics/dashboard-metrics');
                const data = await response.json();
                
                // Renderizar métricas
                const metricsHtml = `
                    <div class="metric-card">
                        <div class="metric-value">${{data.current_month_sales}}</div>
                        <div class="metric-label">Ventas Mes Actual</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${{data.current_month_orders}}</div>
                        <div class="metric-label">Órdenes Mes Actual</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${{data.ytd_sales}}</div>
                        <div class="metric-label">Ventas YTD</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${{data.total_products}}</div>
                        <div class="metric-label">Productos Activos</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${{data.total_customers}}</div>
                        <div class="metric-label">Clientes Activos</div>
                    </div>
                `;
                document.getElementById('metrics').innerHTML = metricsHtml;
                
                // Gráfico de ventas mensuales
                const ctx1 = document.getElementById('monthlySalesChart').getContext('2d');
                if (monthlySalesChart) monthlySalesChart.destroy();
                
                monthlySalesChart = new Chart(ctx1, {{
                    type: 'line',
                    data: {{
                        labels: data.monthly_sales.map(m => m.month_name),
                        datasets: [{{
                            label: 'Ventas Mensuales',
                            data: data.monthly_sales.map(m => m.total_sales),
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                            fill: true,
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{
                                    callback: function(value) {{
                                        return (value / 1000000).toFixed(1) + 'M';
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
                
                // Gráfico de tipos de venta
                const ctx2 = document.getElementById('salesTypeChart').getContext('2d');
                if (salesTypeChart) salesTypeChart.destroy();
                
                salesTypeChart = new Chart(ctx2, {{
                    type: 'doughnut',
                    data: {{
                        labels: data.sales_by_type.map(s => s.order_type),
                        datasets: [{{
                            data: data.sales_by_type.map(s => s.total_sales),
                            backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899', '#f97316']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ position: 'bottom' }}
                        }}
                    }}
                }});
                
            }} catch (error) {{
                console.error('Error:', error);
                document.getElementById('metrics').innerHTML = '<p>Error cargando datos</p>';
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', loadDashboard);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(dashboard_html.encode('utf-8'))
    
    def serve_products_page(self):
        """Serve products page"""
        products_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Productos - Sistema Cyberia</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .banner {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; text-align: center; padding: 12px; margin-bottom: 20px; border-radius: 8px; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .nav a {{ padding: 8px 16px; background: #fff; text-decoration: none; color: #333; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .nav a:hover {{ background: #e0e0e0; }}
        .nav a.active {{ background: #6366f1; color: white; }}
        .products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .product-card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .product-code {{ font-family: monospace; background: #f0f0f0; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; }}
        .product-name {{ font-weight: bold; margin: 10px 0; }}
        .product-category {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
        .product-stats {{ display: flex; justify-content: space-between; font-size: 0.9em; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-weight: bold; color: #6366f1; }}
        .stat-label {{ color: #666; }}
    </style>
</head>
<body>
    <div class="banner">📦 Catálogo de Productos MYA - {len(PRODUCTOS_REALES)} Productos Reales</div>
    
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/productos" class="active">Productos</a>
        <a href="/ventas">Ventas</a>
    </div>
    
    <div class="products-grid" id="productsGrid">
        <!-- Productos se cargarán aquí -->
    </div>
    
    <script>
        async function loadProducts() {{
            try {{
                const response = await fetch('/api/productos');
                const products = await response.json();
                
                const productsGrid = document.getElementById('productsGrid');
                productsGrid.innerHTML = '';
                
                products.forEach(product => {{
                    const productCard = `
                        <div class="product-card">
                            <div class="product-code">${{product.product_code}}</div>
                            <div class="product-name">${{product.product_name}}</div>
                            <div class="product-category">${{product.category}}</div>
                            <div class="product-stats">
                                <div class="stat">
                                    <div class="stat-value">${{product.total_quantity.toLocaleString()}}</div>
                                    <div class="stat-label">Vendidos</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-value">$\${product.price.toFixed(2)}</div>
                                    <div class="stat-label">Precio</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-value">${{(product.total_sales / 1000000).toFixed(1)}}M</div>
                                    <div class="stat-label">Ventas</div>
                                </div>
                            </div>
                        </div>
                    `;
                    productsGrid.innerHTML += productCard;
                }});
                
                console.log(`Cargados ${{products.length}} productos`);
                
            }} catch (error) {{
                console.error('Error cargando productos:', error);
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', loadProducts);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(products_html.encode('utf-8'))
    
    def serve_sales_page(self):
        """Serve sales page"""
        sales_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ventas - Sistema Cyberia</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .banner {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; text-align: center; padding: 12px; margin-bottom: 20px; border-radius: 8px; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .nav a {{ padding: 8px 16px; background: #fff; text-decoration: none; color: #333; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .nav a:hover {{ background: #e0e0e0; }}
        .nav a.active {{ background: #6366f1; color: white; }}
        .sales-table {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .sales-table table {{ width: 100%; border-collapse: collapse; }}
        .sales-table th {{ background: #f5f5f5; padding: 12px; text-align: left; font-weight: bold; }}
        .sales-table td {{ padding: 12px; border-bottom: 1px solid #eee; }}
        .sales-table tr:hover {{ background: #f9f9f9; }}
        .status-badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
        .status-completed {{ background: #d4edda; color: #155724; }}
        .status-pending {{ background: #fff3cd; color: #856404; }}
    </style>
</head>
<body>
    <div class="banner">📊 Gestión de Ventas MYA - {len(VENTAS_REALES)} Ventas Simuladas</div>
    
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/productos">Productos</a>
        <a href="/ventas" class="active">Ventas</a>
    </div>
    
    <div class="sales-table">
        <table id="salesTable">
            <thead>
                <tr>
                    <th>Pedido</th>
                    <th>Cliente</th>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio</th>
                    <th>Total</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                <!-- Ventas se cargarán aquí -->
            </tbody>
        </table>
    </div>
    
    <script>
        async function loadSales() {{
            try {{
                const response = await fetch('/api/ventas');
                const sales = await response.json();
                
                const tbody = document.querySelector('#salesTable tbody');
                tbody.innerHTML = '';
                
                sales.forEach(sale => {{
                    const statusClass = sale.estado === 'Completado' ? 'status-completed' : 'status-pending';
                    const row = `
                        <tr>
                            <td>${{sale.pedido}}</td>
                            <td>${{sale.cliente}}</td>
                            <td>${{sale.producto}}</td>
                            <td>${{sale.cantidad}}</td>
                            <td>$\${sale.precio.toFixed(2)}</td>
                            <td>$\${sale.total.toFixed(2)}</td>
                            <td><span class="status-badge ${{statusClass}}">${{sale.estado}}</span></td>
                        </tr>
                    `;
                    tbody.innerHTML += row;
                }});
                
                console.log(`Cargadas ${{sales.length}} ventas`);
                
            }} catch (error) {{
                console.error('Error cargando ventas:', error);
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', loadSales);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(sales_html.encode('utf-8'))

def main():
    print("🚀 Iniciando Cyberia Realistic Demo...")
    print("🗄️ Simulando datos reales del sistema MYA")
    print(f"🌐 Servidor disponible en: http://localhost:{PORT}")
    print("📊 Basado en códigos de productos reales")
    print(f"📦 {len(PRODUCTOS_REALES)} productos con códigos reales")
    print(f"🛒 {len(VENTAS_REALES)} ventas simuladas")
    print()
    
    try:
        with socketserver.TCPServer(("", PORT), CyberiaRealisticHandler) as httpd:
            print(f"✅ Servidor iniciado exitosamente en puerto {PORT}")
            print("📱 Presiona Ctrl+C para detener el servidor")
            print("=" * 60)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()