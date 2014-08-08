from django.db import models

class Ejercicio(models.Model):
    anho = models.IntegerField()
    actual = models.BooleanField();

    def __unicode__(self):
        return str(self.anho)

