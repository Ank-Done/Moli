#!/usr/bin/env python3
"""
CYBERIA SQL DEMO - CON BASE DE DATOS REAL
Sistema de Inteligencia Empresarial para Moliendas y Alimentos
Conectado a Microsoft SQL Server
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime
import os
import sys
import pyodbc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Puerto del servidor
PORT = 8002

# Configuración de base de datos
DB_CONFIG = {
    'server': 'localhost',  # Cambiar si es necesario
    'database': 'Cyberia',
    'username': 'SA',
    'password': 'Mar120305!',
    'driver': '{FreeTDS}'  # Usar FreeTDS en Linux
}

class CyberiaSQLHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db_connection = None
        super().__init__(*args, **kwargs)
    
    def get_db_connection(self):
        """Obtener conexión a la base de datos"""
        if self.db_connection is None:
            try:
                connection_string = (
                    f"DRIVER={DB_CONFIG['driver']};"
                    f"SERVER={DB_CONFIG['server']};"
                    f"DATABASE={DB_CONFIG['database']};"
                    f"UID={DB_CONFIG['username']};"
                    f"PWD={DB_CONFIG['password']}"
                )
                self.db_connection = pyodbc.connect(connection_string)
                logger.info("✅ Conexión a SQL Server establecida")
            except Exception as e:
                logger.error(f"❌ Error conectando a SQL Server: {e}")
                self.db_connection = None
        return self.db_connection
    
    def execute_query(self, query, params=None):
        """Ejecutar consulta SQL"""
        try:
            conn = self.get_db_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Error ejecutando consulta: {e}")
            return []
    
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
                "database": "Microsoft SQL Server - Cyberia",
                "service": "Cyberia SQL Demo v1.0.0"
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
        """Obtener métricas del dashboard desde SQL Server"""
        try:
            # Consulta para obtener métricas básicas
            query = """
            SELECT 
                COUNT(*) as total_products,
                SUM(CASE WHEN MONTH(fecha_venta) = MONTH(GETDATE()) AND YEAR(fecha_venta) = YEAR(GETDATE()) THEN total_venta ELSE 0 END) as current_month_sales,
                COUNT(CASE WHEN MONTH(fecha_venta) = MONTH(GETDATE()) AND YEAR(fecha_venta) = YEAR(GETDATE()) THEN 1 END) as current_month_orders,
                SUM(CASE WHEN YEAR(fecha_venta) = YEAR(GETDATE()) THEN total_venta ELSE 0 END) as ytd_sales,
                AVG(CASE WHEN MONTH(fecha_venta) = MONTH(GETDATE()) AND YEAR(fecha_venta) = YEAR(GETDATE()) THEN total_venta END) as current_avg_order
            FROM productos p
            LEFT JOIN ventas v ON p.producto_id = v.producto_id
            WHERE p.activo = 1
            """
            
            result = self.execute_query(query)
            
            if result:
                data = result[0]
                return {
                    "current_month_sales": self.format_currency_millions(data.get('current_month_sales', 0)),
                    "current_month_orders": data.get('current_month_orders', 0),
                    "current_avg_order": data.get('current_avg_order', 0) or 0,
                    "ytd_sales": self.format_currency_millions(data.get('ytd_sales', 0)),
                    "total_customers": self.get_total_customers(),
                    "total_products": data.get('total_products', 0),
                    "sales_change_pct": 12.5,  # Calcular cambio real
                    "orders_change_pct": -3.2,  # Calcular cambio real
                    "avg_order_change_pct": 8.1,  # Calcular cambio real
                    "monthly_sales": self.get_monthly_sales(),
                    "sales_by_type": self.get_sales_by_type(),
                    "top_agents": self.get_top_agents(),
                    "top_products": self.get_top_products(),
                    "worst_products": self.get_worst_products()
                }
            else:
                return {"error": "No se pudieron obtener las métricas"}
                
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}")
            return {"error": str(e)}
    
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
    
    def get_total_customers(self):
        """Obtener total de clientes"""
        query = "SELECT COUNT(*) as total FROM clientes WHERE activo = 1"
        result = self.execute_query(query)
        return result[0]['total'] if result else 0
    
    def get_monthly_sales(self):
        """Obtener ventas mensuales"""
        query = """
        SELECT 
            MONTH(fecha_venta) as month,
            YEAR(fecha_venta) as year,
            DATENAME(MONTH, fecha_venta) as month_name,
            SUM(total_venta) as total_sales
        FROM ventas 
        WHERE YEAR(fecha_venta) = YEAR(GETDATE())
        GROUP BY MONTH(fecha_venta), YEAR(fecha_venta), DATENAME(MONTH, fecha_venta)
        ORDER BY MONTH(fecha_venta)
        """
        result = self.execute_query(query)
        return result if result else []
    
    def get_sales_by_type(self):
        """Obtener ventas por tipo"""
        query = """
        SELECT 
            tipo_venta as order_type,
            SUM(total_venta) as total_sales
        FROM ventas 
        WHERE YEAR(fecha_venta) = YEAR(GETDATE())
        GROUP BY tipo_venta
        ORDER BY total_sales DESC
        """
        result = self.execute_query(query)
        return result if result else []
    
    def get_top_agents(self):
        """Obtener top agentes de ventas"""
        query = """
        SELECT TOP 5
            a.agente_codigo as agent_code,
            a.nombre as agent_name,
            SUM(v.total_venta) as total_sales,
            COUNT(v.venta_id) as total_orders
        FROM agentes a
        INNER JOIN ventas v ON a.agente_id = v.agente_id
        WHERE YEAR(v.fecha_venta) = YEAR(GETDATE())
        GROUP BY a.agente_codigo, a.nombre
        ORDER BY total_sales DESC
        """
        result = self.execute_query(query)
        return result if result else []
    
    def get_top_products(self):
        """Obtener top productos"""
        query = """
        SELECT TOP 5
            p.producto_codigo as product_code,
            p.nombre as product_name,
            SUM(v.cantidad) as total_quantity,
            SUM(v.total_venta) as total_sales,
            c.nombre as category
        FROM productos p
        INNER JOIN ventas v ON p.producto_id = v.producto_id
        LEFT JOIN categorias c ON p.categoria_id = c.categoria_id
        WHERE YEAR(v.fecha_venta) = YEAR(GETDATE())
        GROUP BY p.producto_codigo, p.nombre, c.nombre
        ORDER BY total_sales DESC
        """
        result = self.execute_query(query)
        return result if result else []
    
    def get_worst_products(self):
        """Obtener productos con peor rendimiento"""
        query = """
        SELECT TOP 5
            p.producto_codigo as product_code,
            p.nombre as product_name,
            SUM(v.cantidad) as total_quantity,
            SUM(v.total_venta) as total_sales,
            AVG(v.margen_porcentaje) as avg_margin,
            c.nombre as category
        FROM productos p
        INNER JOIN ventas v ON p.producto_id = v.producto_id
        LEFT JOIN categorias c ON p.categoria_id = c.categoria_id
        WHERE YEAR(v.fecha_venta) = YEAR(GETDATE())
        GROUP BY p.producto_codigo, p.nombre, c.nombre
        ORDER BY total_sales ASC
        """
        result = self.execute_query(query)
        return result if result else []
    
    def get_all_products(self):
        """Obtener todos los productos desde SQL Server"""
        query = """
        SELECT 
            p.producto_id,
            p.producto_codigo as product_code,
            p.nombre as product_name,
            c.nombre as category,
            p.unidad as unit,
            p.precio_venta as price,
            p.activo as is_active,
            COALESCE(SUM(v.cantidad), 0) as total_quantity,
            COALESCE(SUM(v.total_venta), 0) as total_sales
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.categoria_id
        LEFT JOIN ventas v ON p.producto_id = v.producto_id AND YEAR(v.fecha_venta) = YEAR(GETDATE())
        WHERE p.activo = 1
        GROUP BY p.producto_id, p.producto_codigo, p.nombre, c.nombre, p.unidad, p.precio_venta, p.activo
        ORDER BY total_sales DESC
        """
        result = self.execute_query(query)
        return result if result else []
    
    def get_all_sales(self):
        """Obtener todas las ventas desde SQL Server"""
        query = """
        SELECT TOP 50
            v.venta_id as pedido,
            c.nombre as cliente,
            p.producto_codigo + ' - ' + p.nombre as producto,
            CAST(v.cantidad as VARCHAR) + ' ' + p.unidad as cantidad,
            v.precio_unitario as precio,
            v.total_venta as total,
            v.estado as estado
        FROM ventas v
        INNER JOIN productos p ON v.producto_id = p.producto_id
        INNER JOIN clientes c ON v.cliente_id = c.cliente_id
        WHERE YEAR(v.fecha_venta) = YEAR(GETDATE())
        ORDER BY v.fecha_venta DESC
        """
        result = self.execute_query(query)
        return result if result else []
    
    def serve_dashboard(self):
        """Serve the dashboard HTML"""
        dashboard_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Sistema Cyberia SQL</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .banner { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; text-align: center; padding: 12px; margin-bottom: 20px; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; }
        .nav a { padding: 8px 16px; background: #f0f0f0; text-decoration: none; color: #333; border-radius: 4px; }
        .nav a:hover { background: #e0e0e0; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #6366f1; }
        .metric-label { color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="banner">🗄️ Cyberia SQL Dashboard - Microsoft SQL Server</div>
    
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/productos">Productos</a>
        <a href="/ventas">Ventas</a>
    </div>
    
    <div class="metrics" id="metrics">
        <!-- Métricas se cargarán aquí -->
    </div>
    
    <script>
        async function loadDashboard() {
            try {
                const response = await fetch('/api/analytics/dashboard-metrics');
                const data = await response.json();
                
                const metricsHtml = `
                    <div class="metric-card">
                        <div class="metric-value">${data.current_month_sales}</div>
                        <div class="metric-label">Ventas Mes Actual</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.current_month_orders}</div>
                        <div class="metric-label">Órdenes Mes Actual</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.ytd_sales}</div>
                        <div class="metric-label">Ventas YTD</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.total_products}</div>
                        <div class="metric-label">Productos Activos</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.total_customers}</div>
                        <div class="metric-label">Clientes Activos</div>
                    </div>
                `;
                
                document.getElementById('metrics').innerHTML = metricsHtml;
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('metrics').innerHTML = '<p>Error cargando datos</p>';
            }
        }
        
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
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'<h1>Productos - Conectar con /api/productos</h1>')
    
    def serve_sales_page(self):
        """Serve sales page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'<h1>Ventas - Conectar con /api/ventas</h1>')

def main():
    print("🚀 Iniciando Cyberia SQL Demo...")
    print("🗄️ Conectando a Microsoft SQL Server")
    print(f"🌐 Servidor disponible en: http://localhost:{PORT}")
    print("🔑 Base de datos: Cyberia")
    print("👤 Usuario: SA")
    print()
    
    # Probar conexión
    try:
        connection_string = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']}"
        )
        conn = pyodbc.connect(connection_string)
        print("✅ Conexión a SQL Server exitosa")
        conn.close()
    except Exception as e:
        print(f"❌ Error conectando a SQL Server: {e}")
        print("   Asegúrate de que:")
        print("   - SQL Server esté corriendo")
        print("   - La base de datos 'Cyberia' exista")
        print("   - El usuario SA tenga permisos")
        sys.exit(1)
    
    try:
        with socketserver.TCPServer(("", PORT), CyberiaSQLHandler) as httpd:
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