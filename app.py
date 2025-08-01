from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response, send_file
import pyodbc
import pandas as pd
import warnings
import json
import math
from datetime import datetime, date
import io
import tempfile
import os

# Ignorar advertencias específicas de pandas
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy connectable')

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Language translations
LANGUAGES = {
    'es': {
        'name': 'Español',
        'flag': '🇪🇸',
        'ui': {
            'system_title': 'Sistema de Reportes',
            'year_report': 'Reporte por Año',
            'daily_sales': 'Ventas por Día',
            'monthly_sales': 'Ventas por Mes',
            'sales_objectives': 'Objetivos',
            'filter_agent': 'Filtro de Agente',
            'select_agent': 'Seleccionar Agente',
            'filter_btn': 'Filtrar',
            'active_filter': 'Filtro activo',
            'showing_data_for': 'Mostrando datos para el agente',
            'coverage_report': 'Reporte de Coberturas',
            'records_per_page': 'Registros por página',
            'quick_search': 'Búsqueda rápida',
            'refresh': 'Actualizar',
            'total_records': 'Total de registros',
            'export_excel': 'Excel',
            'export_csv': 'CSV',
            'export_pdf': 'PDF',
            'print': 'Imprimir',
            'search_table': 'Buscar en la tabla...',
            'page_of': 'de',
            'pages': 'páginas',
            'per_page': 'por página',
            'language': 'Idioma'
        }
    },
    'en': {
        'name': 'English',
        'flag': '🇺🇸',
        'ui': {
            'system_title': 'Reports System',
            'year_report': 'Year Report',
            'daily_sales': 'Daily Sales',
            'monthly_sales': 'Monthly Sales',
            'sales_objectives': 'Objectives',
            'coverage_report': 'Coverage Report',
            'filter_agent': 'Agent Filter',
            'select_agent': 'Select Agent',
            'filter_btn': 'Filter',
            'active_filter': 'Active filter',
            'showing_data_for': 'Showing data for agent',
            'records_per_page': 'Records per page',
            'quick_search': 'Quick search',
            'refresh': 'Refresh',
            'total_records': 'Total records',
            'export_excel': 'Excel',
            'export_csv': 'CSV',
            'export_pdf': 'PDF',
            'print': 'Print',
            'search_table': 'Search in table...',
            'page_of': 'of',
            'pages': 'pages',
            'per_page': 'per page',
            'language': 'Language'
        }
    },
    'ja': {
        'name': '日本語',
        'flag': '🇯🇵',
        'ui': {
            'system_title': 'レポートシステム',
            'year_report': '年次レポート',
            'daily_sales': '日次売上',
            'monthly_sales': '月次売上',
            'sales_objectives': '目標',
            'coverage_report': 'カバレッジレポート',
            'filter_agent': 'エージェントフィルター',
            'select_agent': 'エージェント選択',
            'filter_btn': 'フィルター',
            'active_filter': 'アクティブフィルター',
            'showing_data_for': 'エージェントのデータを表示',
            'records_per_page': 'ページあたりの記録数',
            'quick_search': 'クイック検索',
            'refresh': '更新',
            'total_records': '総記録数',
            'export_excel': 'Excel',
            'export_csv': 'CSV',
            'export_pdf': 'PDF',
            'print': '印刷',
            'search_table': 'テーブルで検索...',
            'page_of': 'の',
            'pages': 'ページ',
            'per_page': 'ページあたり',
            'language': '言語'
        }
    },
    'zh': {
        'name': '中文',
        'flag': '🇨🇳',
        'ui': {
            'system_title': '报告系统',
            'year_report': '年度报告',
            'daily_sales': '日销售',
            'monthly_sales': '月销售',
            'sales_objectives': '目标',
            'coverage_report': '覆盖报告',
            'filter_agent': '代理筛选',
            'select_agent': '选择代理',
            'filter_btn': '筛选',
            'active_filter': '活动筛选',
            'showing_data_for': '显示代理的数据',
            'records_per_page': '每页记录数',
            'quick_search': '快速搜索',
            'refresh': '刷新',
            'total_records': '总记录数',
            'export_excel': 'Excel',
            'export_csv': 'CSV',
            'export_pdf': 'PDF',
            'print': '打印',
            'search_table': '在表格中搜索...',
            'page_of': '的',
            'pages': '页',
            'per_page': '每页',
            'language': '语言'
        }
    },
    'de': {
        'name': 'Deutsch',
        'flag': '🇩🇪',
        'ui': {
            'system_title': 'Berichtssystem',
            'year_report': 'Jahresbericht',
            'daily_sales': 'Tagesverkäufe',
            'monthly_sales': 'Monatsverkäufe',
            'sales_objectives': 'Ziele',
            'coverage_report': 'Abdeckungsbericht',
            'filter_agent': 'Agentenfilter',
            'select_agent': 'Agent auswählen',
            'filter_btn': 'Filtern',
            'active_filter': 'Aktiver Filter',
            'showing_data_for': 'Zeige Daten für Agent',
            'records_per_page': 'Datensätze pro Seite',
            'quick_search': 'Schnellsuche',
            'refresh': 'Aktualisieren',
            'total_records': 'Gesamtdatensätze',
            'export_excel': 'Excel',
            'export_csv': 'CSV',
            'export_pdf': 'PDF',
            'print': 'Drucken',
            'search_table': 'In Tabelle suchen...',
            'page_of': 'von',
            'pages': 'Seiten',
            'per_page': 'pro Seite',
            'language': 'Sprache'
        }
    }
}

def get_language():
    """Get current language from session or default to Spanish"""
    return session.get('language', 'es')

def get_translations():
    """Get translations for current language"""
    lang = get_language()
    return LANGUAGES.get(lang, LANGUAGES['es'])

# Configuración de la conexión a la base de datos
def get_db_connection():
    server = "localhost,1433"
    database = "adMOLIENDAS_Y_ALIMENTO"
    username = "SA"
    password = "Mar120305!"
    
    conn = pyodbc.connect(
        'DRIVER=FreeTDS;'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        'TDS_Version=7.4;'
        'Port=1433;'
    )
    return conn

