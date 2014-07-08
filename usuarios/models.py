from django.db import models
from django.contrib.auth.models import User

from comunidades.models import Comunidad

class Usuario(models.Model):
    user = models.OneToOneField(User)
    comunidad = models.ForeignKey(Comunidad)

# Create your models here.
