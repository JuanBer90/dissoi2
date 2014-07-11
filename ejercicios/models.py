from django.db import models

class Ejercicio(models.Model):
    anho = models.CharField(max_length=4,unique=True)

# Create your models here.
