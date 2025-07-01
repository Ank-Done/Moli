import os
from flask import Flask, render_template
from database import get_db_connection

app = Flask(__name__)

@app.route('/')
def mostrar_usuarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM usuarios')
        usuarios = cursor.fetchall()
        
        if not usuarios:
            usuarios = [{"mensaje": "No hay usuarios registrados"}]
            
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        usuarios = [{"error": f"Error de base de datos: {str(e)}"}]
        
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
    
    return render_template('index.htm', usuarios=usuarios)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)