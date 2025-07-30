import pyodbc

def get_db_connection():
    server = "localhost,1433"  # Ej: "localhost,1433" o "IP,puerto"
    database = "adMOLIENDAS_Y_ALIMENTO"
    username = "SA"
    password = "Mar120305!"
    
    conn = pyodbc.connect(
        driver="FreeTDS",
        server=server,
        database=database,
        uid=username,
        pwd=password,
        TDS_Version="7.4"
    )
    return conn