# Consulta para el reporte por año
def get_reporte_anio(agente=None):
    conn = get_db_connection()
    
    # Agent filtering condition
    agente_condition = ""
    if agente and agente != 'Todos':
        agente_condition = f"AND a.CNOMBREAGENTE = '{agente}'"
    
    # Tu consulta completa para reporte por año aquí
    query = f"""SELECT
	YEAR(m.CFECHA) AS Año,
    MONTH(m.CFECHA) AS Mes,
    SUM(
        CASE
            WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
            WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
            WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
            WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
            WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
            WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
            WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
            WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
            WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
            WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
            WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
            WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
            WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
            ELSE 0
        END
    ) AS KilosTotales,
    SUM(
        CASE
            WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
            WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
            WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
            WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
            WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
            WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
            WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
            WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
            WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
            WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
            WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
            WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
            WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
            ELSE 0
        END
    ) / 1000.0 AS ToneladasTotales
FROM 
    admMovimientos m
JOIN 
    admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
JOIN
    admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
JOIN
    admDocumentos d ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
JOIN
    admAgentes a ON d.CIDAGENTE = a.CIDAGENTE
WHERE
    p.CCODIGOPRODUCTO IN (('MESCO25'),
	('MESCO30'),
	('MESPU07'),
	('MREGR26'),
	('MREGR30'),
	('MREP613'),
	('MREP614'),
	('MREP620'),
	('PAL0007'),
	('PAL0008'),
	('PAL0009'),
	('PBSMZ04'),
	('PBSMZ05'),
	('PBSMZ06'),
	('PBSMZ08'),
	('PBSMZ09'),
	('PBSMZ11'),
	('PBSMZ14'),
	('PCAGF02'),
	('PCAGF03'),
	('PCAGF04'),
	('PCFAI03'),
	('PCFAM03'),
	('PCFAZ03'),
	('PCFMO03'),
	('PCFMO05'),
	('PCFNA03'),
	('PCFNE03'),
	('PCFRS03'),
	('PCFVA03'),
	('PCFVE03'),
	('PCFVI03'),
	('PCFVL03'),
	('PCGAI03'),
	('PCGAM03'),
	('PCGAZ03'),
	('PCGMO03'),
	('PCGNA03'),
	('PCGNE03'),
	('PCGRF03'),
	('PCGRO03'),
	('PCGRS03'),
	('PCGVA03'),
	('PCGVE03'),
	('PCGVI03'),
	('PCGVL01'),
	('PCGVL03'),
	('PESCO25'),
	('PESEM17'),
	('PESGR07'),
	('PESGR10'),
	('PESGR21'),
	('PESGR22'),
	('PESP607'),
	('PESP610'),
	('PG3EN01'),
	('PG3EN08'),
	('PM5EN04'),
	('PREBS07'),
	('PRECE01'),
	('PRECE02'),
	('PRECS01'),
	('PREEF26'),
	('PREEM17'),
	('PREFS11'),
	('PREFS12'),
	('PREGG12'),
	('PREGR07'),
	('PREGR10'),
	('PREGR23'),
	('PREGR24'),
	('PREGR25'),
	('PRELG02'),
	('PREMC11'),
	('PREO407'),
	('PREP107'),
	('PREP108'),
	('PREP112'),
	('PREP113'),
	('PREP607'),
	('PBAR002'),
	('PCMNE01'),
	('PREP111'),
	('PCFVV03'),
	('MAREGR11'),
	('RMREP614'),
	('PESEM11'),
	('MREP621'),
	('MREP622'),
	('RREGR10'),
	('RPREP607'),
	('CSER026'),
	('PREGR27'),
	('PREGR29'),
	('PBSMZ22'),
	('RMREP620'),
	('CSER208'),
	('PESEM12'),
	('AREGR10'),
	('AE1GR01'),
	('AR1GR10'),
	('ABEGR01'),
	('PBAR003'),
	('MAM5ESCNI'),
	('PESGG12'),
	('RPREBS07'),
	('RPBSMZ08'),
	('PRECCN2'),
	('MGSMDLZ'),
	('ZTAR003'),
	('ZTAR004'),
	('ZTAR005'),
	('CSER209'),
	('MGL01'),
	('PREEF27'),
	('FEUR10'),
	('JS109'),
	('EX45'),
	('SEÑ1600'),
	('PCGEAZ1'),
	('MREGR23'),
	('ZEMP006'),
	('MAREGR15'),
	('PESCO40'),
	('PPIL001'),
	('ZBES010'),
	('ZBES005'),
	('ZBESM907'),
	('ZBRE010'),
	('ZBRE005'),
	('PPIL002'),
	('PPIL003'),
	('ZSAC004'),
	('MAM5CESGR2'),
	('RSERMAQ04'),
	('RSERMAQ05'),
	('RSERMAQ06'),
	('PILCJA01'),
	('PILCJA02'),
	('FLSER001'),
	('LBACE01'),
	('ZEDU007'))
    AND m.CIDDOCUMENTODE = 4
    AND dm.CMODULO = 1
    {agente_condition}
GROUP BY
    YEAR(m.CFECHA),
    MONTH(m.CFECHA) 
ORDER BY 
    YEAR(m.CFECHA),
    MONTH(m.CFECHA); """  # Mantén tu consulta
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Function to get year report data for graphs
def get_reporte_anio_for_graph(year1=None, year2=None, start_month=1, end_month=12, agente=None):
    conn = get_db_connection()
    
    year_filter = ""
    if year1 and year2:
        year_filter = f"AND YEAR(m.CFECHA) IN ({year1}, {year2})"
    elif year1:
        year_filter = f"AND YEAR(m.CFECHA) = {year1}"
    
    month_filter = f"AND MONTH(m.CFECHA) BETWEEN {start_month} AND {end_month}"
    
    agente_condition = ""
    if agente and agente != 'Todos':
        agente_condition = f"AND a.CNOMBREAGENTE = '{agente}'"
    
    query = f"""SELECT
	YEAR(m.CFECHA) AS Anio,
    MONTH(m.CFECHA) AS Mes,
    SUM(
        CASE
            WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
            WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
            WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
            WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
            WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
            WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
            WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
            WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
            WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
            WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
            WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
            WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
            WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
            ELSE 0
        END
    ) / 1000.0 AS ToneladasTotales
FROM 
    admMovimientos m
JOIN 
    admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
JOIN
    admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
JOIN
    admDocumentos d ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
JOIN
    admAgentes a ON d.CIDAGENTE = a.CIDAGENTE
WHERE
    p.CCODIGOPRODUCTO IN (('MESCO25'),('MESCO30'),('MESPU07'),('MREGR26'),('MREGR30'),('MREP613'),('MREP614'),('MREP620'),('PAL0007'),('PAL0008'),('PAL0009'),('PBSMZ04'),('PBSMZ05'),('PBSMZ06'),('PBSMZ08'),('PBSMZ09'),('PBSMZ11'),('PBSMZ14'),('PCAGF02'),('PCAGF03'),('PCAGF04'),('PCFAI03'),('PCFAM03'),('PCFAZ03'),('PCFMO03'),('PCFMO05'),('PCFNA03'),('PCFNE03'),('PCFRS03'),('PCFVA03'),('PCFVE03'),('PCFVI03'),('PCFVL03'),('PCGAI03'),('PCGAM03'),('PCGAZ03'),('PCGMO03'),('PCGNA03'),('PCGNE03'),('PCGRF03'),('PCGRO03'),('PCGRS03'),('PCGVA03'),('PCGVE03'),('PCGVI03'),('PCGVL01'),('PCGVL03'),('PESCO25'),('PESEM17'),('PESGR07'),('PESGR10'),('PESGR21'),('PESGR22'),('PESP607'),('PESP610'),('PG3EN01'),('PG3EN08'),('PM5EN04'),('PREBS07'),('PRECE01'),('PRECE02'),('PRECS01'),('PREEF26'),('PREEM17'),('PREFS11'),('PREFS12'),('PREGG12'),('PREGR07'),('PREGR10'),('PREGR23'),('PREGR24'),('PREGR25'),('PRELG02'),('PREMC11'),('PREO407'),('PREP107'),('PREP108'),('PREP112'),('PREP113'),('PREP607'),('PBAR002'),('PCMNE01'),('PREP111'),('PCFVV03'),('MAREGR11'),('RMREP614'),('PESEM11'),('MREP621'),('MREP622'),('RREGR10'),('RPREP607'),('CSER026'),('PREGR27'),('PREGR29'),('PBSMZ22'),('RMREP620'),('CSER208'),('PESEM12'),('AREGR10'),('AE1GR01'),('AR1GR10'),('ABEGR01'),('PBAR003'),('MAM5ESCNI'),('PESGG12'),('RPREBS07'),('RPBSMZ08'),('PRECCN2'),('MGSMDLZ'),('ZTAR003'),('ZTAR004'),('ZTAR005'),('CSER209'),('MGL01'),('PREEF27'),('FEUR10'),('JS109'),('EX45'),('SEÑ1600'),('PCGEAZ1'),('MREGR23'),('ZEMP006'),('MAREGR15'),('PESCO40'),('PPIL001'),('ZBES010'),('ZBES005'),('ZBESM907'),('ZBRE010'),('ZBRE005'),('PPIL002'),('PPIL003'),('ZSAC004'),('MAM5CESGR2'),('RSERMAQ04'),('RSERMAQ05'),('RSERMAQ06'),('PILCJA01'),('PILCJA02'),('FLSER001'),('LBACE01'),('ZEDU007'))
    AND m.CIDDOCUMENTODE = 4
    AND dm.CMODULO = 1
    {year_filter}
    {month_filter}
    {agente_condition}
GROUP BY
    YEAR(m.CFECHA),
    MONTH(m.CFECHA) 
ORDER BY 
    YEAR(m.CFECHA),
    MONTH(m.CFECHA);"""
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Consulta para ventas por agente día (CORREGIDA)
def get_ventas_agente_dia(agente=None, fecha=None, anio1=None, mes1=None, dia_inicio=None, dia_fin=None, anio2=None, mes2=None):
    conn = get_db_connection()
    
    # Construir las condiciones dinámicamente
    agente_condition = ""
    if agente and agente != 'Todos':
        agente_condition = f"AND a.CNOMBREAGENTE = '{agente}'"
    
    fecha_condition = ""
    if fecha:
        fecha_condition = f"AND CONVERT(DATE, m.CFECHA) = '{fecha}'"
    elif anio1 and mes1:  # Range mode
        if dia_inicio and dia_fin:
            if anio2 and mes2:  # Comparison mode
                fecha_condition = f"""AND (
                    (YEAR(m.CFECHA) = {anio1} AND MONTH(m.CFECHA) = {mes1} AND DAY(m.CFECHA) BETWEEN {dia_inicio} AND {dia_fin})
                    OR (YEAR(m.CFECHA) = {anio2} AND MONTH(m.CFECHA) = {mes2} AND DAY(m.CFECHA) BETWEEN {dia_inicio} AND {dia_fin})
                )"""
            else:  # Single month range
                fecha_condition = f"AND YEAR(m.CFECHA) = {anio1} AND MONTH(m.CFECHA) = {mes1} AND DAY(m.CFECHA) BETWEEN {dia_inicio} AND {dia_fin}"
        else:  # Full month
            if anio2 and mes2:  # Comparison mode
                fecha_condition = f"""AND (
                    (YEAR(m.CFECHA) = {anio1} AND MONTH(m.CFECHA) = {mes1})
                    OR (YEAR(m.CFECHA) = {anio2} AND MONTH(m.CFECHA) = {mes2})
                )"""
            else:  # Single month
                fecha_condition = f"AND YEAR(m.CFECHA) = {anio1} AND MONTH(m.CFECHA) = {mes1}"
    query = f"""
    SELECT
        d.CRAZONSOCIAL,
        p.CCODIGOPRODUCTO,
        p.CNOMBREPRODUCTO,
        CONVERT(DATE, m.CFECHA) AS Fecha,
        a.CNOMBREAGENTE AS Agente,
        CASE
            WHEN p.CNOMBREPRODUCTO LIKE '%BOLSA%' THEN 'Empaquetado'
            WHEN p.CNOMBREPRODUCTO LIKE '%GLUCOSA%' THEN 'Glucosa'
            WHEN p.CNOMBREPRODUCTO LIKE '%ALMIDON%' THEN 'Almidon'
            WHEN p.CNOMBREPRODUCTO LIKE '%PILONCILLO%' THEN 'Piloncillo'
            WHEN p.CNOMBREPRODUCTO LIKE '%PULVER%' THEN 'Pulverizada'
            WHEN p.CNOMBREPRODUCTO LIKE '%CASTER%' THEN 'Confeccion'
            WHEN p.CNOMBREPRODUCTO LIKE '%MIX%' THEN 'Confeccion'
            WHEN p.CNOMBREPRODUCTO LIKE '%EXTRA%' THEN 'Confeccion'
            WHEN p.CNOMBREPRODUCTO LIKE '%ENDULZANTE%' THEN 'Sucralosa'
            WHEN p.CNOMBREPRODUCTO LIKE '%SERVICIO%' THEN 'Servicio de Maniobras'
            WHEN p.CCODIGOPRODUCTO LIKE '%CO%' THEN 'Confeccion'
            WHEN p.CCODIGOPRODUCTO LIKE '%PREGR%' THEN 'Refinada Granulada'
            WHEN p.CCODIGOPRODUCTO LIKE '%PESGR%' THEN 'Estandar Granulada'
            ELSE 'otro'
        END AS Categoria,
        CASE
            WHEN a.CNOMBREAGENTE = 'MOLIENDAS' THEN 'Moliendas'
            ELSE 'Switen'
        END AS TipoAgente,
        SUM(m.CUNIDADES) AS Unidades,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) / 1000.0 AS Toneladas
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    JOIN admDocumentos d ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN admAgentes a ON d.CIDAGENTE = a.CIDAGENTE
    WHERE
        p.CCODIGOPRODUCTO IN (
        'MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620',
        'PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09',
        'PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03',
        'PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03',
        'PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03',
        'PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25',
        'PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01',
        'PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17',
        'PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25',
        'PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607',
        'PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621',
        'MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620',
        'CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI',
        'PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005',
        'CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23',
        'ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010',
        'ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05',
        'RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007'
        )
        AND (
            m.CIDDOCUMENTODE = 4
            OR (m.CIDDOCUMENTODE = 3 AND dm.CMODULO = 1)
        )
        AND a.CNOMBREAGENTE IN (
            'MAYOREO / SPOT',
            'MOLIENDAS',
            'JAVIER ARROYO',
            'MOLIENDAS MAQ MDLZ',
            'MDLZ P2',
            'MOSTRADOR 1',
            'MOSTRADOR 2',
            'MOSTRADOR 3'
        )
        {agente_condition}
        {fecha_condition}
    GROUP BY
        d.CRAZONSOCIAL,
        p.CCODIGOPRODUCTO,
        p.CNOMBREPRODUCTO,
        CONVERT(DATE, m.CFECHA),
        a.CNOMBREAGENTE,
        -- Columnas CASE
        CASE
            WHEN p.CNOMBREPRODUCTO LIKE '%BOLSA%' THEN 'Empaquetado'
            WHEN p.CNOMBREPRODUCTO LIKE '%GLUCOSA%' THEN 'Glucosa'
            WHEN p.CNOMBREPRODUCTO LIKE '%ALMIDON%' THEN 'Almidon'
            WHEN p.CNOMBREPRODUCTO LIKE '%PILONCILLO%' THEN 'Piloncillo'
            WHEN p.CNOMBREPRODUCTO LIKE '%PULVER%' THEN 'Pulverizada'
            WHEN p.CNOMBREPRODUCTO LIKE '%CASTER%' THEN 'Confeccion'
            WHEN p.CNOMBREPRODUCTO LIKE '%MIX%' THEN 'Confeccion'
            WHEN p.CNOMBREPRODUCTO LIKE '%EXTRA%' THEN 'Confeccion'
            WHEN p.CNOMBREPRODUCTO LIKE '%ENDULZANTE%' THEN 'Sucralosa'
            WHEN p.CNOMBREPRODUCTO LIKE '%SERVICIO%' THEN 'Servicio de Maniobras'
            WHEN p.CCODIGOPRODUCTO LIKE '%CO%' THEN 'Confeccion'
            WHEN p.CCODIGOPRODUCTO LIKE '%PREGR%' THEN 'Refinada Granulada'
            WHEN p.CCODIGOPRODUCTO LIKE '%PESGR%' THEN 'Estandar Granulada'
            ELSE 'otro'
        END,
        CASE
            WHEN a.CNOMBREAGENTE = 'MOLIENDAS' THEN 'Moliendas'
            ELSE 'Switen'
        END
    ORDER BY Fecha DESC, Agente;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Función para obtener datos de ventas por día para gráfico de comparación
def get_ventas_dia_for_graph(agente=None, anio1=None, mes1=None, dia_inicio=None, dia_fin=None, anio2=None, mes2=None):
    conn = get_db_connection()
    
    # Construir las condiciones dinámicamente
    agente_condition = ""
    if agente and agente != 'Todos':
        agente_condition = f"AND a.CNOMBREAGENTE = '{agente}'"
    
    fecha_condition = ""
    if anio1 and mes1:
        if dia_inicio and dia_fin:
            if anio2 and mes2:  # Comparison mode
                fecha_condition = f"""AND (
                    (YEAR(m.CFECHA) = {anio1} AND MONTH(m.CFECHA) = {mes1} AND DAY(m.CFECHA) BETWEEN {dia_inicio} AND {dia_fin})
                    OR (YEAR(m.CFECHA) = {anio2} AND MONTH(m.CFECHA) = {mes2} AND DAY(m.CFECHA) BETWEEN {dia_inicio} AND {dia_fin})
                )"""
            else:  # Single month range
                fecha_condition = f"AND YEAR(m.CFECHA) = {anio1} AND MONTH(m.CFECHA) = {mes1} AND DAY(m.CFECHA) BETWEEN {dia_inicio} AND {dia_fin}"
        else:  # Full month
            if anio2 and mes2:  # Comparison mode
                fecha_condition = f"""AND (
                    (YEAR(m.CFECHA) = {anio1} AND MONTH(m.CFECHA) = {mes1})
                    OR (YEAR(m.CFECHA) = {anio2} AND MONTH(m.CFECHA) = {mes2})
                )"""
            else:  # Single month
                fecha_condition = f"AND YEAR(m.CFECHA) = {anio1} AND MONTH(m.CFECHA) = {mes1}"
    
    query = f"""
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        DAY(m.CFECHA) AS Dia,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) / 1000.0 AS ToneladasTotales
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    JOIN admDocumentos d ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN admAgentes a ON d.CIDAGENTE = a.CIDAGENTE
    WHERE
        p.CCODIGOPRODUCTO IN (
        'MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620',
        'PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09',
        'PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03',
        'PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03',
        'PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03',
        'PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25',
        'PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01',
        'PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17',
        'PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25',
        'PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607',
        'PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621',
        'MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620',
        'CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI',
        'PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005',
        'CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23',
        'ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010',
        'ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05',
        'RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007'
        )
        AND (
            m.CIDDOCUMENTODE = 4
            OR (m.CIDDOCUMENTODE = 3 AND dm.CMODULO = 1)
        )
        AND a.CNOMBREAGENTE IN (
            'MAYOREO / SPOT',
            'MOLIENDAS',
            'JAVIER ARROYO',
            'MOLIENDAS MAQ MDLZ',
            'MDLZ P2',
            'MOSTRADOR 1',
            'MOSTRADOR 2',
            'MOSTRADOR 3'
        )
        {agente_condition}
        {fecha_condition}
    GROUP BY
        YEAR(m.CFECHA),
        MONTH(m.CFECHA),
        DAY(m.CFECHA)
    ORDER BY Anio, Mes, Dia;
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Consulta para ventas por agente mes (CORREGIDA)
def get_ventas_agente_mes(agente=None, anio=None, mes=None):
    conn = get_db_connection()
    
    # Construir las condiciones dinámicamente
    agente_condition = ""
    if agente and agente != 'Todos':
        agente_condition = f"AND a.CNOMBREAGENTE = '{agente}'"
    
    fecha_condition = ""
    if anio and mes:
        fecha_condition = f"AND YEAR(m.CFECHA) = {anio} AND MONTH(m.CFECHA) = {mes}"
    
    query = f"""
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        a.CNOMBREAGENTE AS Agente,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) AS KilosTotales,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) / 1000.0 AS ToneladasTotales
    FROM admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    JOIN admDocumentos d ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN admAgentes a ON d.CIDAGENTE = a.CIDAGENTE
    WHERE
        p.CCODIGOPRODUCTO IN (
                    'MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620',
                    'PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09',
                    'PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03',
                    'PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03',
                    'PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03',
                    'PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25',
                    'PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01',
                    'PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17',
                    'PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25',
                    'PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607',
                    'PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621',
                    'MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620',
                    'CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI',
                    'PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005',
                    'CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23',
                    'ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010',
                    'ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05',
                    'RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007'
        )
        AND (
            m.CIDDOCUMENTODE = 4
            OR (m.CIDDOCUMENTODE = 4 AND dm.CMODULO = 1)
        )
        AND a.CNOMBREAGENTE IN (
            'MAYOREO / SPOT',
            'MOLIENDAS',
            'JAVIER ARROYO',
            'MOLIENDAS MAQ MDLZ',
            'MDLZ P2',
            'MOSTRADOR 1',
            'MOSTRADOR 2',
            'MOSTRADOR 3'
        )
        {agente_condition}
        {fecha_condition}
    GROUP BY
        YEAR(m.CFECHA),
        MONTH(m.CFECHA),
        a.CNOMBREAGENTE
    ORDER BY Anio, Mes, Agente;
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Consulta para objetivos de venta
def get_objetivos_venta(agente=None):
    conn = get_db_connection()
    
    # Construir la condición del agente dinámicamente
    agente_condition = ""
    if agente and agente != 'Todos':
        agente_condition = f"AND a.CNOMBREAGENTE = '{agente}'"
    
    # No usar filtro de mes en la función principal de objetivos
    mes_condition = ""
    # Consulta corregida para objetivos - usando datos históricos del mismo periodo del año anterior como objetivo
    query = f"""SELECT 
    actual.Agente,
    actual.Anio,
    actual.Mes,
    ISNULL(objetivo.ToneladasTotales, 0) AS Objetivo,
    actual.ToneladasTotales AS Avance,
    CASE 
        WHEN ISNULL(objetivo.ToneladasTotales, 0) > 0 
        THEN (actual.ToneladasTotales * 100.0) / objetivo.ToneladasTotales 
        ELSE NULL 
    END AS PorcAvance,
    AVG(actual.ToneladasTotales) OVER (PARTITION BY actual.Agente, actual.Mes) AS Tendencia,
    actual.ToneladasTotales / DAY(EOMONTH(DATEFROMPARTS(actual.Anio, actual.Mes, 1))) AS PromedioDiario
