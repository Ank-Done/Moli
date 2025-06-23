import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

@app.route('/productos')
def productos():
    # Se agrega una 'categoria' a cada producto para el sistema de filtros
    lista_productos = [
        {
            "nombre": "Azúcar con Canela",
            "descripcion": "Mezcla perfecta de azúcar y canela, ideal para repostería y bebidas.",
            "imagen": "azucar-canela.jpg",
            "categoria": "mezclas"
        },
        {
            "nombre": "Azúcar de Colores",
            "descripcion": "Azúcar granulada teñida para decoración de postres y dulces.",
            "imagen": "azucar-colores.jpg",
            "categoria": "decoracion"
        },
        {
            "nombre": "Bajo en Calorías",
            "descripcion": "Mezclas de endulzantes para reducir calorías sin sacrificar sabor.",
            "imagen": "bajo-en-calorias.jpg",
            "categoria": "endulzantes"
        },
        {
            "nombre": "Caramel Sugar",
            "descripcion": "Azúcar con un toque de caramelo para un sabor y color único.",
            "imagen": "caramel-sugar.jpg",
            "categoria": "mezclas"
        },
        {
            "nombre": "Coberturas",
            "descripcion": "Variedad de coberturas en polvo para decorar productos de panadería.",
            "imagen": "coberturas.jpg",
            "categoria": "decoracion"
        },
        {
            "nombre": "Icing Sugar (Azúcar Glass)",
            "descripcion": "Azúcar pulverizada de alta finura, ideal para glaseados y frostings.",
            "imagen": "icing-sugar.jpg",
            "categoria": "endulzantes"
        },
        {
            "nombre": "Azúcar Mascabado",
            "descripcion": "Azúcar de caña no refinada con un robusto sabor a melaza.",
            "imagen": "mascabado.jpg",
            "categoria": "endulzantes"
        },
        {
            "nombre": "Sucralosa",
            "descripcion": "Endulzante de alta intensidad sin calorías para múltiples aplicaciones.",
            "imagen": "sucralosa.jpg",
            "categoria": "endulzantes"
        }
    ]
    return render_template('productos.html', productos=lista_productos)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)