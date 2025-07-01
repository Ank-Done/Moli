from flask import Flask, render_template

# Inicialización de la aplicación Flask
app = Flask(__name__)

# --- Definición de Rutas ---

@app.route('/')
def inicio():
    """ Ruta para la página de inicio """
    return render_template('index.html')

@app.route('/servicios')
def servicios():
    """ Ruta para la página de servicios """
    return render_template('servicios.html')

@app.route('/productos')
def productos():
    """ Ruta para la página de productos """
    # Lista de productos que se pasarán a la plantilla
    lista_productos = [
        {
            "nombre": "Azúcar con Canela",
            "descripcion": "Una mezcla perfecta de azúcar y canela molida, ideal para repostería y bebidas.",
            "imagen": "azucar-canela.jpg"
        },
        {
            "nombre": "Azúcar de Colores",
            "descripcion": "Azúcar granulada teñida con colores vibrantes para decoración de postres y dulces.",
            "imagen": "azucar-colores.jpg"
        },
        {
            "nombre": "Bajo en Calorías",
            "descripcion": "Mezclas especiales de endulzantes para reducir el aporte calórico sin sacrificar sabor.",
            "imagen": "bajo-en-calorias.jpg"
        },
        {
            "nombre": "Caramel Sugar",
            "descripcion": "Azúcar con un toque de caramelo, perfecta para dar un sabor y color único a tus creaciones.",
            "imagen": "caramel-sugar.jpg"
        },
        {
            "nombre": "Coberturas",
            "descripcion": "Variedad de coberturas en polvo para decorar y dar el toque final a productos de panadería.",
            "imagen": "coberturas.jpg"
        },
        {
            "nombre": "Icing Sugar (Azúcar Glass)",
            "descripcion": "Azúcar pulverizada de alta finura, ideal para glaseados, frostings y betunes.",
            "imagen": "icing-sugar.jpg"
        },
        {
            "nombre": "Azúcar Mascabado",
            "descripcion": "Azúcar de caña no refinada, con un sabor robusto a melaza, ideal para repostería rústica.",
            "imagen": "mascabado.jpg"
        },
        {
            "nombre": "Sucralosa",
            "descripcion": "Endulzante de alta intensidad sin calorías, perfecto para una amplia gama de aplicaciones.",
            "imagen": "sucralosa.jpg"
        }
    ]
    return render_template('productos.html', productos=lista_productos)

@app.route('/contacto')
def contacto():
    """ Ruta para la página de contacto """
    return render_template('contacto.html')

# --- Iniciar la aplicación ---

if __name__ == '__main__':
    # El modo debug se actualiza automáticamente con los cambios
    app.run(debug=True, host='0.0.0.0', port=5000)