FROM (
    -- Datos actuales (últimos 2 años)
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        a.CNOMBREAGENTE AS Agente,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) / 1000.0 AS ToneladasTotales
    FROM admMovimientos m WITH (NOLOCK)
    JOIN admProductos p WITH (NOLOCK) ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentos d WITH (NOLOCK) ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN admAgentes a WITH (NOLOCK) ON d.CIDAGENTE = a.CIDAGENTE
    WHERE p.CCODIGOPRODUCTO IN (
        'MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620',
        'PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09',
        'PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03',
        'PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03',
        'PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03',
        'PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25',
        'PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01',
        'PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17',
        'PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25',
        'PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607',
        'PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621',
        'MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620',
        'CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI',
        'PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005',
        'CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23',
        'ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010',
        'ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05',
        'RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007'
    )
    AND m.CIDDOCUMENTODE = 4
    AND a.CNOMBREAGENTE IN (
        'MAYOREO / SPOT','MOLIENDAS','JAVIER ARROYO','MOLIENDAS MAQ MDLZ',
        'MDLZ P2','MOSTRADOR 1','MOSTRADOR 2','MOSTRADOR 3'
    )
    {agente_condition}
    {mes_condition}
    AND m.CFECHA >= DATEADD(year, -2, GETDATE())  -- Last 2 years for current data
    GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA), a.CNOMBREAGENTE
) actual
LEFT JOIN (
    -- Datos históricos para objetivos (mismo mes del año anterior)
    SELECT
        YEAR(m.CFECHA) AS AnioObjetivo,  -- Year of historical data
        MONTH(m.CFECHA) AS Mes,
        a.CNOMBREAGENTE AS Agente,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) / 1000.0 AS ToneladasTotales
    FROM admMovimientos m WITH (NOLOCK)
    JOIN admProductos p WITH (NOLOCK) ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentos d WITH (NOLOCK) ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN admAgentes a WITH (NOLOCK) ON d.CIDAGENTE = a.CIDAGENTE
    WHERE p.CCODIGOPRODUCTO IN (
        'MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620',
        'PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09',
        'PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03',
        'PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03',
        'PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03',
        'PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25',
        'PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01',
        'PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17',
        'PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25',
        'PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607',
        'PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621',
        'MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620',
        'CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI',
        'PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005',
        'CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23',
        'ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010',
        'ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05',
        'RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007'
    )
    AND m.CIDDOCUMENTODE = 4
    AND a.CNOMBREAGENTE IN (
        'MAYOREO / SPOT','MOLIENDAS','JAVIER ARROYO','MOLIENDAS MAQ MDLZ',
        'MDLZ P2','MOSTRADOR 1','MOSTRADOR 2','MOSTRADOR 3'
    )
    {agente_condition}
    {mes_condition}
    AND YEAR(m.CFECHA) >= YEAR(GETDATE()) - 2  -- Get data from 2 years ago
    AND YEAR(m.CFECHA) < YEAR(GETDATE())       -- Up to last year
    GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA), a.CNOMBREAGENTE
) objetivo ON actual.Agente = objetivo.Agente 
                AND actual.Mes = objetivo.Mes 
                AND actual.Anio = objetivo.AnioObjetivo + 1
