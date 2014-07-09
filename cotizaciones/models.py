from django.db import models
from comunidades.models import Pais

class Cotizacion(models.Model):
    pais = models.ForeignKey(Pais)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=22, default=0, decimal_places=3)

# Create your models here.
