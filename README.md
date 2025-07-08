# 🚀 Cyberia Business Intelligence Dashboard

## Descripción

Sistema integral de gestión y análisis empresarial que combina múltiples bases de datos en una interfaz moderna y potente. Desarrollado con Flask, este dashboard proporciona análisis en tiempo real, generación de reportes y gestión completa de datos empresariales.

## 🌟 Características Principales

### 📊 Dashboard Ejecutivo
- Métricas en tiempo real de clientes, productos, ventas e inventario
- Gráficos interactivos con Plotly
- Visualización de tendencias de ventas mensuales
- KPIs empresariales centralizados

### 💼 Análisis de Ventas
- Filtros avanzados por año, mes, agente, cliente y producto
- Exportación a PDF y Excel con formato profesional
- Búsqueda inteligente en base de datos de ventas
- Cálculos automáticos de totales y estadísticas

### 📦 Gestión de Productos
- Catálogo completo de productos con familias y clasificaciones
- Control de unidades de medida y especificaciones
- Integración con sistema de inventario
- Formularios de gestión con validación

### 👥 Administración de Clientes
- Base de datos unificada de clientes
- Gestión de límites de crédito y condiciones comerciales
- Estados de cuenta y análisis crediticio
- Información de contacto y direcciones

### 📋 Control de Inventario
- Monitoreo en tiempo real de existencias por almacén
- Alertas de stock bajo automatizadas
- Valorización de inventario por costos
- Reportes de movimientos de inventario

### 📈 Centro de Reportes
- Generación de reportes personalizados
- Múltiples formatos de exportación (PDF, Excel)
- Reportes programados por período
- Análisis comparativo y tendencias

### ⚙️ Gestión del Sistema
- Monitoreo del estado de bases de datos
- Estadísticas del sistema en tiempo real
- Herramientas de respaldo y mantenimiento
- Panel de administración centralizado

## 🗄️ Bases de Datos Soportadas

### 1. normalzone (MySQL)
- **Productos**: Catálogo completo con familias y clasificaciones
- **Clientes**: Representantes, límites de crédito, direcciones
- **Inventario**: Existencias, almacenes, movimientos
- **Documentos**: Facturas, órdenes, comprobantes
- **Configuración**: Monedas, países, tipos de documento

### 2. reporteventasenejul (MySQL)
- **Ventas**: Datos históricos de ventas por período
- **Agentes**: Información de representantes de ventas
- **Análisis**: Métricas de rendimiento y comisiones

### 3. moliendascyberia (MariaDB)
- **Usuarios**: Sistema de usuarios especializado
- **Operaciones**: Datos específicos de moliendas

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask 2.3.3**: Framework web Python
- **MySQL Connector**: Conexión a bases de datos MySQL
- **MariaDB Connector**: Soporte para bases de datos MariaDB
- **Pandas**: Análisis y manipulación de datos
- **ReportLab**: Generación de PDFs profesionales

### Frontend
- **HTML5/CSS3**: Estructura y estilos modernos
- **JavaScript Vanilla**: Interactividad sin dependencias
- **Plotly.js**: Gráficos interactivos y visualizaciones
- **Font Awesome**: Iconografía profesional
- **CSS Grid/Flexbox**: Layout responsivo moderno

### Exportación
- **ReportLab**: PDFs con formato corporativo
- **OpenPyXL**: Archivos Excel con estilos
- **Plotly**: Gráficos exportables

## 🚀 Instalación y Uso

### Requisitos Previos
- Python 3.8+
- MySQL/MariaDB en ejecución
- Bases de datos configuradas

### Instalación Rápida

```bash
# Navegar al directorio del proyecto
cd /home/ank/Documents/REporte

# Ejecutar script de inicio (recomendado)
./run_cyberia.sh
```

