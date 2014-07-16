from django.db import models
from ejercicios.models import Ejercicio
from cuentas.models import Cuenta

MESES = (
    ('1', 'Enero'),
    ('2', 'Febrero'),
    ('3', 'Marzo'),
    ('4', 'Abril'),
    ('5', 'Mayo'),
    ('6', 'Junio'),
    ('7', 'Julio'),
    ('8', 'Agosto'),
    ('9', 'Septiembre'),
    ('10', 'Octubre'),
    ('11', 'Noviembre'),
    ('12', 'Diciembre'),
)

class Presupuesto(models.Model):
    ejercicio = models.ForeignKey(Ejercicio)
    mes = models.SmallIntegerField(choices=MESES)
    cuenta = models.ForeignKey(Cuenta)
    monto = models.DecimalField(max_digits=22, default=0, decimal_places=2)

    

    
    
# Create your models here.