ORDER BY actual.Agente, actual.Anio DESC, actual.Mes DESC;"""  # Mantén tu consulta
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Función para obtener resumen de avance por agente
def get_objetivos_summary(agente=None, mes=None):
    conn = get_db_connection()
    
    # Construir la condición del agente dinámicamente
    agente_condition = ""
    if agente and agente != 'Todos':
        agente_condition = f"AND a.CNOMBREAGENTE = '{agente}'"
    
    # Construir la condición del mes dinámicamente
    mes_condition = ""
    if mes and mes != 'Todos':
        mes_condition = f"AND MONTH(m.CFECHA) = {mes}"
    
    query = f"""SELECT 
    actual.Agente,
    ISNULL(AVG(CASE WHEN ISNULL(objetivo.ToneladasTotales, 0) > 0 
                    THEN (actual.ToneladasTotales * 100.0) / objetivo.ToneladasTotales 
                    ELSE NULL END), 0) AS PromedioAvance,
    COUNT(*) AS TotalRegistros,
    SUM(actual.ToneladasTotales) AS TotalVentas,
    SUM(ISNULL(objetivo.ToneladasTotales, 0)) AS TotalObjetivos
FROM (
    -- Datos actuales (últimos 2 años)
    SELECT
        YEAR(m.CFECHA) AS Anio,
        MONTH(m.CFECHA) AS Mes,
        a.CNOMBREAGENTE AS Agente,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) / 1000.0 AS ToneladasTotales
    FROM admMovimientos m WITH (NOLOCK)
    JOIN admProductos p WITH (NOLOCK) ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentos d WITH (NOLOCK) ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN admAgentes a WITH (NOLOCK) ON d.CIDAGENTE = a.CIDAGENTE
    WHERE p.CCODIGOPRODUCTO IN (
        'MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620',
        'PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09',
        'PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03',
        'PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03',
        'PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03',
        'PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25',
        'PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01',
        'PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17',
        'PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25',
        'PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607',
        'PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621',
        'MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620',
        'CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI',
        'PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005',
        'CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23',
        'ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010',
        'ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05',
        'RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007'
    )
    AND m.CIDDOCUMENTODE = 4
    AND a.CNOMBREAGENTE IN (
        'MAYOREO / SPOT','MOLIENDAS','JAVIER ARROYO','MOLIENDAS MAQ MDLZ',
        'MDLZ P2','MOSTRADOR 1','MOSTRADOR 2','MOSTRADOR 3'
    )
    {agente_condition}
    {mes_condition}
    AND m.CFECHA >= DATEADD(year, -2, GETDATE())  -- Last 2 years for current data
    GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA), a.CNOMBREAGENTE
) actual
LEFT JOIN (
    -- Datos históricos para objetivos (mismo mes del año anterior)
    SELECT
        YEAR(m.CFECHA) AS AnioObjetivo,  -- Year of historical data
        MONTH(m.CFECHA) AS Mes,
        a.CNOMBREAGENTE AS Agente,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) / 1000.0 AS ToneladasTotales
    FROM admMovimientos m WITH (NOLOCK)
    JOIN admProductos p WITH (NOLOCK) ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentos d WITH (NOLOCK) ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN admAgentes a WITH (NOLOCK) ON d.CIDAGENTE = a.CIDAGENTE
    WHERE p.CCODIGOPRODUCTO IN (
        'MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620',
        'PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09',
        'PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03',
        'PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03',
        'PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03',
        'PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25',
        'PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01',
        'PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17',
        'PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25',
        'PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607',
        'PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621',
        'MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620',
        'CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI',
        'PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005',
        'CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23',
        'ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010',
        'ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05',
        'RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007'
    )
    AND m.CIDDOCUMENTODE = 4
    AND a.CNOMBREAGENTE IN (
        'MAYOREO / SPOT','MOLIENDAS','JAVIER ARROYO','MOLIENDAS MAQ MDLZ',
        'MDLZ P2','MOSTRADOR 1','MOSTRADOR 2','MOSTRADOR 3'
    )
    {agente_condition}
    {mes_condition}
    AND YEAR(m.CFECHA) >= YEAR(GETDATE()) - 2  -- Get data from 2 years ago
    AND YEAR(m.CFECHA) < YEAR(GETDATE())       -- Up to last year
    GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA), a.CNOMBREAGENTE
) objetivo ON actual.Agente = objetivo.Agente 
                AND actual.Mes = objetivo.Mes 
                AND actual.Anio = objetivo.AnioObjetivo + 1
