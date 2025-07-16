#!/usr/bin/env python3
"""
CYBERIA SIMPLE DEMO - SIN DEPENDENCIAS EXTERNAS
Sistema de Inteligencia Empresarial para Moliendas y Alimentos
Versión demo simplificada con servidor HTTP nativo de Python
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime
import os
import sys

# Puerto del servidor
PORT = 8001

# Datos simulados del dashboard
MOCK_DASHBOARD_DATA = {
    "current_month_sales": "2.5M",
    "current_month_orders": 156,
    "current_avg_order": 16025.50,
    "ytd_sales": "18.7M",
    "total_customers": 89,
    "total_products": 24,  # Azúcares, glucosa, almidón de maíz y productos complementarios
    "sales_change_pct": 12.5,  # Positivo
    "orders_change_pct": -3.2,  # Negativo
    "avg_order_change_pct": 8.1,  # Positivo
    "monthly_sales": [
        {"month_name": "Enero", "total_sales": 2800000, "year": 2024, "month": 1},
        {"month_name": "Febrero", "total_sales": 2650000, "year": 2024, "month": 2},
        {"month_name": "Marzo", "total_sales": 3200000, "year": 2024, "month": 3},
        {"month_name": "Abril", "total_sales": 2900000, "year": 2024, "month": 4},
        {"month_name": "Mayo", "total_sales": 3400000, "year": 2024, "month": 5},
        {"month_name": "Junio", "total_sales": 2750000, "year": 2024, "month": 6},
        {"month_name": "Julio", "total_sales": 0, "year": 2024, "month": 7}
    ],
    "sales_by_type": [
        {"order_type": "Venta Directa", "total_sales": 8500000},
        {"order_type": "Distribuidor", "total_sales": 6200000},
        {"order_type": "Exportación", "total_sales": 2800000},
        {"order_type": "Mayorista", "total_sales": 1200000}
    ],
    "top_agents": [
        {"agent_code": "AGT001", "agent_name": "María González", "total_sales": 3500000, "total_orders": 45},
        {"agent_code": "AGT002", "agent_name": "Carlos Rivera", "total_sales": 2800000, "total_orders": 38},
        {"agent_code": "AGT003", "agent_name": "Ana López", "total_sales": 2200000, "total_orders": 32},
        {"agent_code": "AGT004", "agent_name": "José Martínez", "total_sales": 1900000, "total_orders": 28},
        {"agent_code": "AGT005", "agent_name": "Laura Sánchez", "total_sales": 1600000, "total_orders": 24}
    ],
    "top_products": [
        {"product_code": "PREGR07", "product_name": "Azúcar Refinado Granulado Saco 25kg", "total_quantity": 125000, "total_sales": 4500000, "category": "Azúcar Refinado"},
        {"product_code": "PESGR07", "product_name": "Azúcar Estándar Granulado Saco 25kg", "total_quantity": 98000, "total_sales": 3800000, "category": "Azúcar Estándar"},
        {"product_code": "PG3EN09", "product_name": "Glucosa 43 Cubeta 27kg", "total_quantity": 78000, "total_sales": 2900000, "category": "Glucosa"},
        {"product_code": "PREP107", "product_name": "Azúcar Refinado Pulverizado 10X Saco 25kg", "total_quantity": 15000, "total_sales": 1200000, "category": "Azúcar Refinado"},
        {"product_code": "PAL0007", "product_name": "Almidón de Maíz Saco 25kg", "total_quantity": 32000, "total_sales": 980000, "category": "Almidón"}
    ],
    "worst_products": [
        {"product_code": "PESEM17", "product_name": "Azúcar Estándar Granulado C/10 Bolsas 2 LBS", "total_quantity": 2500, "total_sales": 180000, "avg_margin": 5.2, "category": "Azúcar Estándar"},
        {"product_code": "PREG009", "product_name": "Azúcar Refinado Granulado Saco 1kg", "total_quantity": 1200, "total_sales": 95000, "avg_margin": 7.8, "category": "Azúcar Refinado"},
        {"product_code": "PG4EN10", "product_name": "Glucosa 44 Cubeta 10kg", "total_quantity": 800, "total_sales": 75000, "avg_margin": 8.5, "category": "Glucosa"},
        {"product_code": "PREP205", "product_name": "Azúcar Refinado Pulverizado 6X Saco 5kg", "total_quantity": 950, "total_sales": 68000, "avg_margin": 9.2, "category": "Azúcar Refinado"},
        {"product_code": "PAL0005", "product_name": "Almidón de Maíz Saco 5kg", "total_quantity": 600, "total_sales": 45000, "avg_margin": 11.8, "category": "Almidón"}
    ],
    "total_real_products": 24  # Azúcares, glucosa, almidón de maíz y productos complementarios de Moliendas y Alimentos
}

class CyberiaHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        print(f"📝 Request: {path}")
        
        # API endpoints
        if path == '/api/analytics/dashboard-metrics':
            self.send_json_response(MOCK_DASHBOARD_DATA)
        elif path == '/health':
            self.send_json_response({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database": "mock data",
                "service": "Cyberia Simple Demo v1.0.0"
            })
        elif path == '/productos':
            self.serve_products_page()
        elif path == '/ventas':
            self.serve_sales_page()
        elif path == '/api/productos':
            self.send_json_response(self.get_all_products())
        elif path == '/api/ventas':
            self.send_json_response(self.get_all_sales())
        # Static files
        elif path == '/' or path == '/dashboard':
            self.serve_dashboard()
        elif path.startswith('/templates/'):
            # Serve templates as text
            file_path = path[1:]  # Remove leading slash
            self.serve_template_file(file_path)
        else:
            # Try to serve as static file
            super().do_GET()
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def serve_dashboard(self):
        """Serve the dashboard HTML"""
        dashboard_html = self.get_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(dashboard_html.encode('utf-8'))
    
    def serve_products_page(self):
        """Serve the products page HTML"""
        products_html = self.get_products_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(products_html.encode('utf-8'))
    
    def serve_sales_page(self):
        """Serve the sales page HTML"""
        sales_html = self.get_sales_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(sales_html.encode('utf-8'))
    
    def get_all_products(self):
        """Get all products data"""
        # Expandir los datos de productos usando los que ya tenemos
        all_products = MOCK_DASHBOARD_DATA['top_products'] + MOCK_DASHBOARD_DATA['worst_products']
        
        # Agregar más productos simulados basados en códigos reales
        additional_products = [
            {"product_code": "PREGR01", "product_name": "Azúcar Refinado Granulado Saco 1kg", "total_quantity": 8500, "total_sales": 425000, "category": "Azúcar Refinado"},
            {"product_code": "PREGR05", "product_name": "Azúcar Refinado Granulado Saco 5kg", "total_quantity": 12000, "total_sales": 720000, "category": "Azúcar Refinado"},
            {"product_code": "PESGR01", "product_name": "Azúcar Estándar Granulado Saco 1kg", "total_quantity": 15000, "total_sales": 540000, "category": "Azúcar Estándar"},
            {"product_code": "PESGR05", "product_name": "Azúcar Estándar Granulado Saco 5kg", "total_quantity": 18000, "total_sales": 648000, "category": "Azúcar Estándar"},
            {"product_code": "PREP105", "product_name": "Azúcar Refinado Pulverizado 10X Saco 5kg", "total_quantity": 3500, "total_sales": 315000, "category": "Azúcar Refinado"},
            {"product_code": "PREP110", "product_name": "Azúcar Refinado Pulverizado 10X Saco 10kg", "total_quantity": 2800, "total_sales": 350000, "category": "Azúcar Refinado"},
            {"product_code": "PG3EN27", "product_name": "Glucosa 43 Cubeta 27kg", "total_quantity": 8200, "total_sales": 1230000, "category": "Glucosa"},
            {"product_code": "PG4EN27", "product_name": "Glucosa 44 Cubeta 27kg", "total_quantity": 7500, "total_sales": 1180000, "category": "Glucosa"},
            {"product_code": "PAL0001", "product_name": "Almidón de Maíz Saco 1kg", "total_quantity": 5200, "total_sales": 156000, "category": "Almidón"},
            {"product_code": "PAL0005", "product_name": "Almidón de Maíz Saco 5kg", "total_quantity": 4800, "total_sales": 288000, "category": "Almidón"},
            {"product_code": "PAL0010", "product_name": "Almidón de Maíz Saco 10kg", "total_quantity": 3200, "total_sales": 320000, "category": "Almidón"},
            {"product_code": "DEXT001", "product_name": "Dextrosa Monohidrato Saco 25kg", "total_quantity": 2100, "total_sales": 441000, "category": "Dextrosa"},
            {"product_code": "DEXT005", "product_name": "Dextrosa Monohidrato Saco 5kg", "total_quantity": 1800, "total_sales": 162000, "category": "Dextrosa"},
            {"product_code": "FRUCT01", "product_name": "Fructosa Cristalina Saco 25kg", "total_quantity": 1200, "total_sales": 360000, "category": "Fructosa"},
            {"product_code": "MALTO01", "product_name": "Maltodextrina Saco 25kg", "total_quantity": 980, "total_sales": 294000, "category": "Maltodextrina"},
            {"product_code": "SORB001", "product_name": "Sorbitol Polvo Saco 25kg", "total_quantity": 650, "total_sales": 260000, "category": "Sorbitol"},
            {"product_code": "PESEM10", "product_name": "Azúcar Estándar Granulado C/5 Bolsas 2kg", "total_quantity": 4200, "total_sales": 252000, "category": "Azúcar Estándar"},
            {"product_code": "PRESEM5", "product_name": "Azúcar Refinado Granulado C/5 Bolsas 1kg", "total_quantity": 3800, "total_sales": 190000, "category": "Azúcar Refinado"},
        ]
        
        return all_products + additional_products
    
    def get_all_sales(self):
        """Get all sales data"""
        return [
            {"pedido": "556773", "cliente": "Helados Eliza", "producto": "PREGR07 - Azúcar Refinado Granulado 25kg", "cantidad": "2 sacos", "precio": 490.00, "total": 980.00, "estado": "Completado"},
            {"pedido": "556774", "cliente": "Jorge Tamez", "producto": "PESGR07 - Azúcar Estándar Granulado 25kg", "cantidad": "4 sacos", "precio": 370.00, "total": 1480.00, "estado": "Completado"},
            {"pedido": "556775", "cliente": "Sergio Chaires", "producto": "PESGR07 - Azúcar Estándar Granulado 25kg", "cantidad": "4 sacos", "precio": 370.00, "total": 1480.00, "estado": "Completado"},
            {"pedido": "556784", "cliente": "Sergio Chaires", "producto": "PESGR07 - Azúcar Estándar Granulado 25kg", "cantidad": "3 sacos", "precio": 370.00, "total": 1110.00, "estado": "Completado"},
            {"pedido": "556785", "cliente": "Sergio Chaires", "producto": "PREGR07 - Azúcar Refinado Granulado 25kg", "cantidad": "3 sacos", "precio": 490.00, "total": 1470.00, "estado": "Completado"},
            {"pedido": "556786", "cliente": "Juan Manuel Rojas", "producto": "PESGR07 - Azúcar Estándar Granulado 25kg", "cantidad": "2 sacos", "precio": 375.00, "total": 750.00, "estado": "Completado"},
            {"pedido": "556787", "cliente": "David Muñoz", "producto": "PREGR07 - Azúcar Refinado Granulado 25kg", "cantidad": "10 sacos", "precio": 490.00, "total": 4900.00, "estado": "Completado"},
            {"pedido": "556793", "cliente": "Juan Huerta", "producto": "PESGR07 - Azúcar Estándar Granulado 25kg", "cantidad": "1 saco", "precio": 370.00, "total": 370.00, "estado": "Completado"},
            {"pedido": "556794", "cliente": "Juan Huerta", "producto": "PESEM17 - Azúcar Estándar Granulado C/10 Bolsas 2 LBS", "cantidad": "1 paquete", "precio": 149.00, "total": 149.00, "estado": "Completado"},
            {"pedido": "556795", "cliente": "Panadería Central", "producto": "PREGR07 - Azúcar Refinado Granulado 25kg", "cantidad": "10 sacos", "precio": 490.00, "total": 4900.00, "estado": "Pendiente"},
            {"pedido": "556795", "cliente": "Panadería Central", "producto": "PESGR07 - Azúcar Estándar Granulado 25kg", "cantidad": "5 sacos", "precio": 370.00, "total": 1850.00, "estado": "Pendiente"},
            {"pedido": "556795", "cliente": "Panadería Central", "producto": "PG3EN09 - Glucosa 43 Cubeta 27kg", "cantidad": "2 cubetas", "precio": 706.00, "total": 1412.00, "estado": "Pendiente"},
            {"pedido": "556798", "cliente": "Distribuidora Zucarmex", "producto": "PESGR07 - Azúcar Estándar Granulado 25kg", "cantidad": "5 sacos", "precio": 370.00, "total": 1850.00, "estado": "Completado"},
            {"pedido": "556798", "cliente": "Distribuidora Zucarmex", "producto": "PAL0007 - Almidón de Maíz 25kg", "cantidad": "2 sacos", "precio": 630.00, "total": 1260.00, "estado": "Completado"},
            {"pedido": "556799", "cliente": "Repostería Dulce", "producto": "PREGR07 - Azúcar Refinado Granulado 25kg", "cantidad": "2 sacos", "precio": 490.00, "total": 980.00, "estado": "Completado"},
            {"pedido": "556799", "cliente": "Repostería Dulce", "producto": "PREP107 - Azúcar Refinado Pulverizado 10X 25kg", "cantidad": "1 saco", "precio": 521.00, "total": 521.00, "estado": "Completado"},
            {"pedido": "556802", "cliente": "Confitería Royal", "producto": "PREGR07 - Azúcar Refinado Granulado 25kg", "cantidad": "8 sacos", "precio": 490.00, "total": 3920.00, "estado": "Completado"},
            {"pedido": "556803", "cliente": "Dulces Tradicionales", "producto": "PREP107 - Azúcar Refinado Pulverizado 10X 25kg", "cantidad": "3 sacos", "precio": 521.00, "total": 1563.00, "estado": "Completado"},
            {"pedido": "556804", "cliente": "Industria Gallo", "producto": "PG3EN09 - Glucosa 43 Cubeta 27kg", "cantidad": "5 cubetas", "precio": 706.00, "total": 3530.00, "estado": "Completado"},
            {"pedido": "556805", "cliente": "Panadería La Moderna", "producto": "PESGR07 - Azúcar Estándar Granulado 25kg", "cantidad": "15 sacos", "precio": 370.00, "total": 5550.00, "estado": "Completado"},
            {"pedido": "556806", "cliente": "Chocolates Finos", "producto": "DEXT001 - Dextrosa Monohidrato 25kg", "cantidad": "3 sacos", "precio": 210.00, "total": 630.00, "estado": "Completado"},
            {"pedido": "556807", "cliente": "Bebidas Refrescantes", "producto": "FRUCT01 - Fructosa Cristalina 25kg", "cantidad": "2 sacos", "precio": 300.00, "total": 600.00, "estado": "Pendiente"},
            {"pedido": "556808", "cliente": "Productos Naturales", "producto": "MALTO01 - Maltodextrina 25kg", "cantidad": "4 sacos", "precio": 300.00, "total": 1200.00, "estado": "Pendiente"},
            {"pedido": "556809", "cliente": "Alimentos Saludables", "producto": "SORB001 - Sorbitol Polvo 25kg", "cantidad": "2 sacos", "precio": 400.00, "total": 800.00, "estado": "Completado"},
            {"pedido": "556810", "cliente": "Supermercado del Norte", "producto": "PESEM10 - Azúcar Estándar C/5 Bolsas 2kg", "cantidad": "20 paquetes", "precio": 60.00, "total": 1200.00, "estado": "Completado"},
            {"pedido": "556811", "cliente": "Tienda de Conveniencia", "producto": "PRESEM5 - Azúcar Refinado C/5 Bolsas 1kg", "cantidad": "15 paquetes", "precio": 50.00, "total": 750.00, "estado": "Completado"},
            {"pedido": "556812", "cliente": "Cafetería Central", "producto": "PREGR01 - Azúcar Refinado Granulado 1kg", "cantidad": "25 sacos", "precio": 50.00, "total": 1250.00, "estado": "Completado"},
            {"pedido": "556813", "cliente": "Restaurante Gourmet", "producto": "PREGR05 - Azúcar Refinado Granulado 5kg", "cantidad": "8 sacos", "precio": 60.00, "total": 480.00, "estado": "Completado"},
            {"pedido": "556814", "cliente": "Panadería Artesanal", "producto": "PAL0001 - Almidón de Maíz 1kg", "cantidad": "12 sacos", "precio": 30.00, "total": 360.00, "estado": "Completado"},
            {"pedido": "556815", "cliente": "Repostería Especializada", "producto": "PAL0005 - Almidón de Maíz 5kg", "cantidad": "6 sacos", "precio": 60.00, "total": 360.00, "estado": "Pendiente"},
        ]
    
    def serve_template_file(self, file_path):
        """Serve template files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Template not found')
    
    def get_dashboard_html(self):
        """Generate the dashboard HTML with embedded styling"""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Sistema Cyberia (Demo)</title>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        /* Obsidian-inspired CSS Variables */
        :root {{
            --color-primary: #6366f1;
            --color-accent: #8b5cf6;
            --background-primary: #ffffff;
            --background-secondary: #f8fafc;
            --background-tertiary: #f1f5f9;
            --background-modifier-border: #e2e8f0;
            --text-normal: #1e293b;
            --text-muted: #64748b;
            --text-faint: #94a3b8;
            --text-accent: #6366f1;
            --text-error: #ef4444;
            --text-success: #22c55e;
            --text-warning: #f59e0b;
            --page-width: 1200px;
            --sidebar-left-width: 280px;
            --sidebar-right-width: 300px;
            --header-height: 60px;
            --page-side-padding: 24px;
            --font-text: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-size-normal: 16px;
            --font-size-small: 14px;
            --font-size-smaller: 12px;
            --font-weight-normal: 400;
            --font-weight-medium: 500;
            --font-weight-semibold: 600;
            --anim-duration-medium: 250ms;
            --anim-motion-smooth: cubic-bezier(0.4, 0, 0.2, 1);
            --shadow-s: 0 1px 2px rgba(0, 0, 0, 0.04);
            --shadow-m: 0 4px 8px rgba(0, 0, 0, 0.06);
            --shadow-l: 0 8px 24px rgba(0, 0, 0, 0.12);
        }}

        * {{ box-sizing: border-box; }}

        body {{
            margin: 0;
            font-family: var(--font-text);
            font-size: var(--font-size-normal);
            line-height: 1.6;
            color: var(--text-normal);
            background-color: var(--background-primary);
            transition: background-color var(--anim-duration-medium) var(--anim-motion-smooth);
        }}

        .app-container {{
            display: flex;
            min-height: 100vh;
            max-width: var(--page-width);
            margin: 0 auto;
        }}

        .sidebar-left {{
            width: var(--sidebar-left-width);
            background-color: var(--background-secondary);
            border-right: 1px solid var(--background-modifier-border);
            display: flex;
            flex-direction: column;
            padding: var(--page-side-padding);
        }}

        .main-content {{
            flex: 1;
            padding: var(--page-side-padding);
            min-width: 0;
        }}

        .sidebar-right {{
            width: var(--sidebar-right-width);
            background-color: var(--background-secondary);
            border-left: 1px solid var(--background-modifier-border);
            padding: var(--page-side-padding);
        }}

        .page-header {{
            margin-bottom: 32px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--background-modifier-border);
        }}

        .page-title {{
            font-size: 2.2em;
            font-weight: var(--font-weight-semibold);
            color: var(--text-normal);
            margin: 0;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }}

        .metric-card {{
            padding: 24px;
            border-radius: 12px;
            color: white;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-m);
        }}

        .metric-label {{
            font-size: var(--font-size-small);
            opacity: 0.9;
            margin-bottom: 8px;
        }}

        .metric-value {{
            font-size: 2.2em;
            font-weight: var(--font-weight-semibold);
            margin-bottom: 8px;
        }}

        .metric-change {{
            font-size: var(--font-size-smaller);
            opacity: 0.8;
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .metric-change svg {{
            width: 14px;
            height: 14px;
        }}

        .card {{
            background-color: var(--background-primary);
            border: 1px solid var(--background-modifier-border);
            border-radius: 12px;
            padding: 24px;
            box-shadow: var(--shadow-s);
            margin-bottom: 24px;
        }}

        .card-header {{
            margin-bottom: 20px;
        }}

        .card-title {{
            font-size: 1.1em;
            font-weight: var(--font-weight-semibold);
            color: var(--text-normal);
            margin: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .card-title svg {{
            width: 20px;
            height: 20px;
            color: var(--text-accent);
        }}

        .chart-container {{
            position: relative;
            height: 300px;
        }}

        .sidebar-section {{
            margin-bottom: 32px;
        }}

        .sidebar-section-title {{
            font-size: var(--font-size-small);
            font-weight: var(--font-weight-semibold);
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .sidebar-section-title svg {{
            width: 16px;
            height: 16px;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 16px;
            background-color: var(--color-primary);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: var(--font-size-small);
            font-weight: var(--font-weight-medium);
            transition: all var(--anim-duration-medium) var(--anim-motion-smooth);
            border: none;
            cursor: pointer;
        }}

        .btn:hover {{
            background-color: var(--color-accent);
            transform: translateY(-1px);
            box-shadow: var(--shadow-m);
        }}

        .btn svg {{
            width: 16px;
            height: 16px;
        }}

        .status-indicator {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .status-success {{ background-color: var(--text-success); }}
        .status-warning {{ background-color: var(--text-warning); }}
        .status-error {{ background-color: var(--text-error); }}

        /* Demo banner */
        .demo-banner {{
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            text-align: center;
            padding: 12px;
            font-size: var(--font-size-small);
            font-weight: var(--font-weight-medium);
        }}

        /* Responsive design */
        @media (max-width: 1024px) {{
            .app-container {{ flex-direction: column; }}
            .sidebar-left, .sidebar-right {{ 
                width: 100%; 
                border: none;
                border-bottom: 1px solid var(--background-modifier-border);
            }}
            .metrics-grid {{ grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }}
        }}
    </style>
</head>
<body>
    <div class="demo-banner">
        🚀 Cyberia FastAPI Demo - Datos Simulados • Estilo Obsidian Publish
    </div>
    
    <div class="app-container">
        <!-- Left Sidebar -->
        <div class="sidebar-left">
            <div class="sidebar-section">
                <div class="sidebar-section-title">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/>
                    </svg>
                    Dashboard
                </div>
                <nav>
                    <a href="#" class="btn" style="justify-content: flex-start; margin-bottom: 8px; background-color: var(--background-tertiary); color: var(--text-accent);">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z"/>
                        </svg>
                        Dashboard
                    </a>
                    <a href="/productos" class="btn" style="justify-content: flex-start; margin-bottom: 8px; background-color: transparent; color: var(--text-muted); border: 1px solid var(--background-modifier-border);">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"/>
                        </svg>
                        Productos
                    </a>
                    <a href="/ventas" class="btn" style="justify-content: flex-start; margin-bottom: 8px; background-color: transparent; color: var(--text-muted); border: 1px solid var(--background-modifier-border);">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/>
                        </svg>
                        Ventas
                    </a>
                </nav>
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="page-header">
                <h1 class="page-title">Dashboard Ejecutivo</h1>
            </div>

            <!-- Métricas Principales -->
            <div class="metrics-grid" id="metricsGrid">
                <!-- Las métricas se cargarán dinámicamente aquí -->
            </div>

            <!-- Gráficos -->
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px; margin-bottom: 32px;">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 010 5.814 3.75 3.75 0 01-5.596 2.058"/>
                            </svg>
                            Tendencia de Ventas Mensuales
                        </h3>
                    </div>
                    <div class="chart-container">
                        <canvas id="monthlySalesChart"></canvas>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6a7.5 7.5 0 107.5 7.5h-7.5V6z"/>
                            </svg>
                            Distribución por Tipo
                        </h3>
                    </div>
                    <div class="chart-container">
                        <canvas id="salesByTypeChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Top Performers -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px;">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872"/>
                            </svg>
                            Top Agentes de Ventas
                        </h3>
                    </div>
                    <div id="topAgents">
                        <!-- Los agentes se cargarán aquí -->
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988"/>
                            </svg>
                            Productos Estrella
                        </h3>
                    </div>
                    <div id="topProducts">
                        <!-- Los productos se cargarán aquí -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Sidebar -->
        <div class="sidebar-right">
            <div class="sidebar-section">
                <div class="sidebar-section-title">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853"/>
                    </svg>
                    Estado del Sistema
                </div>
                <div id="systemStatus">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div class="status-indicator status-success"></div>
                        <span style="font-size: var(--font-size-small);">Demo activo</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div class="status-indicator status-success"></div>
                        <span style="font-size: var(--font-size-small);">Servidor funcionando</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div class="status-indicator status-warning"></div>
                        <span style="font-size: var(--font-size-small);" id="lastUpdateText">Datos simulados</span>
                    </div>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75"/>
                    </svg>
                    Métricas Rápidas
                </div>
                <div id="quickMetrics">
                    <!-- Métricas rápidas se cargarán aquí -->
                </div>
            </div>
        </div>
    </div>

    <script>
        let monthlySalesChart, salesByTypeChart;

        // Utilidades para formateo
        const utils = {{
            formatNumber: function(num) {{
                return new Intl.NumberFormat('es-MX').format(num);
            }},
            formatCurrency: function(amount) {{
                if (amount >= 1000000) {{
                    return (amount / 1000000).toFixed(1) + 'M';
                }} else if (amount >= 1000) {{
                    return (amount / 1000).toFixed(0) + 'K';
                }}
                return new Intl.NumberFormat('es-MX', {{
                    style: 'currency',
                    currency: 'MXN'
                }}).format(amount);
            }},
            showToast: function(message, type) {{
                console.log(`${{type.toUpperCase()}}: ${{message}}`);
            }}
        }};

        // API service
        const apiService = {{
            async get(url) {{
                try {{
                    const response = await fetch(url);
                    return await response.json();
                }} catch (error) {{
                    console.error('API Error:', error);
                    throw error;
                }}
            }}
        }};

        // Dashboard service
        const dashboardService = {{
            async getMetrics() {{
                return await apiService.get('/api/analytics/dashboard-metrics');
            }}
        }};

        // Initialize dashboard
        async function initDashboard() {{
            try {{
                const metrics = await dashboardService.getMetrics();
                renderMetrics(metrics);
                renderCharts(metrics);
                renderTopPerformers(metrics);
                renderQuickMetrics(metrics);
                updateLastUpdateTime();
                
                utils.showToast('Dashboard cargado exitosamente', 'success');
            }} catch (error) {{
                console.error('Error loading dashboard:', error);
                utils.showToast('Error al cargar el dashboard', 'error');
            }}
        }}

        // Render key metrics
        function renderMetrics(data) {{
            const metricsGrid = document.getElementById('metricsGrid');
            
            // Función para obtener color e ícono según el cambio
            function getChangeIndicator(changeValue) {{
                if (changeValue > 0) {{
                    return {{
                        color: '#22c55e',
                        icon: 'M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 010 5.814 3.75 3.75 0 01-5.596 2.058',
                        symbol: '▲'
                    }};
                }} else if (changeValue < 0) {{
                    return {{
                        color: '#ef4444',
                        icon: 'M2.25 6L9 12.75l4.306-4.307a11.95 11.95 0 015.814 0 3.75 3.75 0 01-1.232 6.832',
                        symbol: '▼'
                    }};
                }} else {{
                    return {{
                        color: '#f59e0b',
                        icon: 'M5 12h14',
                        symbol: '━'
                    }};
                }}
            }}
            
            const salesChange = getChangeIndicator(data.sales_change_pct);
            const ordersChange = getChangeIndicator(data.orders_change_pct);
            const avgOrderChange = getChangeIndicator(data.avg_order_change_pct);
            
            const metricsHtml = `
                <div class="metric-card" style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">
                    <div class="metric-label">Ventas Mes Actual</div>
                    <div class="metric-value">${{data.current_month_sales}}</div>
                    <div class="metric-change" style="color: ${{salesChange.color}};">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="${{salesChange.icon}}"/>
                        </svg>
                        ${{salesChange.symbol}} ${{data.sales_change_pct ? Math.abs(data.sales_change_pct).toFixed(1) + '%' : 'N/A'}} vs mes anterior
                    </div>
                </div>
                
                <div class="metric-card" style="background: linear-gradient(135deg, #ec4899, #f97316);">
                    <div class="metric-label">Órdenes Mes Actual</div>
                    <div class="metric-value">${{utils.formatNumber(data.current_month_orders)}}</div>
                    <div class="metric-change" style="color: ${{ordersChange.color}};">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="${{ordersChange.icon}}"/>
                        </svg>
                        ${{ordersChange.symbol}} ${{data.orders_change_pct ? Math.abs(data.orders_change_pct).toFixed(1) + '%' : 'N/A'}} vs mes anterior
                    </div>
                </div>
                
                <div class="metric-card" style="background: linear-gradient(135deg, #06b6d4, #3b82f6);">
                    <div class="metric-label">Ventas Año a la Fecha</div>
                    <div class="metric-value">${{data.ytd_sales}}</div>
                    <div class="metric-change" style="color: rgba(255, 255, 255, 0.8);">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5a2.25 2.25 0 002.25-2.25"/>
                        </svg>
                        Total acumulado ${{new Date().getFullYear()}}
                    </div>
                </div>
                
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981, #059669);">
                    <div class="metric-label">Orden Promedio</div>
                    <div class="metric-value">${{utils.formatCurrency(data.current_avg_order)}}</div>
                    <div class="metric-change" style="color: ${{avgOrderChange.color}};">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="${{avgOrderChange.icon}}"/>
                        </svg>
                        ${{avgOrderChange.symbol}} ${{data.avg_order_change_pct ? Math.abs(data.avg_order_change_pct).toFixed(1) + '%' : 'N/A'}} vs mes anterior
                    </div>
                </div>
            `;
            
            metricsGrid.innerHTML = metricsHtml;
        }}

        // Render charts
        function renderCharts(data) {{
            // Monthly Sales Chart
            const ctxMonthlySales = document.getElementById('monthlySalesChart').getContext('2d');
            
            if (monthlySalesChart) {{
                monthlySalesChart.destroy();
            }}
            
            monthlySalesChart = new Chart(ctxMonthlySales, {{
                type: 'line',
                data: {{
                    labels: data.monthly_sales.map(item => item.month_name),
                    datasets: [{{
                        label: 'Ventas Mensuales',
                        data: data.monthly_sales.map(item => item.total_sales),
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#6366f1',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            titleColor: '#f1f5f9',
                            bodyColor: '#f1f5f9',
                            borderColor: '#475569',
                            borderWidth: 1,
                            cornerRadius: 8,
                            callbacks: {{
                                label: function(context) {{
                                    return `Ventas: ${{utils.formatCurrency(context.parsed.y)}}`;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            grid: {{ color: 'rgba(71, 85, 105, 0.1)' }},
                            ticks: {{ color: '#64748b' }}
                        }},
                        y: {{
                            beginAtZero: true,
                            grid: {{ color: 'rgba(71, 85, 105, 0.1)' }},
                            ticks: {{
                                color: '#64748b',
                                callback: function(value) {{
                                    return utils.formatCurrency(value);
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Sales by Type Chart
            const ctxSalesByType = document.getElementById('salesByTypeChart').getContext('2d');
            
            if (salesByTypeChart) {{
                salesByTypeChart.destroy();
            }}
            
            const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f97316', '#06b6d4', '#10b981'];
            
            salesByTypeChart = new Chart(ctxSalesByType, {{
                type: 'doughnut',
                data: {{
                    labels: data.sales_by_type.map(item => item.order_type),
                    datasets: [{{
                        data: data.sales_by_type.map(item => item.total_sales),
                        backgroundColor: colors,
                        borderWidth: 0,
                        hoverBorderWidth: 2,
                        hoverBorderColor: '#ffffff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                padding: 20,
                                usePointStyle: true,
                                color: '#64748b'
                            }}
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            titleColor: '#f1f5f9',
                            bodyColor: '#f1f5f9',
                            borderColor: '#475569',
                            borderWidth: 1,
                            cornerRadius: 8,
                            callbacks: {{
                                label: function(context) {{
                                    return `${{context.label}}: ${{utils.formatCurrency(context.parsed)}}`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        // Render top performers
        function renderTopPerformers(data) {{
            // Top Agents
            const topAgentsHtml = data.top_agents.map((agent, index) => `
                <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--background-modifier-border);">
                    <div style="
                        width: 32px; 
                        height: 32px; 
                        background: linear-gradient(135deg, #6366f1, #8b5cf6); 
                        color: white; 
                        border-radius: 50%; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        font-weight: var(--font-weight-semibold);
                        font-size: var(--font-size-small);
                        margin-right: 12px;
                    ">${{index + 1}}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: var(--font-weight-medium); color: var(--text-normal); margin-bottom: 2px;">
                            ${{agent.agent_name}}
                        </div>
                        <div style="font-size: var(--font-size-smaller); color: var(--text-muted);">
                            ${{agent.agent_code}} • ${{agent.total_orders}} órdenes
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: var(--font-weight-semibold); color: var(--text-normal);">
                            ${{utils.formatCurrency(agent.total_sales)}}
                        </div>
                    </div>
                </div>
            `).join('');
            
            document.getElementById('topAgents').innerHTML = topAgentsHtml;
            
            // Top Products
            const topProductsHtml = data.top_products.map((product, index) => `
                <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--background-modifier-border);">
                    <div style="
                        width: 32px; 
                        height: 32px; 
                        background: linear-gradient(135deg, #10b981, #059669); 
                        color: white; 
                        border-radius: 50%; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        font-weight: var(--font-weight-semibold);
                        font-size: var(--font-size-small);
                        margin-right: 12px;
                    ">${{index + 1}}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: var(--font-weight-medium); color: var(--text-normal); margin-bottom: 2px;">
                            ${{product.product_name}}
                        </div>
                        <div style="font-size: var(--font-size-smaller); color: var(--text-muted);">
                            <code>${{product.product_code}}</code> • ${{utils.formatNumber(product.total_quantity)}} kg
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: var(--font-weight-semibold); color: var(--text-normal);">
                            ${{utils.formatCurrency(product.total_sales)}}
                        </div>
                    </div>
                </div>
            `).join('');
            
            document.getElementById('topProducts').innerHTML = topProductsHtml;
        }}

        // Render quick metrics in sidebar
        function renderQuickMetrics(data) {{
            const quickMetricsHtml = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 12px; background-color: var(--background-secondary); border-radius: 8px;">
                    <div>
                        <div style="font-size: var(--font-size-smaller); color: var(--text-muted);">Clientes Activos</div>
                        <div style="font-weight: var(--font-weight-semibold); color: var(--text-normal);">${{utils.formatNumber(data.total_customers)}}</div>
                    </div>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 24px; height: 24px; color: var(--text-accent);">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952"/>
                    </svg>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 12px; background-color: var(--background-secondary); border-radius: 8px;">
                    <div>
                        <div style="font-size: var(--font-size-smaller); color: var(--text-muted);">Productos MYA</div>
                        <div style="font-weight: var(--font-weight-semibold); color: var(--text-normal); display: flex; align-items: center; gap: 4px;">
                            ${{utils.formatNumber(data.total_products)}}
                            <span style="font-size: 10px; background-color: var(--color-accent); color: white; padding: 2px 6px; border-radius: 10px;">REAL</span>
                        </div>
                    </div>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 24px; height: 24px; color: var(--text-accent);">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"/>
                    </svg>
                </div>
            `;
            
            document.getElementById('quickMetrics').innerHTML = quickMetricsHtml;
        }}

        // Update last update time
        function updateLastUpdateTime() {{
            const now = new Date();
            const timeString = now.toLocaleTimeString('es-MX', {{ 
                hour: '2-digit', 
                minute: '2-digit' 
            }});
            
            document.getElementById('lastUpdateText').textContent = `Última actualización: ${{timeString}}`;
        }}

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', initDashboard);
    </script>
</body>
</html>"""

    def get_products_html(self):
        """Generate products page HTML"""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Productos - Sistema Cyberia (Demo)</title>
    <style>
        /* Base styles from dashboard */
        :root {{
            --color-primary: #6366f1;
            --color-accent: #8b5cf6;
            --background-primary: #ffffff;
            --background-secondary: #f8fafc;
            --background-tertiary: #f1f5f9;
            --background-modifier-border: #e2e8f0;
            --text-normal: #1e293b;
            --text-muted: #64748b;
            --text-accent: #6366f1;
            --text-success: #22c55e;
            --font-text: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-size-normal: 16px;
            --font-size-small: 14px;
            --font-weight-medium: 500;
            --font-weight-semibold: 600;
        }}
        
        * {{ box-sizing: border-box; }}
        
        body {{
            margin: 0;
            font-family: var(--font-text);
            font-size: var(--font-size-normal);
            line-height: 1.6;
            color: var(--text-normal);
            background-color: var(--background-primary);
            padding: 24px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            margin-bottom: 32px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--background-modifier-border);
        }}
        
        .page-title {{
            font-size: 2.2em;
            font-weight: var(--font-weight-semibold);
            color: var(--text-normal);
            margin: 0;
        }}
        
        .nav-links {{
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .nav-link {{
            padding: 8px 16px;
            text-decoration: none;
            color: var(--text-muted);
            border-radius: 6px;
            transition: all 0.2s;
        }}
        
        .nav-link:hover {{
            background-color: var(--background-secondary);
            color: var(--text-normal);
        }}
        
        .nav-link.active {{
            background-color: var(--color-primary);
            color: white;
        }}
        
        .products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 24px;
        }}
        
        .product-card {{
            background: white;
            border: 1px solid var(--background-modifier-border);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .product-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }}
        
        .product-code {{
            font-family: monospace;
            font-size: var(--font-size-small);
            background-color: var(--background-secondary);
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 8px;
        }}
        
        .product-name {{
            font-size: 1.1em;
            font-weight: var(--font-weight-medium);
            margin-bottom: 8px;
        }}
        
        .product-category {{
            color: var(--text-muted);
            font-size: var(--font-size-small);
            margin-bottom: 12px;
        }}
        
        .product-stats {{
            display: flex;
            justify-content: space-between;
            font-size: var(--font-size-small);
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-weight: var(--font-weight-semibold);
            color: var(--text-normal);
        }}
        
        .stat-label {{
            color: var(--text-muted);
        }}
        
        .demo-banner {{
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            text-align: center;
            padding: 12px;
            font-size: var(--font-size-small);
            font-weight: var(--font-weight-medium);
            margin-bottom: 24px;
        }}
    </style>
</head>
<body>
    <div class="demo-banner">
        🛍️ Productos MYA - Azúcares, Glucosa y Almidón de Maíz
    </div>
    
    <div class="container">
        <div class="header">
            <h1 class="page-title">Catálogo de Productos</h1>
            <div class="nav-links">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/productos" class="nav-link active">📦 Productos</a>
                <a href="/ventas" class="nav-link">📊 Ventas</a>
            </div>
        </div>
        
        <div class="products-grid" id="productsGrid">
            <!-- Los productos se cargarán dinámicamente aquí -->
        </div>
    </div>
    
    <script>
        // Utilidades para formateo
        function formatNumber(num) {{
            return new Intl.NumberFormat('es-MX').format(num);
        }}
        
        function formatCurrency(amount) {{
            if (amount >= 1000000) {{
                return (amount / 1000000).toFixed(1) + 'M';
            }} else if (amount >= 1000) {{
                return (amount / 1000).toFixed(0) + 'K';
            }}
            return new Intl.NumberFormat('es-MX', {{
                style: 'currency',
                currency: 'MXN'
            }}).format(amount);
        }}
        
        function calculatePrice(product) {{
            if (product.total_sales > 0 && product.total_quantity > 0) {{
                return product.total_sales / product.total_quantity;
            }}
            return 0;
        }}
        
        // Cargar productos dinámicamente
        async function loadProducts() {{
            try {{
                const response = await fetch('/api/productos');
                const products = await response.json();
                
                const productsGrid = document.getElementById('productsGrid');
                productsGrid.innerHTML = '';
                
                products.forEach(product => {{
                    const price = calculatePrice(product);
                    const productCard = `
                        <div class="product-card">
                            <div class="product-code">${{product.product_code}}</div>
                            <div class="product-name">${{product.product_name}}</div>
                            <div class="product-category">${{product.category}}</div>
                            <div class="product-stats">
                                <div class="stat">
                                    <div class="stat-value">${{formatNumber(product.total_quantity)}}</div>
                                    <div class="stat-label">Kg Vendidos</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-value">${{formatCurrency(price)}}</div>
                                    <div class="stat-label">Precio Est.</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-value">${{formatCurrency(product.total_sales)}}</div>
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
                document.getElementById('productsGrid').innerHTML = '<p>Error al cargar productos</p>';
            }}
        }}
        
        // Cargar productos al iniciar la página
        document.addEventListener('DOMContentLoaded', loadProducts);
    </script>
</body>
</html>"""

    def get_sales_html(self):
        """Generate sales page HTML"""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ventas - Sistema Cyberia (Demo)</title>
    <style>
        /* Base styles from dashboard */
        :root {{
            --color-primary: #6366f1;
            --color-accent: #8b5cf6;
            --background-primary: #ffffff;
            --background-secondary: #f8fafc;
            --background-tertiary: #f1f5f9;
            --background-modifier-border: #e2e8f0;
            --text-normal: #1e293b;
            --text-muted: #64748b;
            --text-accent: #6366f1;
            --text-success: #22c55e;
            --font-text: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-size-normal: 16px;
            --font-size-small: 14px;
            --font-weight-medium: 500;
            --font-weight-semibold: 600;
        }}
        
        * {{ box-sizing: border-box; }}
        
        body {{
            margin: 0;
            font-family: var(--font-text);
            font-size: var(--font-size-normal);
            line-height: 1.6;
            color: var(--text-normal);
            background-color: var(--background-primary);
            padding: 24px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            margin-bottom: 32px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--background-modifier-border);
        }}
        
        .page-title {{
            font-size: 2.2em;
            font-weight: var(--font-weight-semibold);
            color: var(--text-normal);
            margin: 0;
        }}
        
        .nav-links {{
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .nav-link {{
            padding: 8px 16px;
            text-decoration: none;
            color: var(--text-muted);
            border-radius: 6px;
            transition: all 0.2s;
        }}
        
        .nav-link:hover {{
            background-color: var(--background-secondary);
            color: var(--text-normal);
        }}
        
        .nav-link.active {{
            background-color: var(--color-primary);
            color: white;
        }}
        
        .sales-table {{
            background: white;
            border: 1px solid var(--background-modifier-border);
            border-radius: 12px;
            overflow: hidden;
        }}
        
        .sales-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .sales-table th {{
            background-color: var(--background-secondary);
            padding: 12px;
            text-align: left;
            font-weight: var(--font-weight-semibold);
            color: var(--text-normal);
            border-bottom: 1px solid var(--background-modifier-border);
        }}
        
        .sales-table td {{
            padding: 12px;
            border-bottom: 1px solid var(--background-modifier-border);
        }}
        
        .sales-table tr:hover {{
            background-color: var(--background-tertiary);
        }}
        
        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: var(--font-size-small);
            font-weight: var(--font-weight-medium);
        }}
        
        .status-completed {{
            background-color: rgba(34, 197, 94, 0.1);
            color: var(--text-success);
        }}
        
        .status-pending {{
            background-color: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
        }}
        
        .demo-banner {{
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            text-align: center;
            padding: 12px;
            font-size: var(--font-size-small);
            font-weight: var(--font-weight-medium);
            margin-bottom: 24px;
        }}
    </style>
</head>
<body>
    <div class="demo-banner">
        📊 Ventas MYA - Pedidos y Facturación
    </div>
    
    <div class="container">
        <div class="header">
            <h1 class="page-title">Gestión de Ventas</h1>
            <div class="nav-links">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/productos" class="nav-link">📦 Productos</a>
                <a href="/ventas" class="nav-link active">📊 Ventas</a>
            </div>
        </div>
        
        <div class="sales-table">
            <table>
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
                    <tr>
                        <td>556773</td>
                        <td>Helados Eliza</td>
                        <td>PREGR07 - Azúcar Refinado Granulado 25kg</td>
                        <td>2 sacos</td>
                        <td>$490.00</td>
                        <td>$980.00</td>
                        <td><span class="status-badge status-completed">Completado</span></td>
                    </tr>
                    <tr>
                        <td>556774</td>
                        <td>Jorge Tamez</td>
                        <td>PESGR07 - Azúcar Estándar Granulado 25kg</td>
                        <td>4 sacos</td>
                        <td>$370.00</td>
                        <td>$1,480.00</td>
                        <td><span class="status-badge status-completed">Completado</span></td>
                    </tr>
                    <tr>
                        <td>556775</td>
                        <td>Sergio Chaires</td>
                        <td>PESGR07 - Azúcar Estándar Granulado 25kg</td>
                        <td>4 sacos</td>
                        <td>$370.00</td>
                        <td>$1,480.00</td>
                        <td><span class="status-badge status-completed">Completado</span></td>
                    </tr>
                    <tr>
                        <td>556795</td>
                        <td>Panadería Central</td>
                        <td>PREGR07 - Azúcar Refinado Granulado 25kg</td>
                        <td>10 sacos</td>
                        <td>$490.00</td>
                        <td>$4,900.00</td>
                        <td><span class="status-badge status-pending">Pendiente</span></td>
                    </tr>
                    <tr>
                        <td>556795</td>
                        <td>Panadería Central</td>
                        <td>PESGR07 - Azúcar Estándar Granulado 25kg</td>
                        <td>5 sacos</td>
                        <td>$370.00</td>
                        <td>$1,850.00</td>
                        <td><span class="status-badge status-pending">Pendiente</span></td>
                    </tr>
                    <tr>
                        <td>556795</td>
                        <td>Panadería Central</td>
                        <td>PG3EN09 - Glucosa 43 Cubeta 27kg</td>
                        <td>2 cubetas</td>
                        <td>$706.00</td>
                        <td>$1,412.00</td>
                        <td><span class="status-badge status-pending">Pendiente</span></td>
                    </tr>
                    <tr>
                        <td>556798</td>
                        <td>Distribuidora Zucarmex</td>
                        <td>PESGR07 - Azúcar Estándar Granulado 25kg</td>
                        <td>5 sacos</td>
                        <td>$370.00</td>
                        <td>$1,850.00</td>
                        <td><span class="status-badge status-completed">Completado</span></td>
                    </tr>
                    <tr>
                        <td>556798</td>
                        <td>Distribuidora Zucarmex</td>
                        <td>PAL0007 - Almidón de Maíz 25kg</td>
                        <td>2 sacos</td>
                        <td>$630.00</td>
                        <td>$1,260.00</td>
                        <td><span class="status-badge status-completed">Completado</span></td>
                    </tr>
                    <tr>
                        <td>556799</td>
                        <td>Repostería Dulce</td>
                        <td>PREGR07 - Azúcar Refinado Granulado 25kg</td>
                        <td>2 sacos</td>
                        <td>$490.00</td>
                        <td>$980.00</td>
                        <td><span class="status-badge status-completed">Completado</span></td>
                    </tr>
                    <tr>
                        <td>556799</td>
                        <td>Repostería Dulce</td>
                        <td>PREP107 - Azúcar Refinado Pulverizado 10X 25kg</td>
                        <td>1 saco</td>
                        <td>$521.00</td>
                        <td>$521.00</td>
                        <td><span class="status-badge status-completed">Completado</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""

def main():
    print("🚀 Iniciando Cyberia Simple Demo...")
    print("📊 Usando datos simulados (sin dependencias externas)")
    print(f"🌐 Servidor disponible en: http://localhost:{PORT}")
    print("🎨 Estilo inspirado en Obsidian Publish")
    print("💡 Dashboard con métricas en formato millones")
    print("⚡ Sin FastAPI - servidor HTTP nativo de Python")
    print()
    print("Para probar el API:")
    print(f"  curl http://localhost:{PORT}/api/analytics/dashboard-metrics")
    print(f"  curl http://localhost:{PORT}/health")
    print()
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        with socketserver.TCPServer(("", PORT), CyberiaHTTPRequestHandler) as httpd:
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