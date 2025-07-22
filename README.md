# Sistema de Reportes de Ventas - Moliendas y Alimentos

Sistema web para generar reportes de ventas basados en datos de Microsoft SQL Server, con funcionalidades de filtrado, visualización y exportación.

## Características

- ✅ Dashboard con estadísticas generales
- ✅ Reportes con filtros por fecha y productos
- ✅ Visualización de datos con gráficos interactivos
- ✅ Exportación a Excel
- ✅ Interfaz responsive basada en Bootstrap
- ✅ Conexión directa a SQL Server
- ✅ 137 productos predefinidos para filtrado

## Requisitos del Sistema

- Python 3.8+
- Microsoft SQL Server con base de datos `adMOLIENDAS_Y_ALIMENTO`
- ODBC Driver 18 for SQL Server
- Sistema operativo: Linux (desarrollado en Arch Linux)

## Instalación

### 1. Clonar o descargar el proyecto
```bash
cd /home/ank/Documents/FlaskReporteApp
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias
```bash
pip install flask pyodbc pandas openpyxl
```

### 4. Configurar base de datos
Editar `config/database.py` si es necesario:
```python
server = 'localhost'
database = 'adMOLIENDAS_Y_ALIMENTO'
username = 'SA'
password = 'Tu_Password_Aqui'
```

### 5. Probar conexión
```bash
python test_connection.py
```

### 6. Ejecutar aplicación
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## Uso del Sistema

### Dashboard Principal
- Acceso desde: `http://localhost:5000/`
- Muestra estadísticas generales de ventas
- Gráfico de evolución de ventas (últimos 12 meses)
- Información del sistema y productos disponibles

### Reportes Detallados
- Acceso desde: `http://localhost:5000/reporte`
- **Filtros disponibles:**
  - Fecha de inicio y fin
  - Selección múltiple de productos
- **Visualización:**
  - Gráfico de barras por periodo
  - Tabla detallada con datos
  - Estadísticas del periodo filtrado
- **Exportación:**
  - Botón "Excel" descarga archivo .xlsx

## Estructura de Datos

### Consulta Principal
El sistema calcula kilogramos totales basándose en patrones en nombres de productos:
- Productos "1 KG" → unidades × 1
- Productos "25 KG" → unidades × 25  
- Productos "50 KG" → unidades × 50
- etc.

### Filtros Automáticos
- Solo documentos tipo 3 (Remisiones) y 4 (específico)
- Excluye productos con movimientos tipo 5 y 6
- Solo módulo 1 del sistema

## API Endpoints

### GET `/api/reporte-datos`
Obtiene datos de ventas con filtros.

**Parámetros:**
- `fecha_inicio` (opcional): formato YYYY-MM-DD
- `fecha_fin` (opcional): formato YYYY-MM-DD  
- `productos[]` (opcional): array de códigos de productos

**Respuesta:**
```json
{
  "success": true,
  "datos": [...],
  "estadisticas": {...},
  "chart_data": {...}
}
```

### GET `/api/exportar-excel`
Descarga reporte en formato Excel con los mismos filtros.

## Productos Configurados

El sistema incluye 137 productos predefinidos, incluyendo:
- MESCO25, MESCO30 (Mezclas especiales)
- PBSMZ04-22 (Productos base maíz)  
- PCAGF02-04 (Productos concentrado gallina)
- PREP107-622 (Productos preparados)
- Y muchos más...

Lista completa en `config/database.py` → `PRODUCTOS_VALIDOS`

## Solución de Problemas

### Error de conexión a base de datos
```bash
# Verificar driver ODBC
odbcinst -q -d

# Probar conexión
python test_connection.py
```

### Puerto ocupado
```bash
# Cambiar puerto en app.py línea final:
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Módulos no encontrados
```bash
# Asegurar que el entorno virtual está activo
source venv/bin/activate
pip list  # verificar dependencias
```

## Desarrollo

### Agregar nuevos productos
1. Editar `config/database.py`
2. Agregar códigos a lista `PRODUCTOS_VALIDOS`
3. Reiniciar aplicación

### Modificar consulta SQL
1. Editar método `get_ventas_por_periodo()` en `app/models/reportes.py`
2. Probar con `test_connection.py`

### Personalizar interfaz
- CSS: `app/static/css/`
- JavaScript: Directamente en templates
- Templates: `app/templates/`

## Despliegue en Producción

### Con Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Con Nginx (reverso proxy)
```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Arquitectura

Ver documento detallado en `ARQUITECTURA.md`

## Soporte

Para problemas técnicos:
1. Verificar logs en consola Flask
2. Probar conexión con `test_connection.py`  
3. Revisar configuración en `config/database.py`

---

**Desarrollado para Moliendas y Alimentos** - Sistema de Reportes de Ventas v1.0