from _testcapi import traceback_print
from django.db import models
from comunidades.models import Comunidad, Pais
from cuentas.models import Cuenta
import datetime
from cuentas_bancarias.models import CuentaBancaria
from cotizaciones.models import Cotizacion


class AsientoContable(models.Model):
    fecha = models.DateField(default=datetime.date.today())
    comunidad = models.ForeignKey(Comunidad)
    observacion=models.CharField(max_length=100,null=True)

    def __unicode__(self):
        return unicode(self.fecha)
    def anho(self):
        return self.fecha.year
    class Meta:
        verbose_name_plural = "Asientos contables"
        

class AsientoContableDetalle(models.Model):
    asiento_contable = models.ForeignKey(AsientoContable)
    cuenta = models.ForeignKey(Cuenta)
    debe = models.DecimalField(max_digits=22,default=0,decimal_places=2)
    haber = models.DecimalField(max_digits=22, default=0, decimal_places=2)
    cuenta_bancaria=models.ForeignKey(CuentaBancaria,null=True,blank=True)
    observacion = models.CharField(max_length=100, null=True)


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
        if Cotizacion.objects.filter(pais=self.pais_id(),fecha=self.fecha()).exists():
            cotizacion=Cotizacion.objects.filter(pais=self.pais_id(), fecha=self.fecha())[0]
            return cotizacion.monto
        else:
            return 0
    def haber_en_dolares(self):
        if self.cotizacion_del_dia() > 0:
            return round(self.haber/self.cotizacion_del_dia(),2)
        else:
            #si en el dia no existe una cotizacion se retorna 1 para que se pueda realizar la operacion
            return 1
    def debe_en_dolares(self):
        if self.cotizacion_del_dia() > 0:
            return round(self.debe/self.cotizacion_del_dia(),2)
        else:
            #si en el dia no existe una cotizacion se retorna 1 para que se pueda realizar la operacion
            return 1

    def saldo(self):
        return self.debe - self.haber

    def saldo_en_dolares(self):
        return self.debe_en_dolares() - self.haber_en_dolares()
