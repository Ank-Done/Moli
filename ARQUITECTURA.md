# Arquitectura del Sistema - Reportes de Ventas Moliendas y Alimentos

## Resumen del Sistema

Sistema web desarrollado en Flask para generar reportes de ventas basados en datos de Microsoft SQL Server. Proporciona visualización de datos de ventas por periodo con funcionalidades de filtrado y exportación.

## Arquitectura General

```
FlaskReporteApp/
├── app.py                          # Punto de entrada de la aplicación
├── config/
│   ├── __init__.py
│   └── database.py                 # Configuración de base de datos
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── reportes.py            # Lógica de negocio y consultas
│   ├── views/
│   │   ├── __init__.py
│   │   └── routes.py              # Rutas y controladores web
│   ├── templates/
│   │   ├── base.html              # Plantilla base
│   │   ├── dashboard.html         # Página principal
│   │   ├── reporte.html          # Página de reportes con filtros
│   │   └── error.html            # Página de errores
│   ├── static/
│   │   ├── css/                   # Estilos CSS
│   │   ├── js/                    # JavaScript
│   │   ├── img/                   # Imágenes
│   │   └── webfonts/              # Fuentes
│   └── utils/
│       └── __init__.py
├── venv/                          # Entorno virtual Python
└── test_connection.py             # Script de prueba de conexión
```

## Componentes del Sistema

### 1. Capa de Datos (Data Layer)

**Base de datos:** Microsoft SQL Server - `adMOLIENDAS_Y_ALIMENTO`

**Tablas principales utilizadas:**
- `admMovimientos`: Movimientos de inventario y ventas
- `admProductos`: Catálogo de productos
- `admDocumentosModelo`: Tipos de documentos del sistema
- `admClientes`: Información de clientes
- `admDocumentos`: Documentos generados

**Conexión:**
- Driver: ODBC Driver 18 for SQL Server
- Biblioteca: pyodbc + pandas para consultas

### 2. Capa de Modelos (Model Layer)

**Archivo:** `app/models/reportes.py`

**Clase principal:** `ReporteVentas`

**Funcionalidades:**
- `get_productos_disponibles()`: Lista productos válidos con nombres
- `get_ventas_por_periodo()`: Consulta principal de ventas con filtros
- `get_resumen_estadisticas()`: Estadísticas agregadas del periodo
- `get_anos_disponibles()`: Años disponibles en los datos

### 3. Capa de Vista (View Layer)

**Archivo:** `app/views/routes.py`

**Rutas implementadas:**
- `/` - Dashboard principal con estadísticas generales
- `/reporte` - Página de reportes con filtros avanzados
- `/api/reporte-datos` - API REST para obtener datos filtrados
- `/api/exportar-excel` - Exportación a formato Excel

### 4. Capa de Presentación (Presentation Layer)

**Templates Jinja2:**
- `base.html`: Layout común con navegación y estilos
- `dashboard.html`: Vista principal con gráficos y estadísticas
- `reporte.html`: Interfaz de filtros y resultados detallados
- `error.html`: Manejo de errores

**Frontend:**
- Bootstrap 4.6 para responsive design
- Chart.js para visualización de datos
- jQuery para interactividad
- FontAwesome para iconografía

## Flujo de Datos

1. **Usuario accede al sistema** → Templates HTML renderizados
2. **Usuario aplica filtros** → JavaScript envía petición AJAX
3. **Controlador procesa petición** → Valida parámetros y llama al modelo
4. **Modelo ejecuta consulta** → Conexión a SQL Server vía pyodbc
5. **Datos procesados** → pandas DataFrame convertido a JSON
6. **Respuesta al cliente** → JavaScript actualiza gráficos y tablas

## Consulta SQL Principal

La consulta principal convierte unidades de productos a kilogramos usando patrones de texto en nombres de productos:

```sql
SELECT
    YEAR(m.CFECHA) AS Anio,
    MONTH(m.CFECHA) AS Mes,
    SUM(CASE 
        WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
        WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
        -- ... más conversiones
        ELSE 0
    END) AS KilosTotales,
    -- Conversión a toneladas dividiendo por 1000
FROM admMovimientos m
JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
JOIN admDocumentosModelo dm ON m.CIDDOCUMENTODE = dm.CIDDOCUMENTODE
WHERE (m.CIDDOCUMENTODE = 4 OR m.CIDDOCUMENTODE = 3)
  AND dm.CMODULO = 1
  AND p.CCODIGOPRODUCTO IN (lista_productos_validos)
  -- Exclusiones de documentos tipo 5 y 6
GROUP BY YEAR(m.CFECHA), MONTH(m.CFECHA)
ORDER BY Anio, Mes
```

## Filtros Implementados

1. **Filtro por Fechas:**
   - Fecha de inicio (opcional)
   - Fecha de fin (opcional)

2. **Filtro por Productos:**
   - Lista desplegable múltiple
   - 137 productos predefinidos en configuración

3. **Exclusiones automáticas:**
   - Documentos tipo 5 (devoluciones)
   - Documentos tipo 6 (cancelaciones)

## Funcionalidades de Exportación

- **Formato Excel:** Usando openpyxl
- **Datos incluidos:** Año, Mes, Nombre del Mes, Kilos Totales, Toneladas Totales
- **Descarga directa** desde el navegador

## Tecnologías Utilizadas

**Backend:**
- Python 3.x
- Flask 3.1.1
- pyodbc 5.2.0
- pandas 2.3.1
- openpyxl 3.1.5

**Frontend:**
- HTML5/CSS3
- JavaScript ES6+
- Bootstrap 4.6.0
- Chart.js
- jQuery 3.6.0
- FontAwesome

**Base de Datos:**
- Microsoft SQL Server
- ODBC Driver 18

## Configuración de Despliegue

**Desarrollo:**
```bash
cd FlaskReporteApp
source venv/bin/activate
python app.py
```

**Producción recomendada:**
- Usar Gunicorn como WSGI server
- Nginx como reverse proxy
- Configurar variables de entorno para credenciales
- SSL/HTTPS obligatorio

## Seguridad

**Implementado:**
- Conexión SQL Server con TrustServerCertificate
- Sanitización de parámetros SQL via pandas
- Validación de tipos de datos
- Manejo de errores sin exposición de información sensible

**Recomendaciones adicionales:**
- Implementar autenticación de usuarios
- Rate limiting en APIs
- Logs de auditoría
- Encriptar credenciales en variables de entorno

## Mantenimiento

**Tareas periódicas:**
- Monitoreo de logs de errores
- Verificación de conexión a base de datos
- Actualización de lista de productos válidos
- Backup de configuraciones

**Escalabilidad:**
- Caché de consultas frecuentes (Redis)
- Paginación para datasets grandes
- Optimización de índices en SQL Server
- Load balancing para múltiples instancias