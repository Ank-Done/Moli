"""
Aplicación Flask para Reportes de Ventas
Moliendas y Alimentos
"""

from flask import Flask
import os

def create_app():
    """Factory function para crear la aplicación Flask"""
    
    # Especificar rutas de templates y static
    app = Flask(__name__, 
                template_folder='app/templates',
                static_folder='app/static')
    
    # Configuración
    app.config['SECRET_KEY'] = 'clave-secreta-moliendas-alimentos'
    app.config['DEBUG'] = True
    
    # Registrar blueprints
    from app.views.routes import main
    app.register_blueprint(main)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)