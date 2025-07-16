from fastapi import FastAPI, Depends, HTTPException
from database import get_db_connection

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with SQL Server!"}

@app.get("/movimientos-con-total")
def get_movimientos_con_total():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                m.CIDMOVIMIENTO, 
                p.CIDPRODUCTO, 
                p.cnombreproducto, 
                m.CUNIDADES, 
                m.CPRECIO, 
                (m.CUNIDADES * m.CPRECIO) AS CTOTAL,
                m.CFECHA
            FROM 
                admMovimientos m
            JOIN 
                admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
        """)
        
        # Convertir a lista de diccionarios
        movimientos = []
        columns = [column[0] for column in cursor.description]
        
        for row in cursor.fetchall():
            movimientos.append(dict(zip(columns, row)))
        
        return {"movimientos": movimientos}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()