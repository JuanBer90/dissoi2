from django.db import models
from django.db.models.aggregates import Sum
from comunidades.models import Comunidad
from cuentas.models import Cuenta
import datetime


class AsientoContable(models.Model):
    fecha = models.DateField(default=datetime.date.today())
    comunidad = models.ForeignKey(Comunidad)

    def __unicode__(self):
        return unicode(self.fecha)
    class Meta:
        verbose_name_plural = "Asientos contables"

class AsientoContableDetalle(models.Model):
    asiento_contable = models.ForeignKey(AsientoContable)
    cuenta = models.ForeignKey(Cuenta)
    debe = models.DecimalField(max_digits=22,default=0,decimal_places=2)
    haber = models.DecimalField(max_digits=22, default=0, decimal_places=2)

    def comunidad_id(self):
        asiento = AsientoContable.objects.get(id=self.asiento_contable.id)
        return asiento.comunidad.id

