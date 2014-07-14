from django.db import models
from comunidades.models import Comunidad, Pais
from cuentas.models import Cuenta
import datetime
from cuentas_bancarias.models import CuentaBancaria
from cotizaciones.models import Cotizacion


class AsientoContable(models.Model):
    fecha = models.DateField(default=datetime.date.today())
    comunidad = models.ForeignKey(Comunidad)

    def __unicode__(self):
        return unicode(self.fecha)
    def anho(self):
        return fecha.year()
    class Meta:
        verbose_name_plural = "Asientos contables"
        

class AsientoContableDetalle(models.Model):
    asiento_contable = models.ForeignKey(AsientoContable)
    cuenta = models.ForeignKey(Cuenta)
    debe = models.DecimalField(max_digits=22,default=0,decimal_places=2)
    haber = models.DecimalField(max_digits=22, default=0, decimal_places=2)
    cuenta_bancaria=models.ForeignKey(CuentaBancaria,null=True)
    def comunidad_id(self):
        asiento = AsientoContable.objects.get(id=self.asiento_contable.id)
        return asiento.comunidad.id
    def pais_id(self):
        pais = Pais.objects.get(comunidad = self.comunidad_id())
        return pais.id
    def fecha(self):
        asiento = AsientoContable.objects.get(id=self.asiento_contable.id)
        return asiento.fecha
    def anho(self):
        return self.fecha().year
    def cotizacion_del_dia(self):
        cotizacion = Cotizacion.objects.get(pais=self.pais_id(),fecha=self.fecha())
        return cotizacion.monto
    def haber_en_dolares(self):
        return self.haber/self.cotizacion_del_dia()
    def debe_en_dolares(self):
        return self.debe/self.cotizacion_del_dia()