GROUP BY actual.Agente
ORDER BY PromedioAvance DESC;"""
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Función para obtener datos de cobertura de clientes
def get_cobertura_clientes(anio=None, agente=None):
    conn = get_db_connection()
    
    if not anio:
        anio = datetime.now().year
    
    query = f"""WITH VentasMensuales AS (
    SELECT
        d.CRAZONSOCIAL AS RazonSocial,
        a.CNOMBREAGENTE AS Agente,
        DATENAME(MONTH, m.CFECHA) AS Mes,
        YEAR(m.CFECHA) AS Anio,
        SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' OR p.CNOMBREPRODUCTO LIKE '%1KG%' OR p.CNOMBREPRODUCTO LIKE '%1. KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' OR p.CNOMBREPRODUCTO LIKE '%25KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 25%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' OR p.CNOMBREPRODUCTO LIKE '%50KG%' OR p.CNOMBREPRODUCTO LIKE '%SACO 50%' THEN m.CUNIDADES * 50
                WHEN p.CNOMBREPRODUCTO LIKE '%907 GR%' OR p.CNOMBREPRODUCTO LIKE '%2 LB%' THEN m.CUNIDADES * 0.907
                WHEN p.CNOMBREPRODUCTO LIKE '%500 GR%' OR p.CNOMBREPRODUCTO LIKE '%0.5 KG%' THEN m.CUNIDADES * 0.5
                WHEN p.CNOMBREPRODUCTO LIKE '%5 KG%' OR p.CNOMBREPRODUCTO LIKE '%5KG%' THEN m.CUNIDADES * 5
                WHEN p.CNOMBREPRODUCTO LIKE '%2 KG%' OR p.CNOMBREPRODUCTO LIKE '%2KG%' THEN m.CUNIDADES * 2
                WHEN p.CNOMBREPRODUCTO LIKE '%20 KG%' OR p.CNOMBREPRODUCTO LIKE '%20KG%' THEN m.CUNIDADES * 20
                WHEN p.CNOMBREPRODUCTO LIKE '%26 KG%' OR p.CNOMBREPRODUCTO LIKE '%26KG%' THEN m.CUNIDADES * 26
                WHEN p.CNOMBREPRODUCTO LIKE '%27 KG%' OR p.CNOMBREPRODUCTO LIKE '%27KG%' THEN m.CUNIDADES * 27
                WHEN p.CNOMBREPRODUCTO LIKE '%50 LB%' THEN m.CUNIDADES * 22.68
                WHEN p.CNOMBREPRODUCTO LIKE '%900 KG%' THEN m.CUNIDADES * 900
                WHEN p.CNOMBREPRODUCTO LIKE '%1000 KG%' THEN m.CUNIDADES * 1000
                ELSE 0
            END
        ) AS KilosTotales,
        'Vendido' AS Estado
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN
        admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
    JOIN 
        admDocumentos d ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN 
        admAgentes a ON d.CIDAGENTE = a.CIDAGENTE
    WHERE
        p.CCODIGOPRODUCTO IN (
            'MESCO25','MESCO30','MESPU07','MREGR26','MREGR30','MREP613','MREP614','MREP620',
            'PAL0007','PAL0008','PAL0009','PBSMZ04','PBSMZ05','PBSMZ06','PBSMZ08','PBSMZ09',
            'PBSMZ11','PBSMZ14','PCAGF02','PCAGF03','PCAGF04','PCFAI03','PCFAM03','PCFAZ03',
            'PCFMO03','PCFMO05','PCFNA03','PCFNE03','PCFRS03','PCFVA03','PCFVE03','PCFVI03',
            'PCFVL03','PCGAI03','PCGAM03','PCGAZ03','PCGMO03','PCGNA03','PCGNE03','PCGRF03',
            'PCGRO03','PCGRS03','PCGVA03','PCGVE03','PCGVI03','PCGVL01','PCGVL03','PESCO25',
            'PESEM17','PESGR07','PESGR10','PESGR21','PESGR22','PESP607','PESP610','PG3EN01',
            'PG3EN08','PM5EN04','PREBS07','PRECE01','PRECE02','PRECS01','PREEF26','PREEM17',
            'PREFS11','PREFS12','PREGG12','PREGR07','PREGR10','PREGR23','PREGR24','PREGR25',
            'PRELG02','PREMC11','PREO407','PREP107','PREP108','PREP112','PREP113','PREP607',
            'PBAR002','PCMNE01','PREP111','PCFVV03','MAREGR11','RMREP614','PESEM11','MREP621',
            'MREP622','RREGR10','RPREP607','CSER026','PREGR27','PREGR29','PBSMZ22','RMREP620',
            'CSER208','PESEM12','AREGR10','AE1GR01','AR1GR10','ABEGR01','PBAR003','MAM5ESCNI',
            'PESGG12','RPREBS07','RPBSMZ08','PRECCN2','MGSMDLZ','ZTAR003','ZTAR004','ZTAR005',
            'CSER209','MGL01','PREEF27','FEUR10','JS109','EX45','SEÑ1600','PCGEAZ1','MREGR23',
            'ZEMP006','MAREGR15','PESCO40','PPIL001','ZBES010','ZBES005','ZBESM907','ZBRE010',
            'ZBRE005','PPIL002','PPIL003','ZSAC004','MAM5CESGR2','RSERMAQ04','RSERMAQ05',
            'RSERMAQ06','PILCJA01','PILCJA02','FLSER001','LBACE01','ZEDU007'
        )
        AND (
            m.CIDDOCUMENTODE = 4
            OR (m.CIDDOCUMENTODE = 4 AND dm.CMODULO = 1)
        )
        AND a.CNOMBREAGENTE IN (
            'MAYOREO / SPOT',
            'MOLIENDAS',
            'JAVIER ARROYO',
            'MOLIENDAS MAQ MDLZ',
            'MDLZ P2',
            'MOSTRADOR 1',
            'MOSTRADOR 2',
            'MOSTRADOR 3'
        )
        AND YEAR(m.CFECHA) = {anio}
        {f"AND a.CNOMBREAGENTE = '{agente}'" if agente and agente != 'Todos' else ""}
    GROUP BY
        d.CRAZONSOCIAL,
        a.CNOMBREAGENTE,
        DATENAME(MONTH, m.CFECHA),
        YEAR(m.CFECHA)
),
ClientesUnicos AS (
    SELECT DISTINCT CRAZONSOCIAL
    FROM admDocumentos
    WHERE CRAZONSOCIAL IN (SELECT RazonSocial FROM VentasMensuales)
),
Meses AS (
    SELECT 'Enero' AS Mes, 1 AS Orden
    UNION SELECT 'Febrero', 2
    UNION SELECT 'Marzo', 3
    UNION SELECT 'Abril', 4
    UNION SELECT 'Mayo', 5
    UNION SELECT 'Junio', 6
    UNION SELECT 'Julio', 7
    UNION SELECT 'Agosto', 8
    UNION SELECT 'Septiembre', 9
    UNION SELECT 'Octubre', 10
    UNION SELECT 'Noviembre', 11
    UNION SELECT 'Diciembre', 12
),
ClientesMeses AS (
    SELECT 
        c.CRAZONSOCIAL AS RazonSocial,
        m.Mes,
        {anio} AS Anio,
        'Pendiente' AS Estado
    FROM 
        ClientesUnicos c
    CROSS JOIN 
        Meses m
)
SELECT 
    COALESCE(v.RazonSocial, cm.RazonSocial) AS RazonSocial,
    COALESCE(v.Mes, cm.Mes) AS Mes,
    COALESCE(v.Estado, cm.Estado) AS Estado,
    COALESCE(v.Anio, cm.Anio) AS Anio,
    v.Agente,
    ISNULL(v.KilosTotales, 0) AS KilosTotales
