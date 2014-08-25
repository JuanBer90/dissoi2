from django.db import models
from django.views.generic.dates import timezone_today
from comunidades.models import Comunidad

TIPO_MOVIMIENTO=(('INI','STOCK INICIAL'),
              ('ENT','ENTRADA'),
              ('SAL','SALIDA')
              )

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    
    #
    def total(self,id_comunidad):
        detalles=CategoriaDetalle.objects.filter(categoria=self,comunidad_id=id_comunidad)
        total=0
        for detalle in detalles:
            total+=detalle.precio_total()
        return total
    
    def cantidad(self,id_comunidad):
        detalles=CategoriaDetalle.objects.filter(categoria=self,comunidad_id=id_comunidad)
        total=0
        for detalle in detalles:
            total+=detalle.cantidad
        return total
    
        
    
    def __unicode__(self):
        return self.nombre
class CategoriaDetalle(models.Model):
    descripcion = models.CharField(max_length=200)
    categoria=models.ForeignKey(Categoria)
    cantidad=models.IntegerField()
    precio_unitario=models.DecimalField(max_digits=22,default=0,decimal_places=2)
    comunidad=models.ForeignKey(Comunidad)
    
    def __unicode__(self):
        return self.descripcion
    
    def precio_total(self):
        return self.precio_unitario*self.cantidad
    
class CategoriaDetalleMovimiento(models.Model):
    movimiento = models.CharField(max_length=3, choices=TIPO_MOVIMIENTO)
    observacion = models.CharField(max_length=200,null=True)
    categoria_detalle=models.ForeignKey(CategoriaDetalle)
    cantidad=models.IntegerField()
    fecha=models.DateField(default=timezone_today())
    
    
    
    
    
    