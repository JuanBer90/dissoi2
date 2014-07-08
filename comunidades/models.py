from django.db import models

class Pais(models.Model):
	pais = models.CharField(max_length=40)
	moneda = models.CharField(max_length=40)
	def __unicode__(self):
		return self.pais
	class Meta:
		verbose_name_plural = "paises"

class Comunidad(models.Model):
	pais = models.ForeignKey('Pais')
	comunidad = models.CharField(max_length=100)
	def __unicode__(self):
		return self.comunidad
	class Meta:
		verbose_name_plural = "comunidades"

# Create your models here.