FROM 
    VentasMensuales v
FULL OUTER JOIN 
    ClientesMeses cm ON v.RazonSocial = cm.RazonSocial AND v.Mes = cm.Mes AND v.Anio = cm.Anio
WHERE 
    COALESCE(v.RazonSocial, cm.RazonSocial) IS NOT NULL
ORDER BY 
    COALESCE(v.RazonSocial, cm.RazonSocial),
    (SELECT Orden FROM Meses WHERE Mes = COALESCE(v.Mes, cm.Mes));"""
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Función para obtener datos de cobertura en formato matricial
def get_cobertura_matricial(anio=None, agente=None):
    conn = get_db_connection()
    
    if not anio:
        anio = datetime.now().year
    
    query = f"""
    SELECT
        d.CRAZONSOCIAL AS RazonSocial,
        a.CNOMBREAGENTE AS Agente,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 1 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Enero,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 2 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Febrero,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 3 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Marzo,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 4 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Abril,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 5 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Mayo,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 6 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Junio,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 7 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Julio,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 8 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Agosto,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 9 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Septiembre,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 10 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Octubre,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 11 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Noviembre,
        ISNULL(SUM(CASE WHEN MONTH(m.CFECHA) = 12 THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Diciembre,
        ISNULL(SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END
        ), 0) AS TotalAnual
    FROM 
        admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentos d ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN admAgentes a ON d.CIDAGENTE = a.CIDAGENTE
    WHERE
        YEAR(m.CFECHA) = {anio}
        AND a.CNOMBREAGENTE IN (
            'MAYOREO / SPOT', 'MOLIENDAS', 'JAVIER ARROYO',
            'MOLIENDAS MAQ MDLZ', 'MDLZ P2', 'MOSTRADOR 1',
            'MOSTRADOR 2', 'MOSTRADOR 3'
        )
        {f"AND a.CNOMBREAGENTE = '{agente}'" if agente and agente != 'Todos' else ""}
    GROUP BY d.CRAZONSOCIAL, a.CNOMBREAGENTE
    ORDER BY d.CRAZONSOCIAL
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@app.route('/set_language/<language>')
def set_language(language):
    """Set language preference"""
    if language in LANGUAGES:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    return redirect(url_for('reporte_anio'))

@app.route('/reporte_anio')
def reporte_anio():
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    # Get graph parameters
    year1 = request.args.get('year1', type=int)
    year2 = request.args.get('year2', type=int)
    start_month = int(request.args.get('start_month', 1))
    end_month = int(request.args.get('end_month', 12))
    
    # Get agent parameter
    selected_agente = request.args.get('agente', 'Todos')
    
    df = get_reporte_anio(selected_agente)
    
    # Calculate pagination
    total_records = len(df)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Slice dataframe for current page
    df_page = df.iloc[start_idx:end_idx]
    
    # Pagination info
    total_pages = math.ceil(total_records / per_page)
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total_records,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }
    
    # Get graph data if parameters provided
    graph_data = None
    if year1 or year2:
        graph_df = get_reporte_anio_for_graph(year1, year2, start_month, end_month, selected_agente)
        graph_data = graph_df.to_dict('records')
    
    # Get available years for dropdowns
    available_years = list(range(2020, 2026))  # Adjust range as needed
    
    # Agent list
    agentes = [
        'MAYOREO / SPOT', 'MOLIENDAS', 'JAVIER ARROYO',
        'MOLIENDAS MAQ MDLZ', 'MDLZ P2', 'MOSTRADOR 1',
        'MOSTRADOR 2', 'MOSTRADOR 3', 'Todos'
    ]
    
    translations = get_translations()
    return render_template('enhanced_table_with_graph.html', 
                           title=translations['ui']['year_report'],
                           data=df_page.to_dict('records'),
                           columns=df.columns.tolist(),
                           pagination=pagination_info,
                           graph_data=graph_data,
                           available_years=available_years,
                           selected_year1=year1,
                           selected_year2=year2,
                           selected_start_month=start_month,
                           selected_end_month=end_month,
                           agentes=agentes,
                           selected_agente=selected_agente,
                           translations=translations,
                           languages=LANGUAGES,
                           current_lang=get_language())

