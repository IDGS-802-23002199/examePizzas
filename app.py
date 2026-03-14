from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import CSRFProtect
from datetime import datetime

from config import Config
from models import db, Cliente, Pizza, Pedido, DetallePedido
from forms import PizzaForm, ClienteForm
import calendar
from sqlalchemy import extract

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)
db.init_app(app)

with app.app_context():
    db.create_all()


PRECIOS_PIZZA = {
    "chica": 40,
    "mediana": 80,
    "grande": 120
}
PRECIO_INGREDIENTE = 10


@app.route("/")
def index():

    pizzaForm = PizzaForm()
    clienteForm = ClienteForm()
    if "carrito" not in session:
        session["carrito"] = []
    carrito = session["carrito"]
    total = sum(item["subtotal"] for item in carrito)
    return render_template(
        "index.html",
        carrito=carrito,
        total=total,
        pizzaForm=pizzaForm,
        clienteForm=clienteForm
    )


@app.route("/agregar", methods=["POST"])
def agregar():

    tamano = request.form["tamano"]
    ingredientes_lista = request.form.getlist("ingredientes")
    cantidad = int(request.form["cantidad"])
    precio_base = PRECIOS_PIZZA[tamano]
    precio_ingredientes = len(ingredientes_lista) * PRECIO_INGREDIENTE
    precio_unitario = precio_base + precio_ingredientes
    subtotal = precio_unitario * cantidad
    ingredientes_texto = ", ".join(ingredientes_lista)
    pizza = {
        "tamano": tamano,
        "ingredientes": ingredientes_texto,
        "precio": precio_unitario,
        "cantidad": cantidad,
        "subtotal": subtotal
    }
    carrito = session.get("carrito", [])
    carrito.append(pizza)
    session["carrito"] = carrito
    return redirect(url_for("index"))

@app.route("/quitar", methods=["POST"])
def quitar():
    indice = int(request.form["indice"])
    carrito = session.get("carrito", [])
    if indice < len(carrito):
        carrito.pop(indice)
    session["carrito"] = carrito
    return redirect(url_for("index"))


@app.route("/terminar", methods=["POST"])
def terminar():
    nombre = request.form.get("nombre")
    direccion = request.form.get("direccion")
    telefono = request.form.get("telefono")
    fecha = request.form.get("fecha")
    if not nombre:
        flash("Debes llenar los datos del cliente")
        return redirect(url_for("index"))
    carrito = session.get("carrito", [])
    if len(carrito) == 0:
        flash("No hay pizzas en el pedido")
        return redirect(url_for("index"))
    fecha = datetime.strptime(fecha, "%Y-%m-%d")
    total = sum(item["subtotal"] for item in carrito)
    flash(f"Confirmación: El total a pagar es ${total}")
    cliente = Cliente(
        nombre=nombre,
        direccion=direccion,
        telefono=telefono
    )
    db.session.add(cliente)
    db.session.commit()
    pedido = Pedido(
        id_cliente=cliente.id_cliente,
        fecha=fecha,
        total=total
    )
    db.session.add(pedido)
    db.session.commit()
    for item in carrito:
        pizza = Pizza(
            tamano=item["tamano"],
            ingredientes=item["ingredientes"],
            precio=item["precio"]
        )
        db.session.add(pizza)
        db.session.commit()
        detalle = DetallePedido(
            id_pedido=pedido.id_pedido,
            id_pizza=pizza.id_pizza,
            cantidad=item["cantidad"],
            subtotal=item["subtotal"]
        )
        db.session.add(detalle)
    db.session.commit()
    session["carrito"] = []
    return redirect(url_for("index"))

@app.route("/consulta_dia", methods=["POST"])
def consulta_dia():

    dia = request.form.get("dia").lower()
    dias = {
        "lunes": 0,
        "martes": 1,
        "miercoles": 2,
        "jueves": 3,
        "viernes": 4,
        "sabado": 5,
        "domingo": 6
    }
    if dia not in dias:
        flash("Día inválido")
        return redirect(url_for("index"))
    ventas = Pedido.query.all()
    resultado = []
    for venta in ventas:
        if venta.fecha.weekday() == dias[dia]:
            resultado.append(venta)
    total_dia = sum(v.total for v in resultado)
    carrito = session.get("carrito", [])
    total = sum(item["subtotal"] for item in carrito)
    pizzaForm = PizzaForm()
    clienteForm = ClienteForm()
    return render_template(
        "index.html",
        ventas_dia=resultado,
        total_dia=total_dia,
        carrito=carrito,
        total=total,
        pizzaForm=pizzaForm,
        clienteForm=clienteForm
    )
    
    
@app.route("/consulta_mes", methods=["POST"])
def consulta_mes():

    mes = request.form.get("mes").lower()
    meses = {
        "enero":1,"febrero":2,"marzo":3,"abril":4,
        "mayo":5,"junio":6,"julio":7,"agosto":8,
        "septiembre":9,"octubre":10,"noviembre":11,"diciembre":12
    }
    if mes not in meses:
        flash("Mes inválido")
        return redirect(url_for("index"))
    ventas = Pedido.query.filter(
        extract("month", Pedido.fecha) == meses[mes]
    ).all()
    total = sum(v.total for v in ventas)
    pizzaForm = PizzaForm()
    clienteForm = ClienteForm()
    return render_template(
        "index.html",
        ventas_mes=ventas,
        total_mes=total,
        pizzaForm=pizzaForm,
        clienteForm=clienteForm
    )
    
@app.route("/detalle", methods=["POST"])
def detalle():

    id_pedido = request.form.get("id_pedido")
    detalles = DetallePedido.query.filter_by(id_pedido=id_pedido).all()
    carrito = session.get("carrito", [])
    total = sum(item["subtotal"] for item in carrito)
    pizzaForm = PizzaForm()
    clienteForm = ClienteForm()
    return render_template(
        "index.html",
        detalles=detalles,
        carrito=carrito,
        total=total,
        pizzaForm=pizzaForm,
        clienteForm=clienteForm
    )

if __name__ == "__main__":
    app.run(debug=True)