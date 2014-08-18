from django.db import models
from comunidades.models import Pais
from _codecs import encode

class Cotizacion(models.Model):
    pais = models.ForeignKey(Pais)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=22, default=0, decimal_places=3)
    def __unicode__(self):
        return str(self.fecha)
    
    class Meta:
        verbose_name_plural = "Cotizaciones"

# Create your models here.
