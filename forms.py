from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, DateField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets import ListWidget, CheckboxInput


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class PizzaForm(FlaskForm):

    tamano = RadioField(
        "Tamaño de Pizza",
        choices=[
            ("chica", "Chica ($40)"),
            ("mediana", "Mediana ($80)"),
            ("grande", "Grande ($120)")
        ],
        validators=[DataRequired()]
    )
    ingredientes = MultiCheckboxField(
        "Ingredientes",
        choices=[
            ("jamon", "Jamón ($10)"),
            ("pina", "Piña ($10)"),
            ("champinones", "Champiñones ($10)")
        ]
    )
    cantidad = IntegerField(
        "Número de pizzas",
        validators=[DataRequired(), NumberRange(min=1)]
    )
    agregar = SubmitField("Agregar")


class ClienteForm(FlaskForm):

    nombre = StringField(
        "Nombre completo",
        validators=[DataRequired(), Length(max=100)]
    )
    direccion = StringField(
        "Dirección",
        validators=[DataRequired(), Length(max=200)]
    )
    telefono = StringField(
        "Teléfono",
        validators=[DataRequired(), Length(max=20)]
    )
    fecha = DateField("Fecha de compra", validators=[DataRequired()])
    terminar = SubmitField("Terminar Pedido")