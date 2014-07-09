from django.db import models
from comunidades.models import Comunidad

class CuentaBancaria(models.Model):
    comunidad = models.ForeignKey(Comunidad)
    cuenta_bancaria = models.CharField(max_length=50)
    nro_de_cuenta = models.CharField(max_length=50)
    observacion = models.CharField(max_length=200)
    saldo = models.DecimalField(max_digits=22, decimal_places=2,blank=True)

    class Meta:
        verbose_name_plural = "Cuentas bancarias"

# Create your models here.
