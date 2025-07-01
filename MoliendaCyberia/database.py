import mariadb
import sys
from flask import current_app

def get_db_connection():
    """Establece conexión específica para MariaDB"""
    try:
        conn = mariadb.connect(
            user="root",      # Usuario de MariaDB
            password="", # Contraseña
            host="localhost",
            port=3306,              # Puerto por defecto
            database="moliendascyberia"
        )
        print("¡Conexión exitosa a MariaDB!")
        return conn
        
    except mariadb.Error as e:
        print(f"Error al conectar a MariaDB: {e}")
        sys.exit(1)