### Instalación Manual

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python enhanced_app.py
```

### Acceso a la Aplicación

Después de ejecutar, la aplicación estará disponible en:
- **URL Principal**: http://localhost:5003
- **API REST**: http://localhost:5003/api/

## 📱 Interfaz de Usuario

### Navegación Principal
- **Dashboard**: Vista general con métricas clave
- **Ventas**: Análisis detallado de transacciones
- **Productos**: Gestión del catálogo
- **Clientes**: Administración de la cartera
- **Inventario**: Control de existencias
- **Reportes**: Centro de generación de informes
- **Gestión**: Herramientas administrativas

### Características de UX
- **Diseño Responsivo**: Adaptable a cualquier dispositivo
- **Navegación Intuitiva**: Tabs con iconografía clara
- **Filtros Avanzados**: Búsqueda inteligente en tiempo real
- **Feedback Visual**: Indicadores de carga y estados
- **Modo Oscuro**: Interfaz profesional con gradientes
- **Animaciones Suaves**: Transiciones CSS optimizadas

## 🔧 Configuración

### Bases de Datos
Edita las configuraciones en `enhanced_app.py`:

```python
DB_CONFIGS = {
    'normalzone': {
        'host': 'localhost',
        'user': 'root',
        'password': 'tu_password',
        'database': 'normalzone',
        'port': 3306
    },
    # ... otras configuraciones
}
```

### Puerto de Aplicación
Por defecto ejecuta en puerto **5003**. Para cambiar:

```python
app.run(debug=True, host='0.0.0.0', port=TU_PUERTO)
```

## 📊 API Endpoints

### Dashboard
- `GET /api/dashboard` - Métricas principales

### Ventas
- `GET /api/sales` - Datos de ventas con filtros
- `POST /api/export-pdf` - Exportar ventas a PDF
- `POST /api/export-excel` - Exportar ventas a Excel

### Gestión de Datos
- `GET /api/products` - Lista de productos
- `GET /api/clients` - Lista de clientes
- `GET /api/inventory` - Estado del inventario

### Sistema
- `GET /api/system/db-status` - Estado de bases de datos
- `GET /api/system/stats` - Estadísticas del sistema
- `GET /api/reports/sales` - Reportes de ventas

## 🎨 Personalización

### Colores Corporativos
El tema utiliza una paleta moderna:
- **Primario**: #667eea (Azul)
- **Secundario**: #764ba2 (Púrpura)
- **Éxito**: #38ef7d (Verde)
- **Advertencia**: #ffd89b (Amarillo)

### Agregando Nuevas Funciones
1. Crear endpoint en Flask
2. Agregar función JavaScript correspondiente
3. Incluir en navegación si es necesario
4. Actualizar documentación

## 🔒 Seguridad

- Validación de entrada en todos los formularios
- Conexiones de base de datos con manejo de errores
- Protección contra inyección SQL con parámetros
- Gestión de sesiones Flask

## 📈 Optimización

- Consultas limitadas para mejorar performance
- Carga asíncrona de datos con JavaScript
- Compresión de respuestas Flask-CORS
- Caché de consultas frecuentes

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos
1. Verificar que MySQL/MariaDB esté ejecutándose
2. Comprobar credenciales en configuración
3. Validar nombres de bases de datos
4. Revisar permisos de usuario

### Dependencias Faltantes
```bash
pip install -r requirements.txt --upgrade
```

### Puerto en Uso
Cambiar puerto en `enhanced_app.py` o terminar proceso:
```bash
sudo lsof -i :5003
sudo kill -9 [PID]
```

## 🤝 Contribución

Para contribuir al proyecto:
1. Fork del repositorio
2. Crear rama feature
3. Implementar mejoras
4. Crear pull request

## 📞 Soporte

Para soporte técnico o consultas:
- Revisar logs de la aplicación
- Verificar configuración de bases de datos
- Consultar documentación de APIs

## 🚀 Comando de Ejecución

```bash
./run_cyberia.sh
```

**¡La aplicación estará disponible en http://localhost:5003!**

---

*Desarrollado con ❤️ para gestión empresarial moderna*