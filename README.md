# Sistema Cyberia FastAPI

## Descripción

Sistema de Inteligencia Empresarial moderno para Moliendas y Alimentos, desarrollado con FastAPI. Proporciona gestión completa de productos de azúcar, edulcorantes, servicios logísticos, ventas y análisis de rentabilidad.

### Características Principales

- **Dashboard Ejecutivo**: Métricas en tiempo real con formato de moneda en millones
- **Gestión de Productos**: CRUD completo con búsqueda avanzada y sugerencias
- **Sistema de Ventas**: Gestión de documentos de venta con detalles
- **Precios Dinámicos**: Sistema de precios con historial y análisis de mercado
- **Analytics Avanzados**: Comparativas mensuales, rentabilidad diaria, análisis por kg
- **Interfaz Moderna**: UI responsiva con JavaScript vanilla y Bootstrap 5

## Tecnologías

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5, Chart.js
- **Base de Datos**: SQL Server con stored procedures
- **Validación**: Pydantic schemas
- **Templates**: Jinja2

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- SQL Server con la base de datos Cyberia configurada
- ODBC Driver para SQL Server

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd /home/ank/Documents/REporte/fastapi_cyberia
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   - Editar `config/database.py` con los datos de conexión
   - Asegurar que el servidor SQL Server esté ejecutándose
   - Verificar que las tablas y stored procedures estén creados

5. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

   O usando uvicorn directamente:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Uso

### Acceso a la Aplicación

- **URL Principal**: http://localhost:8000
- **Dashboard**: http://localhost:8000/dashboard
- **Productos**: http://localhost:8000/products
- **Ventas**: http://localhost:8000/sales
- **Precios**: http://localhost:8000/pricing
- **Analytics**: http://localhost:8000/analytics

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### Productos
- `GET /api/products` - Lista de productos con filtros
- `POST /api/products` - Crear nuevo producto
- `PUT /api/products/{id}` - Actualizar producto
- `DELETE /api/products/{id}` - Eliminar producto (soft delete)
- `GET /api/products/search` - Búsqueda avanzada
- `GET /api/products/suggestions` - Sugerencias para autocompletado

#### Ventas
- `GET /api/sales/documents` - Lista de documentos de venta
- `POST /api/sales/documents` - Crear documento de venta
- `GET /api/sales/documents/{id}` - Obtener documento específico
- `POST /api/sales/documents/{id}/details` - Agregar producto al documento

#### Precios
- `GET /api/pricing/current` - Precios actuales
- `PUT /api/pricing/{product_id}` - Actualizar precio
- `GET /api/pricing/{product_id}/history` - Historial de precios
- `GET /api/pricing/market-analysis` - Análisis de mercado

#### Analytics
- `GET /api/analytics/dashboard-metrics` - Métricas del dashboard
- `GET /api/analytics/monthly-comparison` - Comparativa mensual
- `GET /api/analytics/daily-profitability` - Rentabilidad diaria
- `GET /api/analytics/profit-per-kg` - Análisis de ganancia por kg

## Estructura del Proyecto

```
fastapi_cyberia/
├── main.py                 # Aplicación principal FastAPI
├── requirements.txt        # Dependencias Python
├── README.md              # Este archivo
├── config/
│   └── database.py        # Configuración de base de datos
├── models/                # Servicios de negocio
│   ├── products.py        # Servicio de productos
│   ├── sales.py          # Servicio de ventas
│   ├── users.py          # Servicio de usuarios
│   ├── pricing.py        # Servicio de precios
│   └── analytics.py      # Servicio de analytics
├── schemas/              # Esquemas Pydantic
│   ├── products.py       # Schemas de productos
│   ├── sales.py         # Schemas de ventas
│   ├── users.py         # Schemas de usuarios
│   ├── pricing.py       # Schemas de precios
│   └── analytics.py     # Schemas de analytics
├── templates/           # Templates HTML
│   ├── base.html        # Template base
│   ├── dashboard.html   # Dashboard ejecutivo
│   └── products.html    # Gestión de productos
└── static/             # Archivos estáticos
    ├── css/
    │   └── custom.css   # Estilos personalizados
    └── js/             # JavaScript personalizado
```

## Características Especiales

### Dashboard Ejecutivo
- **Formato de Moneda**: Automáticamente convierte grandes cantidades a formato de millones (ej: "2.5M", "150K")
- **Comparativas**: Muestra cambios porcentuales vs mes anterior
- **Ordenamiento Calendar**: Los datos mensuales se ordenan correctamente por calendario
- **Mes Actual**: El mes de julio muestra 0 como se requirió

### Sistema de Productos
- **Búsqueda Inteligente**: Autocompletado con sugerencias en tiempo real
- **Filtros Avanzados**: Por industria, categoría, rango de precios
- **Gestión Completa**: CRUD con validación de datos
- **Categorías Jerárquicas**: Soporte para categorías anidadas

### Sistema de Precios
- **Precios Dinámicos**: Histórico completo de cambios de precios
- **Análisis de Mercado**: Comparativas y volatilidad de precios
- **Sugerencias**: Cálculo automático de precios basado en márgenes objetivo
- **Actualización Masiva**: Soporte para actualización de múltiples precios

### Analytics Avanzados
- **Métricas en Tiempo Real**: Dashboard que se actualiza automáticamente
- **Comparativas Mensuales**: Análisis periodo a periodo
- **Rentabilidad por kg**: Análisis específico para productos de azúcar
- **Visualizaciones**: Gráficos interactivos con Chart.js

## Configuración de Base de Datos

La aplicación requiere que la base de datos tenga las siguientes tablas principales:

- `Products` - Catálogo de productos
- `ProductCategories` - Categorías de productos
- `ProductTypes` - Tipos de productos
- `SugarProductAttributes` - Atributos específicos de azúcar
- `LogisticsServiceAttributes` - Atributos de servicios logísticos
- `DynamicPricing` - Historial de precios
- `SalesDocuments` - Documentos de venta
- `SalesDocumentDetails` - Detalles de ventas
- `Users` - Usuarios/Agentes
- `Customers` - Clientes

## Health Check

La aplicación incluye un endpoint de health check:
- `GET /health` - Verifica estado de la aplicación y conexión a base de datos

## Logging

La aplicación incluye logging detallado para:
- Operaciones de base de datos
- Errores de API
- Eventos de startup/shutdown

## Desarrollo

Para desarrollo local:

1. Usar el flag `--reload` con uvicorn para recarga automática
2. Los templates se recargan automáticamente
3. Los archivos estáticos se sirven desde `/static`

## Soporte

Para soporte técnico o consultas sobre el sistema, contactar al equipo de desarrollo del proyecto Cyberia.