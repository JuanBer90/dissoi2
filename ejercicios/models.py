from django.db import models
from django.contrib.auth.signals import user_logged_in

class Ejercicio(models.Model):
    anho = models.IntegerField()
    actual = models.BooleanField();

    def __unicode__(self):
        return str(self.anho)
    


def get_ejercicio(sender, user, request, **kwargs):
      ejercicio=Ejercicio.objects.filter(actual=True)
      if ejercicio.count() > 0:
          request.session['ejercicio']=str(ejercicio[0].anho)
      else:
          request.session['ejercicio']="Seleccionar ejercicio"

user_logged_in.connect(get_ejercicio)