# Export routes for yearly report
@app.route('/export_reporte_anio_excel')
def export_reporte_anio_excel():
    agente = request.args.get('agente', 'Todos')
    df = get_reporte_anio(agente)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Reporte Anual', index=False)
    
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_anual_{agente}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response

@app.route('/export_reporte_anio_html')
def export_reporte_anio_html():
    agente = request.args.get('agente', 'Todos')
    df = get_reporte_anio(agente)
    translations = get_translations()
    
    # Generate HTML table
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Reporte Anual - {agente}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #e65100; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .header {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Reporte Anual</h1>
            <p><strong>Agente:</strong> {agente}</p>
            <p><strong>Fecha de Exportación:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Total de Registros:</strong> {len(df)}</p>
        </div>
        {df.to_html(classes='table table-striped', table_id='reporte-table', escape=False, index=False)}
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_anual_{agente}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    
    return response

# Export routes for Daily Sales
@app.route('/export_ventas_dia_excel')
def export_ventas_dia_excel():
    agente = request.args.get('agente', 'Todos')
    fecha = request.args.get('fecha', '')
    anio1 = request.args.get('anio1', '')
    mes1 = request.args.get('mes1', '')
    dia_inicio = request.args.get('dia_inicio', '')
    dia_fin = request.args.get('dia_fin', '')
    anio2 = request.args.get('anio2', '')
    mes2 = request.args.get('mes2', '')
    
    # Get complete dataset without pagination
    df, _ = get_ventas_agente_dia(agente, fecha, anio1, mes1, dia_inicio, dia_fin, anio2, mes2, page=1, per_page=999999)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Ventas Diarias', index=False)
    
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=ventas_diarias_{agente}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response

@app.route('/export_ventas_dia_html')
def export_ventas_dia_html():
    agente = request.args.get('agente', 'Todos')
    fecha = request.args.get('fecha', '')
    anio1 = request.args.get('anio1', '')
    mes1 = request.args.get('mes1', '')
    dia_inicio = request.args.get('dia_inicio', '')
    dia_fin = request.args.get('dia_fin', '')
    anio2 = request.args.get('anio2', '')
    mes2 = request.args.get('mes2', '')
    
    # Get complete dataset without pagination
    df, _ = get_ventas_agente_dia(agente, fecha, anio1, mes1, dia_inicio, dia_fin, anio2, mes2, page=1, per_page=999999)
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Ventas Diarias - {agente}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #e65100; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .header {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Ventas Diarias</h1>
            <p><strong>Agente:</strong> {agente}</p>
            <p><strong>Fecha de Exportación:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Total de Registros:</strong> {len(df)}</p>
        </div>
        {df.to_html(classes='table table-striped', table_id='ventas-table', escape=False, index=False)}
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename=ventas_diarias_{agente}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    
    return response

# Export routes for Monthly Sales
@app.route('/export_ventas_mes_excel')
def export_ventas_mes_excel():
    agente = request.args.get('agente', 'Todos')
    anio = request.args.get('anio', '')
    mes = request.args.get('mes', '')
    
    # Get complete dataset without pagination
    df, _ = get_ventas_agente_mes(agente, anio, mes, page=1, per_page=999999)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Ventas Mensuales', index=False)
    
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=ventas_mensuales_{agente}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response

@app.route('/export_ventas_mes_html')
def export_ventas_mes_html():
    agente = request.args.get('agente', 'Todos')
    anio = request.args.get('anio', '')
    mes = request.args.get('mes', '')
    
    # Get complete dataset without pagination
    df, _ = get_ventas_agente_mes(agente, anio, mes, page=1, per_page=999999)
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Ventas Mensuales - {agente}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #e65100; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .header {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Ventas Mensuales</h1>
            <p><strong>Agente:</strong> {agente}</p>
            <p><strong>Fecha de Exportación:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Total de Registros:</strong> {len(df)}</p>
        </div>
        {df.to_html(classes='table table-striped', table_id='ventas-table', escape=False, index=False)}
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename=ventas_mensuales_{agente}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    
    return response

@app.route('/ventas_agente_dia', methods=['GET', 'POST'])
def ventas_agente_dia():
    agentes = [
        'MAYOREO / SPOT', 'MOLIENDAS', 'JAVIER ARROYO',
        'MOLIENDAS MAQ MDLZ', 'MDLZ P2', 'MOSTRADOR 1',
        'MOSTRADOR 2', 'MOSTRADOR 3', 'Todos'
    ]
    
    selected_agente = request.args.get('agente', 'Todos')
    # Default to current month view
    current_date = datetime.now()
    selected_anio1 = int(request.args.get('anio1', current_date.year))
    selected_mes1 = int(request.args.get('mes1', current_date.month))
    selected_dia_inicio = int(request.args.get('dia_inicio', 1))
    # Get last day of current month
    import calendar
    selected_dia_fin = int(request.args.get('dia_fin', calendar.monthrange(selected_anio1, selected_mes1)[1]))
    
    # Comparison parameters
    selected_anio2 = request.args.get('anio2', type=int)
    selected_mes2 = request.args.get('mes2', type=int)
    
    # For backwards compatibility with single date mode
    selected_fecha = request.args.get('fecha')
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    # Graph data
    graph_data = None
    
    if request.method == 'POST':
        selected_agente = request.form.get('agente', 'Todos')
        
        # Check if it's single date mode or range mode
        if request.form.get('fecha'):
            # Single date mode (backwards compatibility)
            selected_fecha = request.form.get('fecha')
            df = get_ventas_agente_dia(selected_agente, selected_fecha)
        else:
            # Range mode
            selected_anio1 = int(request.form.get('anio1', selected_anio1))
            selected_mes1 = int(request.form.get('mes1', selected_mes1))
            selected_dia_inicio = int(request.form.get('dia_inicio', selected_dia_inicio))
            selected_dia_fin = int(request.form.get('dia_fin', selected_dia_fin))
            
            # Optional comparison month
            anio2_val = request.form.get('anio2')
            mes2_val = request.form.get('mes2')
            if anio2_val and mes2_val:
                selected_anio2 = int(anio2_val)
                selected_mes2 = int(mes2_val)
            
            df = get_ventas_agente_dia(selected_agente, None, selected_anio1, selected_mes1, 
                                     selected_dia_inicio, selected_dia_fin, selected_anio2, selected_mes2)
            
            # Get graph data if comparison is enabled
            if selected_anio2 and selected_mes2:
                graph_df = get_ventas_dia_for_graph(selected_agente, selected_anio1, selected_mes1,
                                                  selected_dia_inicio, selected_dia_fin, selected_anio2, selected_mes2)
                if not graph_df.empty:
                    graph_data = graph_df.to_dict('records')
    else:
        # GET request or default: show current month
        if selected_fecha:
            # Single date mode (backwards compatibility)
            df = get_ventas_agente_dia(selected_agente, selected_fecha)
        else:
            # Range mode
            df = get_ventas_agente_dia(selected_agente, None, selected_anio1, selected_mes1, 
                                     selected_dia_inicio, selected_dia_fin, selected_anio2, selected_mes2)
            
            # Get graph data if comparison is enabled
            if selected_anio2 and selected_mes2:
                graph_df = get_ventas_dia_for_graph(selected_agente, selected_anio1, selected_mes1,
                                                  selected_dia_inicio, selected_dia_fin, selected_anio2, selected_mes2)
                if not graph_df.empty:
                    graph_data = graph_df.to_dict('records')
    
    # Calculate pagination
    total_records = len(df)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Slice dataframe for current page
    df_page = df.iloc[start_idx:end_idx]
    
    # Pagination info
    total_pages = math.ceil(total_records / per_page)
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total_records,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }
    
    translations = get_translations()
    # Generate year and month options
    current_year = datetime.now().year
    years = list(range(current_year - 4, current_year + 1))
    months = [
        ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
        ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
        ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ]
    
    return render_template('enhanced_table_with_daily_comparison.html', 
                           title=translations['ui']['daily_sales'],
                           data=df_page.to_dict('records'),
                           columns=df.columns.tolist(),
                           pagination=pagination_info,
                           agentes=agentes,
                           selected_agente=selected_agente,
                           selected_fecha=selected_fecha,
                           selected_anio1=selected_anio1,
                           selected_mes1=selected_mes1,
                           selected_dia_inicio=selected_dia_inicio,
                           selected_dia_fin=selected_dia_fin,
                           selected_anio2=selected_anio2,
                           selected_mes2=selected_mes2,
                           years=years,
                           months=months,
                           graph_data=graph_data,
                           translations=translations,
                           languages=LANGUAGES,
                           current_lang=get_language())

