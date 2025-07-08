from flask import Flask, request, jsonify, render_template_string, send_file, make_response
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import json
import io
import tempfile
import weasyprint
from weasyprint import HTML, CSS

app = Flask(__name__)

# Database configuration - Only reporteventasenejul
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mar120305',
    'database': 'reporteventasenejul',
    'port': 3306
}

def get_db_connection():
    """Get database connection to reporteventasenejul only"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Enhanced HTML Template - Fixed Version
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyberia Business Intelligence - Fixed</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .nav-tabs {
            display: flex;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
        }
        
        .nav-tab {
            flex: 1;
            padding: 15px 25px;
            background: transparent;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            color: #666;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            min-width: 150px;
        }
        
        .nav-tab.active {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .nav-tab:hover:not(.active) {
            background: rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
        }
        
        .tab-content {
            display: none;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            animation: fadeIn 0.5s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            padding: 25px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .filter-group label {
            font-weight: 600;
            color: #444;
            font-size: 0.9em;
        }
        
        .filter-group input,
        .filter-group select {
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: white;
        }
        
        .filter-group input:focus,
        .filter-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
        }
        
        .action-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-secondary {
            background: linear-gradient(45deg, #38ef7d, #11998e);
            color: white;
        }
        
        .btn-warning {
            background: linear-gradient(45deg, #ffd89b, #19547b);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-card i {
            font-size: 2.5em;
            margin-bottom: 15px;
            opacity: 0.9;
        }
        
        .metric-card h3 {
            font-size: 1.1em;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        
        .metric-card .value {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .data-table th {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            border-bottom: none;
        }
        
        .data-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .data-table tr:hover {
            background: #f8f9ff;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
            color: #667eea;
            font-size: 1.2em;
        }
        
        .loading i {
            font-size: 2em;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .results-info {
            margin: 20px 0;
            padding: 15px;
            background: linear-gradient(135deg, #11998e, #38ef7d);
            color: white;
            border-radius: 10px;
            font-weight: 600;
            text-align: center;
        }
        
        .chart-container {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .comparison-tables {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        
        .comparison-card, .performance-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .comparison-table, .performance-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        
        .comparison-table th, .comparison-table td,
        .performance-table th, .performance-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .comparison-table th, .performance-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #667eea;
        }
        
        .positive {
            color: #28a745;
            font-weight: bold;
        }
        
        .negative {
            color: #dc3545;
            font-weight: bold;
        }
        
        .crud-container {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .crud-form {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .crud-list {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            max-height: 600px;
            overflow-y: auto;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #444;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .filters-grid {
                grid-template-columns: 1fr;
            }
            
            .nav-tabs {
                flex-direction: column;
            }
            
            .nav-tab {
                margin-bottom: 5px;
            }
            
            .crud-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-line"></i> Cyberia Business Intelligence</h1>
            <p>Sistema Completo con CRUD, Gráficos y Reportes - Solo Base reporteventasenejul</p>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('dashboard')">
                <i class="fas fa-tachometer-alt"></i> Dashboard
            </button>
            <button class="nav-tab" onclick="showTab('sales')">
                <i class="fas fa-chart-bar"></i> Ventas
            </button>
            <button class="nav-tab" onclick="showTab('crud')">
                <i class="fas fa-database"></i> Gestión CRUD
            </button>
            <button class="nav-tab" onclick="showTab('reports')">
                <i class="fas fa-file-alt"></i> Reportes
            </button>
        </div>
        
        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <h2><i class="fas fa-tachometer-alt"></i> Panel de Control</h2>
            <div id="dashboard-content">
                <div class="loading" style="display: block;">
                    <i class="fas fa-spinner"></i>
                    <div>Cargando métricas del dashboard...</div>
                </div>
            </div>
        </div>
        
        <!-- Sales Tab -->
        <div id="sales" class="tab-content">
            <h2><i class="fas fa-chart-bar"></i> Análisis de Ventas</h2>
            <div class="filters-grid">
                <div class="filter-group">
                    <label>Año</label>
                    <input type="text" id="sales-year" placeholder="2025">
                </div>
                <div class="filter-group">
                    <label>Mes</label>
                    <input type="text" id="sales-month" placeholder="Enero">
                </div>
                <div class="filter-group">
                    <label>Agente</label>
                    <input type="text" id="sales-agent" placeholder="Nombre del agente">
                </div>
                <div class="filter-group">
                    <label>Cliente</label>
                    <input type="text" id="sales-client" placeholder="Razón social">
                </div>
                <div class="filter-group">
                    <label>Tipo</label>
                    <select id="sales-type">
                        <option value="">Todos</option>
                        <option value="Venta">Venta</option>
                        <option value="Maquila">Maquila</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Producto</label>
                    <select id="sales-product">
                        <option value="">Todos los productos</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Total Mínimo</label>
                    <input type="number" id="sales-min-total" placeholder="0">
                </div>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="searchSales()">
                    <i class="fas fa-search"></i> Buscar
                </button>
                <button class="btn btn-secondary" onclick="exportSalesPDF()">
                    <i class="fas fa-file-pdf"></i> Exportar PDF
                </button>
                <button class="btn btn-warning" onclick="exportSalesExcel()">
                    <i class="fas fa-file-excel"></i> Exportar Excel
                </button>
            </div>
            <div class="loading" id="sales-loading">
                <i class="fas fa-spinner"></i>
                <div>Cargando datos de ventas...</div>
            </div>
            <div id="sales-results"></div>
        </div>
        
        <!-- CRUD Tab -->
        <div id="crud" class="tab-content">
            <h2><i class="fas fa-database"></i> Gestión de Datos CRUD</h2>
            
            <div class="crud-container">
                <div class="crud-form">
                    <h3><i class="fas fa-plus"></i> Datos Disponibles</h3>
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="loadCrudData('productos')">
                            <i class="fas fa-box"></i> Ver Productos
                        </button>
                        <button class="btn btn-primary" onclick="loadCrudData('clientes')">
                            <i class="fas fa-users"></i> Ver Clientes
                        </button>
                        <button class="btn btn-primary" onclick="loadCrudData('agentes')">
                            <i class="fas fa-user-tie"></i> Ver Agentes
                        </button>
                        <button class="btn btn-primary" onclick="loadCrudData('ventas_detalladas')">
                            <i class="fas fa-chart-line"></i> Ver Ventas Detalladas
                        </button>
                    </div>
                    <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <h4>📊 Datos en la Base:</h4>
                        <ul style="margin-top: 10px;">
                            <li><strong>Productos:</strong> 100 registros</li>
                            <li><strong>Clientes:</strong> 150 registros</li>
                            <li><strong>Agentes:</strong> 8 registros</li>
                            <li><strong>Ventas:</strong> 1,200+ registros</li>
                            <li><strong>Inventario:</strong> 100 items</li>
                        </ul>
                    </div>
                </div>
                
                <div class="crud-list">
                    <h3><i class="fas fa-list"></i> Vista de Datos</h3>
                    <div class="loading" id="crud-loading">
                        <i class="fas fa-spinner"></i>
                        <div>Selecciona una tabla para ver los datos...</div>
                    </div>
                    <div id="crud-results"></div>
                </div>
            </div>
        </div>
        
        <!-- Reports Tab -->
        <div id="reports" class="tab-content">
            <h2><i class="fas fa-file-alt"></i> Centro de Reportes</h2>
            
            <div class="filters-grid">
                <div class="filter-group">
                    <label>Formato de Reporte</label>
                    <select id="report-format">
                        <option value="pdf">PDF</option>
                        <option value="excel">Excel</option>
                        <option value="html">HTML</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Filtro por Año</label>
                    <input type="text" id="report-year" placeholder="2025">
                </div>
                <div class="filter-group">
                    <label>Filtro por Mes</label>
                    <input type="text" id="report-month" placeholder="Enero">
                </div>
                <div class="filter-group">
                    <label>Agente</label>
                    <input type="text" id="report-agent" placeholder="Todos">
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="generateReport()">
                    <i class="fas fa-file-export"></i> Generar Reporte
                </button>
                <button class="btn btn-secondary" onclick="previewReport()">
                    <i class="fas fa-eye"></i> Vista Previa
                </button>
            </div>
            
            <div id="report-preview" class="chart-container" style="display: none;">
                <h3>Vista Previa del Reporte</h3>
                <div id="report-content"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentData = [];
        
        // Initialize application
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
            loadProducts();
        });
        
        // Load products for dropdown
        async function loadProducts() {
            try {
                const response = await fetch('/api/products');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const products = await response.json();
                
                const productSelect = document.getElementById('sales-product');
                if (!productSelect) {
                    console.error('Product select element not found');
                    return;
                }
                
                productSelect.innerHTML = '<option value="">Todos los productos</option>';
                
                if (Array.isArray(products)) {
                    products.forEach(product => {
                        if (product && typeof product === 'string') {
                            const option = document.createElement('option');
                            option.value = product;
                            option.textContent = product;
                            productSelect.appendChild(option);
                        }
                    });
                } else {
                    console.error('Products response is not an array:', products);
                }
            } catch (error) {
                console.error('Error loading products:', error);
                const productSelect = document.getElementById('sales-product');
                if (productSelect) {
                    productSelect.innerHTML = '<option value="">Error cargando productos</option>';
                }
            }
        }
        
        // Tab management
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all nav tabs
            document.querySelectorAll('.nav-tab').forEach(navTab => {
                navTab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked nav tab
            event.target.classList.add('active');
            
            // Load tab-specific data
            if (tabName === 'dashboard') {
                loadDashboard();
            }
        }
        
        // Dashboard functions
        async function loadDashboard() {
            try {
                const response = await fetch('/api/dashboard-enhanced');
                const data = await response.json();
                
                const dashboardHtml = `
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <i class="fas fa-users"></i>
                            <h3>Total Clientes</h3>
                            <div class="value">${data.total_clients || 0}</div>
                        </div>
                        <div class="metric-card">
                            <i class="fas fa-box"></i>
                            <h3>Total Productos</h3>
                            <div class="value">${data.total_products || 0}</div>
                        </div>
                        <div class="metric-card">
                            <i class="fas fa-dollar-sign"></i>
                            <h3>Profit Total</h3>
                            <div class="value">$${(data.total_profit || 0).toLocaleString()}</div>
                            <small>Total registros: ${data.total_records || 0}</small>
                        </div>
                        <div class="metric-card">
                            <i class="fas fa-calendar-alt"></i>
                            <h3>Profit Enero</h3>
                            <div class="value">$${(data.enero_profit || 0).toLocaleString()}</div>
                            <small>Registros: ${data.enero_records || 0}</small>
                        </div>
                        <div class="metric-card">
                            <i class="fas fa-user-tie"></i>
                            <h3>Total Agentes</h3>
                            <div class="value">${data.total_agents || 0}</div>
                        </div>
                    </div>
                    
                    <div class="comparison-tables">
                        <div class="comparison-card">
                            <h3>Comparativa Mensual</h3>
                            <div id="monthly-comparison"></div>
                        </div>
                        <div class="performance-card">
                            <h3>Desempeño por Mes</h3>
                            <div id="monthly-performance"></div>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <h3>Profit por Mes</h3>
                        <div id="dashboard-chart"></div>
                    </div>
                `;
                
                document.getElementById('dashboard-content').innerHTML = dashboardHtml;
                
                // Create dashboard chart
                if (data.sales_chart_data && data.sales_chart_data.months.length > 0) {
                    const trace = {
                        x: data.sales_chart_data.months,
                        y: data.sales_chart_data.sales,
                        type: 'scatter',
                        mode: 'lines+markers',
                        marker: { color: '#667eea', size: 8 },
                        line: { color: '#667eea', width: 3 }
                    };
                    
                    const layout = {
                        title: false,
                        xaxis: { title: 'Mes' },
                        yaxis: { title: 'Profit ($)' },
                        margin: { t: 20, r: 20, b: 50, l: 80 }
                    };
                    
                    Plotly.newPlot('dashboard-chart', [trace], layout, { responsive: true });
                }
                
                // Create monthly comparison table
                if (data.monthly_comparison) {
                    let comparisonHtml = '<table class="comparison-table"><tr><th>Mes</th><th>Ventas</th><th>Maquilas</th><th>Total</th><th>Cambio</th></tr>';
                    data.monthly_comparison.forEach(month => {
                        const changeClass = month.change >= 0 ? 'positive' : 'negative';
                        const changeIcon = month.change >= 0 ? '▲' : '▼';
                        comparisonHtml += `
                            <tr>
                                <td>${month.month}</td>
                                <td>$${month.ventas.toLocaleString()}</td>
                                <td>$${month.maquilas.toLocaleString()}</td>
                                <td>$${month.total.toLocaleString()}</td>
                                <td class="${changeClass}">${changeIcon} ${Math.abs(month.change).toFixed(1)}%</td>
                            </tr>
                        `;
                    });
                    comparisonHtml += '</table>';
                    document.getElementById('monthly-comparison').innerHTML = comparisonHtml;
                }
                
                // Create monthly performance table
                if (data.monthly_performance) {
                    let performanceHtml = '<table class="performance-table"><tr><th>Mes</th><th>Total Profit</th><th>Promedio/Día</th><th>Ranking</th></tr>';
                    data.monthly_performance.forEach((month, index) => {
                        performanceHtml += `
                            <tr>
                                <td>${month.month}</td>
                                <td>$${month.total.toLocaleString()}</td>
                                <td>$${month.daily_avg.toLocaleString()}</td>
                                <td>#${index + 1}</td>
                            </tr>
                        `;
                    });
                    performanceHtml += '</table>';
                    document.getElementById('monthly-performance').innerHTML = performanceHtml;
                }
                
            } catch (error) {
                console.error('Error loading dashboard:', error);
                document.getElementById('dashboard-content').innerHTML = '<div style="padding: 20px; text-align: center; color: #ff6b6b;">Error al cargar el dashboard</div>';
            }
        }
        
        // Sales functions
        async function searchSales() {
            const loading = document.getElementById('sales-loading');
            const results = document.getElementById('sales-results');
            
            if (!loading || !results) {
                console.error('Required elements not found for search');
                return;
            }
            
            loading.style.display = 'block';
            results.innerHTML = '';
            
            // Clean and validate filters
            const filters = {};
            const filterElements = {
                year: 'sales-year',
                month: 'sales-month',
                agent: 'sales-agent',
                client: 'sales-client',
                type: 'sales-type',
                product: 'sales-product',
                min_total: 'sales-min-total'
            };
            
            // Only add non-empty filters
            for (const [key, elementId] of Object.entries(filterElements)) {
                const element = document.getElementById(elementId);
                if (element && element.value && element.value.trim() !== '') {
                    filters[key] = element.value.trim();
                }
            }
            
            try {
                const params = new URLSearchParams(filters);
                const response = await fetch(`/api/sales?${params}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                loading.style.display = 'none';
                currentData = Array.isArray(data) ? data : [];
                
                if (currentData.length === 0) {
                    results.innerHTML = '<div class="results-info"><i class="fas fa-info-circle"></i> No se encontraron resultados con los filtros especificados</div>';
                    return;
                }
                
                const tableHtml = createSalesTable(currentData);
                const totalAmount = currentData.reduce((sum, item) => sum + (parseFloat(item.total) || 0), 0);
                
                results.innerHTML = `
                    <div class="results-info">
                        <i class="fas fa-check-circle"></i> 
                        Se encontraron ${currentData.length.toLocaleString()} registros
                        <span style="margin-left: 20px;">
                            <i class="fas fa-dollar-sign"></i>
                            Total: $${totalAmount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                        </span>
                    </div>
                    ${tableHtml}
                `;
                
            } catch (error) {
                loading.style.display = 'none';
                results.innerHTML = `<div style="padding: 20px; text-align: center; color: #ff6b6b;">
                    <i class="fas fa-exclamation-triangle"></i> 
                    Error al cargar datos: ${error.message}
                </div>`;
            }
        }
        
        function createSalesTable(data) {
            if (!Array.isArray(data) || data.length === 0) {
                return '<div class="no-data">No hay datos para mostrar</div>';
            }
            
            // Para datasets muy grandes, implementar filtrado inteligente
            const maxDisplayRows = 1000; // Máximo 1000 filas para renderizado óptimo
            let displayData = data;
            
            // Si hay muchos datos, aplicar filtrado inteligente
            if (data.length > maxDisplayRows) {
                // Ordenar por total descendente para mostrar las transacciones más relevantes
                const sortedData = [...data].sort((a, b) => (parseFloat(b.total) || 0) - (parseFloat(a.total) || 0));
                
                // Tomar los primeros 500 (más importantes) y una muestra del resto
                const topRecords = sortedData.slice(0, 500);
                const remainingData = sortedData.slice(500);
                
                // Muestra aleatoria del resto para representar la distribución
                const sampleSize = Math.min(500, remainingData.length);
                const sampledData = [];
                for (let i = 0; i < sampleSize; i++) {
                    const randomIndex = Math.floor(Math.random() * remainingData.length);
                    sampledData.push(remainingData[randomIndex]);
                    remainingData.splice(randomIndex, 1);
                }
                
                displayData = [...topRecords, ...sampledData];
            }
            
            let html = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Año</th><th>Mes</th><th>Fecha</th><th>Folio</th>
                            <th>Agente</th><th>Cliente</th><th>Producto</th>
                            <th>Cantidad</th><th>Precio</th><th>Total</th><th>Tipo</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            if (data.length > maxDisplayRows) {
                html += `<tr><td colspan="11" style="background: #fff3cd; text-align: center; font-weight: bold;">
                    Mostrando ${displayData.length.toLocaleString()} registros centrados de ${data.length.toLocaleString()} totales 
                    (500 más importantes + ${displayData.length - 500} muestra representativa)
                </td></tr>`;
            }
            
            displayData.forEach(row => {
                html += `
                    <tr>
                        <td>${row.año || ''}</td>
                        <td>${row.mes || ''}</td>
                        <td>${row.fecha || ''}</td>
                        <td>${row.folio || ''}</td>
                        <td>${row.agente || ''}</td>
                        <td>${row.razon_social || ''}</td>
                        <td>${row.producto || ''}</td>
                        <td>${row.cantidad || ''}</td>
                        <td>$${parseFloat(row.precio || 0).toLocaleString()}</td>
                        <td>$${parseFloat(row.total || 0).toLocaleString()}</td>
                        <td>${row['tipo_operacion'] || row['Venta/Maquila'] || 'Venta'}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            return html;
        }
        
        // Export functions
        async function exportSalesPDF() {
            if (currentData.length === 0) {
                alert('No hay datos para exportar. Realiza una búsqueda primero.');
                return;
            }
            
            try {
                const response = await fetch('/api/export-pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentData)
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `reporte_ventas_${new Date().toISOString().split('T')[0]}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                } else {
                    alert('Error al generar PDF');
                }
            } catch (error) {
                alert('Error al exportar PDF: ' + error.message);
            }
        }
        
        async function exportSalesExcel() {
            if (currentData.length === 0) {
                alert('No hay datos para exportar. Realiza una búsqueda primero.');
                return;
            }
            
            try {
                const response = await fetch('/api/export-excel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentData)
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `reporte_ventas_${new Date().toISOString().split('T')[0]}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                } else {
                    alert('Error al generar Excel');
                }
            } catch (error) {
                alert('Error al exportar Excel: ' + error.message);
            }
        }
        
        // CRUD functions
        async function loadCrudData(tableName) {
            const loading = document.getElementById('crud-loading');
            const results = document.getElementById('crud-results');
            
            loading.style.display = 'block';
            results.innerHTML = '';
            
            try {
                const response = await fetch(`/api/crud/${tableName}`);
                const data = await response.json();
                
                loading.style.display = 'none';
                
                if (data.error) {
                    results.innerHTML = `<div style="padding: 20px; color: #ff6b6b;">Error: ${data.error}</div>`;
                    return;
                }
                
                if (data.length === 0) {
                    results.innerHTML = '<div style="padding: 20px; text-align: center;">No se encontraron datos</div>';
                    return;
                }
                
                // Create table based on data structure
                let html = `
                    <h4>📋 ${tableName.toUpperCase()} (${data.length} registros)</h4>
                    <table class="data-table">
                        <thead>
                            <tr>
                `;
                
                // Add headers based on first row keys
                const keys = Object.keys(data[0]);
                keys.forEach(key => {
                    html += `<th>${key}</th>`;
                });
                html += '</tr></thead><tbody>';
                
                // Add all data rows
                data.forEach(row => {
                    html += '<tr>';
                    keys.forEach(key => {
                        let value = row[key];
                        if (typeof value === 'number' && key.includes('precio') || key.includes('total') || key.includes('credito')) {
                            value = `$${value.toLocaleString()}`;
                        }
                        html += `<td>${value || ''}</td>`;
                    });
                    html += '</tr>';
                });
                
                html += '</tbody></table>';
                
                if (data.length > 50) {
                    html += `<div style="padding: 10px; text-align: center; color: #666;">Mostrando 50 de ${data.length} registros</div>`;
                }
                
                results.innerHTML = html;
                
            } catch (error) {
                loading.style.display = 'none';
                results.innerHTML = `<div style="padding: 20px; color: #ff6b6b;">Error al cargar datos: ${error.message}</div>`;
            }
        }
        
        // Reports functions
        async function generateReport() {
            const format = document.getElementById('report-format').value;
            const year = document.getElementById('report-year').value;
            const month = document.getElementById('report-month').value;
            const agent = document.getElementById('report-agent').value;
            
            // Build filters
            const filters = {};
            if (year) filters.year = year;
            if (month) filters.month = month;
            if (agent) filters.agent = agent;
            
            try {
                // Get filtered sales data
                const params = new URLSearchParams(filters);
                const response = await fetch(`/api/sales?${params}`);
                const data = await response.json();
                
                if (data.length === 0) {
                    alert('No hay datos para el reporte con los filtros especificados');
                    return;
                }
                
                // Export based on format
                if (format === 'pdf') {
                    const exportResponse = await fetch('/api/export-pdf', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    if (exportResponse.ok) {
                        const blob = await exportResponse.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `reporte_completo_${new Date().toISOString().split('T')[0]}.pdf`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                    }
                } else if (format === 'excel') {
                    const exportResponse = await fetch('/api/export-excel', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    if (exportResponse.ok) {
                        const blob = await exportResponse.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `reporte_completo_${new Date().toISOString().split('T')[0]}.xlsx`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                    }
                }
                
            } catch (error) {
                alert('Error al generar reporte: ' + error.message);
            }
        }
        
        async function previewReport() {
            const year = document.getElementById('report-year').value;
            const month = document.getElementById('report-month').value;
            const agent = document.getElementById('report-agent').value;
            
            // Build filters
            const filters = {};
            if (year) filters.year = year;
            if (month) filters.month = month;
            if (agent) filters.agent = agent;
            
            try {
                const params = new URLSearchParams(filters);
                const response = await fetch(`/api/sales?${params}`);
                const data = await response.json();
                
                if (data.length === 0) {
                    document.getElementById('report-content').innerHTML = '<p>No hay datos para mostrar con los filtros especificados.</p>';
                } else {
                    const tableHtml = createSalesTable(data.slice(0, 20)); // Show first 20 records
                    document.getElementById('report-content').innerHTML = `
                        <h4>Vista Previa del Reporte (${data.length} registros encontrados, mostrando primeros 20)</h4>
                        ${tableHtml}
                    `;
                }
                
                document.getElementById('report-preview').style.display = 'block';
                
            } catch (error) {
                document.getElementById('report-content').innerHTML = `<p>Error generando vista previa: ${error.message}</p>`;
                document.getElementById('report-preview').style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/dashboard-enhanced', methods=['GET'])
def get_dashboard_enhanced():
    """Enhanced dashboard with new tables"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    dashboard_data = {}
    
    try:
        # Check what tables exist first
        cursor.execute("SHOW TABLES")
        tables = [list(table.values())[0] for table in cursor.fetchall()]
        
        # Get counts directly from VentasENEJUL table
        cursor.execute("SELECT COUNT(DISTINCT `Razon social`) as count FROM `VentasENEJUL`")
        dashboard_data['total_clients'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT `Producto`) as count FROM `VentasENEJUL`")
        dashboard_data['total_products'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT `Agente`) as count FROM `VentasENEJUL`")
        dashboard_data['total_agents'] = cursor.fetchone()['count']
        
        # Get profit data directly from VentasENEJUL
        if 'VentasENEJUL' in tables:
            # Calculate total profit (Ventas + Maquilas)
            cursor.execute("""
                SELECT SUM(`Total`) as total 
                FROM `VentasENEJUL`
            """)
            result = cursor.fetchone()
            dashboard_data['total_profit'] = float(result['total'] or 0)
            
            # Get profit for current month (Enero for verification) - SAME QUERY AS SALES API
            cursor.execute("""
                SELECT SUM(`Total`) as total 
                FROM `VentasENEJUL`
                WHERE `Mes` LIKE %s
            """, ['%Enero%'])
            enero_result = cursor.fetchone()
            dashboard_data['enero_profit'] = float(enero_result['total'] or 0)
            
            # DEBUG: Count total records to verify data access
            cursor.execute("SELECT COUNT(*) as count FROM `VentasENEJUL`")
            total_count = cursor.fetchone()
            dashboard_data['total_records'] = total_count['count']
            
            # DEBUG: Count enero records
            cursor.execute("SELECT COUNT(*) as count FROM `VentasENEJUL` WHERE `Mes` LIKE %s", ['%Enero%'])
            enero_count = cursor.fetchone()
            dashboard_data['enero_records'] = enero_count['count']
            
            # Get monthly profit data for chart
            cursor.execute("""
                SELECT 
                    `Mes` as month,
                    SUM(`Total`) as total
                FROM `VentasENEJUL` 
                GROUP BY `Mes`
                ORDER BY 
                    CASE `Mes`
                        WHEN 'Enero' THEN 1
                        WHEN 'Febrero' THEN 2
                        WHEN 'Marzo' THEN 3
                        WHEN 'Abril' THEN 4
                        WHEN 'Mayo' THEN 5
                        WHEN 'Junio' THEN 6
                        WHEN 'Julio' THEN 7
                        WHEN 'Agosto' THEN 8
                        WHEN 'Septiembre' THEN 9
                        WHEN 'Octubre' THEN 10
                        WHEN 'Noviembre' THEN 11
                        WHEN 'Diciembre' THEN 12
                    END
            """)
            chart_data = cursor.fetchall()
            
            # Get monthly comparison data (Ventas vs Maquilas)
            cursor.execute("""
                SELECT 
                    `Mes` as month,
                    SUM(CASE WHEN `Venta/Maquila` = 'Venta' THEN `Total` ELSE 0 END) as ventas,
                    SUM(CASE WHEN `Venta/Maquila` = 'Maquila' THEN `Total` ELSE 0 END) as maquilas,
                    SUM(`Total`) as total
                FROM `VentasENEJUL` 
                GROUP BY `Mes`
                ORDER BY 
                    CASE `Mes`
                        WHEN 'Enero' THEN 1 WHEN 'Febrero' THEN 2 WHEN 'Marzo' THEN 3
                        WHEN 'Abril' THEN 4 WHEN 'Mayo' THEN 5 WHEN 'Junio' THEN 6
                        WHEN 'Julio' THEN 7 WHEN 'Agosto' THEN 8 WHEN 'Septiembre' THEN 9
                        WHEN 'Octubre' THEN 10 WHEN 'Noviembre' THEN 11 WHEN 'Diciembre' THEN 12
                    END
            """)
            comparison_raw = cursor.fetchall()
            
            # Calculate month-to-month changes
            monthly_comparison = []
            for i, month in enumerate(comparison_raw):
                change = 0
                if i > 0:
                    prev_total = comparison_raw[i-1]['total']
                    if prev_total > 0:
                        change = ((month['total'] - prev_total) / prev_total) * 100
                
                monthly_comparison.append({
                    'month': month['month'],
                    'ventas': float(month['ventas'] or 0),
                    'maquilas': float(month['maquilas'] or 0),
                    'total': float(month['total'] or 0),
                    'change': change
                })
            
            dashboard_data['monthly_comparison'] = monthly_comparison
            
            # Get monthly performance (sorted by total)
            monthly_performance = []
            for month in sorted(comparison_raw, key=lambda x: x['total'], reverse=True):
                # Estimate daily average (assuming 30 days per month)
                daily_avg = float(month['total'] or 0) / 30
                monthly_performance.append({
                    'month': month['month'],
                    'total': float(month['total'] or 0),
                    'daily_avg': daily_avg
                })
            
            dashboard_data['monthly_performance'] = monthly_performance
        else:
            dashboard_data['total_profit'] = 0
            dashboard_data['enero_profit'] = 0
            dashboard_data['total_records'] = 0
            dashboard_data['enero_records'] = 0
            dashboard_data['monthly_comparison'] = []
            dashboard_data['monthly_performance'] = []
            chart_data = []
        
        dashboard_data['sales_chart_data'] = {
            'months': [row['month'] for row in chart_data],
            'sales': [float(row['total'] or 0) for row in chart_data]
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': f'Dashboard error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Original Sales API (working with VentasENEJUL table)
@app.route('/api/sales', methods=['GET'])
def get_sales():
    """Get sales data with filters - using VentasENEJUL table"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    # Build query with filters for original VentasENEJUL table
    query = "SELECT * FROM `VentasENEJUL` WHERE 1=1"
    params = []
    
    # Apply filters
    if request.args.get('year'):
        query += " AND `Año` LIKE %s"
        params.append(f"%{request.args.get('year')}%")
    
    if request.args.get('month'):
        query += " AND `Mes` LIKE %s"
        params.append(f"%{request.args.get('month')}%")
    
    if request.args.get('date'):
        query += " AND `Fecha` LIKE %s"
        params.append(f"%{request.args.get('date')}%")
    
    if request.args.get('agent'):
        query += " AND `Agente` LIKE %s"
        params.append(f"%{request.args.get('agent')}%")
    
    if request.args.get('product'):
        query += " AND `Producto` LIKE %s"
        params.append(f"%{request.args.get('product')}%")
    
    if request.args.get('client'):
        query += " AND `Razon social` LIKE %s"
        params.append(f"%{request.args.get('client')}%")
    
    if request.args.get('type'):
        query += " AND `Venta/Maquila` = %s"
        params.append(request.args.get('type'))
    
    if request.args.get('min_total'):
        query += " AND `Total` >= %s"
        params.append(float(request.args.get('min_total')))
    
    # Add ordering
    query += " ORDER BY `Fecha` DESC, `Total` DESC"
    
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        result = []
        for row in rows:
            result.append({
                'año': row['Año'],
                'mes': row['Mes'],
                'fecha': row['Fecha'],
                'folio': row['Folio'],
                'agente': row['Agente'],
                'razon_social': row['Razon social'],
                'producto': row['Producto'],
                'cantidad': row['Cantidad'],
                'kilos': row['Kilos'],
                'toneladas': row['Toneladas'],
                'precio': row['Precio'],
                'total': row['Total']
            })
        
        cursor.close()
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

# Products API for dropdown
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get unique products for dropdown filter"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT DISTINCT `Producto` FROM `VentasENEJUL` WHERE `Producto` IS NOT NULL ORDER BY `Producto`")
        products = [row['Producto'] for row in cursor.fetchall()]
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# CRUD API Endpoints
@app.route('/api/crud/<table>', methods=['GET'])
def get_crud_data(table):
    """Get all records from a table"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if table exists first
        cursor.execute("SHOW TABLES")
        tables = [list(t.values())[0] for t in cursor.fetchall()]
        
        if table not in tables:
            return jsonify({'error': f'Table {table} does not exist'}), 404
        
        if table == 'ventas_detalladas':
            query = """
                SELECT v.*, c.razon_social as cliente_nombre, 
                       a.nombre_completo as agente_nombre,
                       p.nombre as producto_nombre
                FROM ventas_detalladas v
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                LEFT JOIN agentes a ON v.id_agente = a.id_agente  
                LEFT JOIN productos p ON v.id_producto = p.id_producto
                ORDER BY v.fecha_venta DESC
            """
        elif table == 'productos':
            query = "SELECT * FROM productos ORDER BY nombre"
        elif table == 'clientes':
            query = "SELECT * FROM clientes ORDER BY razon_social"
        elif table == 'agentes':
            query = "SELECT * FROM agentes ORDER BY nombre_completo"
        else:
            query = f"SELECT * FROM `{table}` ORDER BY 1 DESC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify(rows)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Fixed PDF Export
@app.route('/api/export-pdf', methods=['POST'])
def export_pdf():
    """Export data as PDF using HTML format"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    margin: 20px;
                }}
                h1 {{
                    color: #667eea;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .header-info {{
                    text-align: center;
                    margin-bottom: 30px;
                    background: #f5f7fa;
                    padding: 15px;
                    border-radius: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                    font-size: 10px;
                }}
                th {{
                    background: #667eea;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background: #f9f9f9;
                }}
                .total-row {{
                    background: #e7f3ff !important;
                    font-weight: bold;
                }}
                .number {{ text-align: right; }}
            </style>
        </head>
        <body>
            <h1>Reporte de Ventas - Cyberia BI</h1>
            <div class="header-info">
                <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p><strong>Total de registros:</strong> {len(data)}</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Año</th><th>Mes</th><th>Fecha</th><th>Folio</th><th>Agente</th>
                        <th>Cliente</th><th>Producto</th><th>Cantidad</th><th>Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_general = 0
        for row in data:
            total_row = float(row.get('total', 0))
            total_general += total_row
            
            html_content += f"""
            <tr>
                <td>{row.get('año', '')}</td>
                <td>{row.get('mes', '')}</td>
                <td>{row.get('fecha', '')}</td>
                <td>{row.get('folio', '')}</td>
                <td>{row.get('agente', '')}</td>
                <td>{row.get('razon_social', '')}</td>
                <td>{row.get('producto', '')}</td>
                <td class="number">{row.get('cantidad', '')}</td>
                <td class="number">${total_row:,.2f}</td>
            </tr>
            """
        
        html_content += f"""
                <tr class="total-row">
                    <td colspan="8" style="text-align: right;"><strong>TOTAL GENERAL:</strong></td>
                    <td class="number"><strong>${total_general:,.2f}</strong></td>
                </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Try WeasyPrint first, fallback to HTML response
        try:
            from weasyprint import HTML
            pdf_buffer = io.BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            pdf_buffer.seek(0)
            
            filename = f'reporte_ventas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            response = make_response(pdf_buffer.read())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
            
        except Exception as pdf_error:
            print(f"PDF generation error: {pdf_error}")
            # Fallback to HTML
            filename = f'reporte_ventas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            response = make_response(html_content)
            response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
            
    except Exception as e:
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

# Excel Export
@app.route('/api/export-excel', methods=['POST'])
def export_excel():
    """Export data as Excel"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ventas', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Ventas']
            
            # Apply basic formatting
            for cell in worksheet[1]:
                cell.font = workbook.create_font(bold=True)
        
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'reporte_ventas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error generating Excel: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)