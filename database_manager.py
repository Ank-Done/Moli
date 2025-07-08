#!/usr/bin/env python3
import mysql.connector
import random
from datetime import datetime, timedelta
import json

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mar120305',
    'database': 'reporteventasenejul',
    'port': 3306
}

def get_db_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def analyze_database_structure():
    """Analyze current database structure"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        structure = {}
        for table in tables:
            table_name = list(table.values())[0]
            print(f"Analyzing table: {table_name}")
            
            # Get table structure
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            
            # Get sample data
            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5")
            sample_data = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
            row_count = cursor.fetchone()['count']
            
            structure[table_name] = {
                'columns': columns,
                'sample_data': sample_data,
                'row_count': row_count
            }
            
        return structure
        
    except Exception as e:
        print(f"Error analyzing database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def create_additional_tables():
    """Create additional tables for enhanced functionality"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INT AUTO_INCREMENT PRIMARY KEY,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(200) NOT NULL,
                categoria VARCHAR(100),
                precio_unitario DECIMAL(10,2),
                costo_unitario DECIMAL(10,2),
                unidad_medida VARCHAR(20),
                descripcion TEXT,
                estado ENUM('activo', 'inactivo') DEFAULT 'activo',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create clients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INT AUTO_INCREMENT PRIMARY KEY,
                codigo_cliente VARCHAR(50) UNIQUE NOT NULL,
                razon_social VARCHAR(200) NOT NULL,
                rfc VARCHAR(20),
                email VARCHAR(100),
                telefono VARCHAR(20),
                direccion TEXT,
                ciudad VARCHAR(100),
                estado VARCHAR(100),
                codigo_postal VARCHAR(10),
                limite_credito DECIMAL(15,2) DEFAULT 0,
                dias_credito INT DEFAULT 30,
                estado_cliente ENUM('activo', 'inactivo', 'suspendido') DEFAULT 'activo',
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agentes (
                id_agente INT AUTO_INCREMENT PRIMARY KEY,
                codigo_agente VARCHAR(50) UNIQUE NOT NULL,
                nombre_completo VARCHAR(200) NOT NULL,
                email VARCHAR(100),
                telefono VARCHAR(20),
                comision_porcentaje DECIMAL(5,2) DEFAULT 5.00,
                meta_mensual DECIMAL(15,2) DEFAULT 0,
                zona_asignada VARCHAR(100),
                estado_agente ENUM('activo', 'inactivo') DEFAULT 'activo',
                fecha_ingreso DATE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create enhanced sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas_detalladas (
                id_venta INT AUTO_INCREMENT PRIMARY KEY,
                folio VARCHAR(50) NOT NULL,
                fecha_venta DATE NOT NULL,
                id_cliente INT,
                id_agente INT,
                id_producto INT,
                cantidad DECIMAL(10,2) NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                descuento_porcentaje DECIMAL(5,2) DEFAULT 0,
                impuesto_porcentaje DECIMAL(5,2) DEFAULT 16,
                subtotal DECIMAL(15,2) NOT NULL,
                descuento DECIMAL(15,2) DEFAULT 0,
                impuestos DECIMAL(15,2) NOT NULL,
                total DECIMAL(15,2) NOT NULL,
                tipo_venta ENUM('contado', 'credito') DEFAULT 'contado',
                estado_venta ENUM('pendiente', 'pagada', 'cancelada') DEFAULT 'pendiente',
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_agente) REFERENCES agentes(id_agente),
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            )
        """)
        
        # Create inventory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id_inventario INT AUTO_INCREMENT PRIMARY KEY,
                id_producto INT NOT NULL,
                almacen VARCHAR(100) DEFAULT 'Principal',
                stock_actual INT DEFAULT 0,
                stock_minimo INT DEFAULT 10,
                stock_maximo INT DEFAULT 1000,
                costo_promedio DECIMAL(10,2) DEFAULT 0,
                ultima_entrada DATE,
                ultima_salida DATE,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            )
        """)
        
        # Create saved graphs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS graficos_guardados (
                id_grafico INT AUTO_INCREMENT PRIMARY KEY,
                nombre_grafico VARCHAR(200) NOT NULL,
                tipo_grafico ENUM('bar', 'line', 'pie', 'scatter', 'area') NOT NULL,
                configuracion JSON NOT NULL,
                datos JSON NOT NULL,
                descripcion TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Additional tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def generate_dummy_data():
    """Generate and insert 1000+ dummy records"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        print("🔄 Generating dummy data...")
        
        # Sample data arrays
        productos_data = [
            ("AZ-EST-25", "Azúcar Estándar 25kg", "Azúcares", 450.00, 380.00, "kg"),
            ("AZ-REF-25", "Azúcar Refinada 25kg", "Azúcares", 480.00, 400.00, "kg"),
            ("END-SUC-1", "Endulzante Sucralosa 1kg", "Endulzantes", 850.00, 720.00, "kg"),
            ("CAF-SOL-500", "Café Soluble 500g", "Bebidas", 180.00, 150.00, "g"),
            ("HAR-TRI-25", "Harina de Trigo 25kg", "Harinas", 320.00, 280.00, "kg"),
            ("ACE-VEG-1L", "Aceite Vegetal 1L", "Aceites", 65.00, 55.00, "L"),
            ("SAL-REF-1", "Sal Refinada 1kg", "Condimentos", 25.00, 20.00, "kg"),
            ("ARR-BLA-25", "Arroz Blanco 25kg", "Cereales", 380.00, 320.00, "kg"),
            ("FRI-NEG-25", "Frijol Negro 25kg", "Legumbres", 420.00, 350.00, "kg"),
            ("MAI-AMA-25", "Maíz Amarillo 25kg", "Cereales", 290.00, 250.00, "kg")
        ]
        
        clientes_data = [
            ("CLI001", "COMERCIALIZADORA DIMAFE SA DE CV", "CDI980515ABC", "comercial@dimafe.com", "8181234567"),
            ("CLI002", "PRODUCTOS AGRICOLAS CHIHUAHUA", "PAC850320DEF", "ventas@pachih.com", "6141234567"),
            ("CLI003", "PANADERIA Y PASTELERIA REGIONAL", "PPR969803857", "admin@panreg.com", "5551234567"),
            ("CLI004", "COMERCIAL TREVIÑO SA", "CTR911104FBA", "contacto@ctrevino.com", "8121234567"),
            ("CLI005", "ALIMENTOS NATURALES SABROZA", "ANS590082849", "pedidos@sabroza.com", "5521234567"),
            ("CLI006", "DISTRIBUIDORA NORTE MAYORISTA", "DNM780912345", "mayoreo@dnorte.com", "8441234567"),
            ("CLI007", "SUPERMERCADOS LA ECONOMIA", "SLE920506789", "compras@economia.com", "3331234567"),
            ("CLI008", "RESTAURANTES GOURMET UNIDOS", "RGU030815432", "abasto@gourmet.com", "5541234567"),
            ("CLI009", "HOTELES Y BANQUETES PREMIER", "HBP010920567", "cocina@premier.com", "8181234568"),
            ("CLI010", "CADENA DE TIENDAS FAMILIAR", "CTF940712890", "adquisiciones@familiar.com", "6641234567")
        ]
        
        agentes_data = [
            ("AG001", "María Elena Rodríguez García", "maria.rodriguez@empresa.com", "5551234567", 8.5, 150000.00, "Norte"),
            ("AG002", "José Antonio Hernández López", "jose.hernandez@empresa.com", "8181234567", 7.0, 120000.00, "Noreste"),
            ("AG003", "Ana Patricia Martínez Silva", "ana.martinez@empresa.com", "3331234567", 9.0, 180000.00, "Occidente"),
            ("AG004", "Carlos Eduardo Ramírez Torres", "carlos.ramirez@empresa.com", "8121234567", 6.5, 100000.00, "Centro"),
            ("AG005", "Laura Beatriz Morales Cruz", "laura.morales@empresa.com", "5521234567", 8.0, 140000.00, "Centro Sur"),
            ("AG006", "Roberto Alejandro Vega Sánchez", "roberto.vega@empresa.com", "6641234567", 7.5, 130000.00, "Noroeste"),
            ("AG007", "Daniela Isabel Flores Mendoza", "daniela.flores@empresa.com", "8441234567", 8.5, 160000.00, "Bajío"),
            ("AG008", "Miguel Ángel Jiménez Ruiz", "miguel.jimenez@empresa.com", "4771234567", "7.0", 110000.00, "Centro Norte")
        ]
        
        # Insert products
        print("📦 Inserting products...")
        for i, (codigo, nombre, categoria, precio, costo, unidad) in enumerate(productos_data):
            for variant in range(10):  # Create 10 variants of each product
                new_codigo = f"{codigo}-{variant+1:02d}"
                new_nombre = f"{nombre} - Variante {variant+1}"
                price_variation = random.uniform(0.9, 1.1)
                cursor.execute("""
                    INSERT INTO productos (codigo, nombre, categoria, precio_unitario, costo_unitario, unidad_medida, descripcion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (new_codigo, new_nombre, categoria, precio * price_variation, costo * price_variation, unidad, f"Descripción detallada del producto {new_nombre}"))
        
        # Insert clients
        print("👥 Inserting clients...")
        for i, (codigo, razon, rfc, email, telefono) in enumerate(clientes_data):
            for variant in range(15):  # Create 15 variants of each client
                new_codigo = f"{codigo}-{variant+1:02d}"
                new_razon = f"{razon} - Sucursal {variant+1}"
                new_rfc = f"{rfc}{variant+1:02d}"
                new_email = f"sucursal{variant+1}.{email}"
                cursor.execute("""
                    INSERT INTO clientes (codigo_cliente, razon_social, rfc, email, telefono, direccion, ciudad, estado, limite_credito, dias_credito)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_codigo, new_razon, new_rfc, new_email, telefono, f"Dirección {variant+1}", f"Ciudad {variant+1}", f"Estado {variant+1}", random.uniform(50000, 500000), random.choice([15, 30, 45, 60])))
        
        # Insert agents
        print("🤝 Inserting agents...")
        for codigo, nombre, email, telefono, comision, meta, zona in agentes_data:
            cursor.execute("""
                INSERT INTO agentes (codigo_agente, nombre_completo, email, telefono, comision_porcentaje, meta_mensual, zona_asignada, fecha_ingreso)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (codigo, nombre, email, telefono, comision, meta, zona, datetime.now().date() - timedelta(days=random.randint(30, 1000))))
        
        # Get inserted IDs for foreign keys
        cursor.execute("SELECT id_producto FROM productos")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id_cliente FROM clientes")
        client_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id_agente FROM agentes")
        agent_ids = [row[0] for row in cursor.fetchall()]
        
        # Insert inventory
        print("📊 Inserting inventory...")
        for product_id in product_ids:
            cursor.execute("""
                INSERT INTO inventario (id_producto, almacen, stock_actual, stock_minimo, stock_maximo, costo_promedio, ultima_entrada)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (product_id, random.choice(['Principal', 'Sucursal Norte', 'Sucursal Sur', 'Bodega Central']), 
                 random.randint(50, 500), random.randint(10, 50), random.randint(500, 1000), 
                 random.uniform(100, 800), datetime.now().date() - timedelta(days=random.randint(1, 30))))
        
        # Insert detailed sales (1000+ records)
        print("💰 Inserting sales records...")
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(1200):  # Generate 1200 sales records
            sale_date = start_date + timedelta(days=random.randint(0, 365))
            product_id = random.choice(product_ids)
            client_id = random.choice(client_ids)
            agent_id = random.choice(agent_ids)
            quantity = random.uniform(1, 50)
            unit_price = random.uniform(50, 800)
            discount_pct = random.choice([0, 5, 10, 15, 20])
            tax_pct = 16
            
            subtotal = quantity * unit_price
            discount = subtotal * (discount_pct / 100)
            taxes = (subtotal - discount) * (tax_pct / 100)
            total = subtotal - discount + taxes
            
            cursor.execute("""
                INSERT INTO ventas_detalladas 
                (folio, fecha_venta, id_cliente, id_agente, id_producto, cantidad, precio_unitario, 
                 descuento_porcentaje, impuesto_porcentaje, subtotal, descuento, impuestos, total, 
                 tipo_venta, estado_venta, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (f"FAC-{i+1000:06d}", sale_date.date(), client_id, agent_id, product_id, quantity, unit_price,
                 discount_pct, tax_pct, subtotal, discount, taxes, total,
                 random.choice(['contado', 'credito']), random.choice(['pendiente', 'pagada', 'cancelada']),
                 f"Observaciones para venta {i+1}"))
        
        conn.commit()
        print("✅ Dummy data inserted successfully!")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM productos")
        print(f"📦 Products: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM clientes")
        print(f"👥 Clients: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM agentes")
        print(f"🤝 Agents: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM ventas_detalladas")
        print(f"💰 Sales: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM inventario")
        print(f"📊 Inventory items: {cursor.fetchone()[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating dummy data: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting database enhancement...")
    
    # Analyze current structure
    structure = analyze_database_structure()
    if structure:
        print("📊 Current database structure analyzed")
        for table_name, info in structure.items():
            print(f"  • {table_name}: {info['row_count']} rows")
    
    # Create additional tables
    if create_additional_tables():
        print("✅ Additional tables created")
    
    # Generate dummy data
    if generate_dummy_data():
        print("✅ Database enhancement completed!")
    else:
        print("❌ Failed to generate dummy data")