@app.route('/ventas_agente_mes', methods=['GET', 'POST'])
def ventas_agente_mes():
    agentes = [
        'MAYOREO / SPOT', 'MOLIENDAS', 'JAVIER ARROYO',
        'MOLIENDAS MAQ MDLZ', 'MDLZ P2', 'MOSTRADOR 1',
        'MOSTRADOR 2', 'MOSTRADOR 3', 'Todos'
    ]
    
    selected_agente = 'Todos'
    current_date = datetime.now()
    selected_anio = current_date.year  # Default to current year
    selected_mes = current_date.month  # Default to current month
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    if request.method == 'POST':
        selected_agente = request.form.get('agente', 'Todos')
        selected_anio = int(request.form.get('anio', selected_anio))
        selected_mes = int(request.form.get('mes', selected_mes))
    
    df = get_ventas_agente_mes(selected_agente, selected_anio, selected_mes)
    
    # Calculate pagination
    total_records = len(df)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Slice dataframe for current page
    df_page = df.iloc[start_idx:end_idx]
    
    # Pagination info
    total_pages = math.ceil(total_records / per_page)
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total_records,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }
    
    translations = get_translations()
    # Generate year options (last 5 years)
    years = list(range(current_date.year - 4, current_date.year + 1))
    months = [
        ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
        ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
        ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ]
    
    return render_template('enhanced_table_with_month_filter.html', 
                           title=translations['ui']['monthly_sales'],
                           data=df_page.to_dict('records'),
                           columns=df.columns.tolist(),
                           pagination=pagination_info,
                           agentes=agentes,
                           selected_agente=selected_agente,
                           selected_anio=selected_anio,
                           selected_mes=selected_mes,
                           years=years,
                           months=months,
                           translations=translations,
                           languages=LANGUAGES,
                           current_lang=get_language())

@app.route('/objetivos_venta', methods=['GET', 'POST'])
def objetivos_venta():
    agentes = [
        'MAYOREO / SPOT', 'MOLIENDAS', 'JAVIER ARROYO',
        'MOLIENDAS MAQ MDLZ', 'MDLZ P2', 'MOSTRADOR 1',
        'MOSTRADOR 2', 'MOSTRADOR 3', 'Todos'
    ]
    
    # Meses para el filtro
    meses = [
        ('Todos', 'Todos los meses'),
        ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
        ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
        ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ]
    
    selected_agente = 'Todos'
    selected_mes = 'Todos'
    # Get pagination parameters - use smaller default for objectives
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))  # Smaller default for better performance
    
    if request.method == 'POST':
        selected_agente = request.form.get('agente', 'Todos')
        selected_mes = request.form.get('mes', 'Todos')
    
    try:
        df = get_objetivos_venta(selected_agente)
        
        # Get summary data for dashboard
        summary_df = get_objetivos_summary(selected_agente, selected_mes)
        
        # If dataframe is very large, limit it for performance
        if len(df) > 10000:
            # Take only the most recent data for performance
            df = df.tail(5000)  # Keep only last 5000 records for performance
        
        # Calculate pagination
        total_records = len(df)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Slice dataframe for current page
        df_page = df.iloc[start_idx:end_idx]
        
        # Pagination info
        total_pages = math.ceil(total_records / per_page)
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': total_records,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
        
        translations = get_translations()
        return render_template('enhanced_table_objectives_with_filter.html', 
                               title=translations['ui']['sales_objectives'],
                               data=df_page.to_dict('records'),
                               columns=df.columns.tolist(),
                               pagination=pagination_info,
                               agentes=agentes,
                               selected_agente=selected_agente,
                               meses=meses,
                               selected_mes=selected_mes,
                               summary_data=summary_df.to_dict('records') if not summary_df.empty else [],
                               translations=translations,
                               languages=LANGUAGES,
                               current_lang=get_language())
    except Exception as e:
        # If query fails or takes too long, show error page
        translations = get_translations()
        return render_template('error_page.html',
                               error_message="La consulta está tomando demasiado tiempo. Por favor, inténtelo más tarde.",
                               translations=translations,
                               languages=LANGUAGES,
                               current_lang=get_language())

@app.route('/reporte_coberturas', methods=['GET', 'POST'])
def reporte_coberturas():
    selected_anio = datetime.now().year  # Default to current year
    selected_agente = 'Todos'  # Default to all agents
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    if request.method == 'POST':
        selected_anio = int(request.form.get('anio', selected_anio))
        selected_agente = request.form.get('agente', selected_agente)
    
    try:
        # Get detailed coverage data
        df_detalle = get_cobertura_clientes(selected_anio, selected_agente)
        
        # Get matrix coverage data
        df_matriz = get_cobertura_matricial(selected_anio, selected_agente)
        
        # Calculate pagination for detailed data
        total_records = len(df_detalle)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Slice dataframe for current page
        df_detalle_page = df_detalle.iloc[start_idx:end_idx]
        
        # Pagination info
        total_pages = math.ceil(total_records / per_page)
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': total_records,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
        
        # Generate year options (last 5 years)
        current_year = datetime.now().year
        years = list(range(current_year - 4, current_year + 1))
        
        # Agent options
        agentes = ['Todos', 'MAYOREO / SPOT', 'MOLIENDAS', 'JAVIER ARROYO', 'MOLIENDAS MAQ MDLZ', 'MDLZ P2', 'MOSTRADOR 1', 'MOSTRADOR 2', 'MOSTRADOR 3']
        
        translations = get_translations()
        
        print(f"Debug - Detailed data shape: {df_detalle.shape}")
        print(f"Debug - Matrix data shape: {df_matriz.shape}")
        print(f"Debug - Detailed columns: {df_detalle.columns.tolist()}")
        print(f"Debug - Matrix columns: {df_matriz.columns.tolist()}")
        if len(df_detalle) > 0:
            print(f"Debug - First detailed record: {df_detalle.iloc[0].to_dict()}")
        if len(df_matriz) > 0:
            print(f"Debug - First matrix record: {df_matriz.iloc[0].to_dict()}")
        
        return render_template('reporte_coberturas.html', 
                               title=translations['ui']['coverage_report'],
                               data_detalle=df_detalle_page.to_dict('records'),
                               columns_detalle=df_detalle.columns.tolist(),
                               data_matriz=df_matriz.to_dict('records'),
                               columns_matriz=df_matriz.columns.tolist(),
                               pagination=pagination_info,
                               selected_anio=selected_anio,
                               selected_agente=selected_agente,
                               years=years,
                               agentes=agentes,
                               translations=translations,
                               languages=LANGUAGES,
                               current_lang=get_language())
    except Exception as e:
        # If query fails, show error page
        translations = get_translations()
        return render_template('error_page.html',
                               error_message="Error al cargar el reporte de coberturas. Intente más tarde.",
                               translations=translations,
                               languages=LANGUAGES,
                               current_lang=get_language())

if __name__ == '__main__':
    # SSL context for HTTPS
    import ssl
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)
