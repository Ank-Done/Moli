import mariadb

def get_db_connection():
    try:
        return mariadb.connect(
            user="root",
            password="",
            host="localhost",
            port=3306,
            database="montamolienda"
        )
    except mariadb.Error as e:
        print(f"Error al conectar a MariaDB: {e}")
        return None
