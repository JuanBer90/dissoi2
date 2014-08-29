from django.db import models
from django.contrib.auth.models import User

from comunidades.models import Comunidad

class Usuario(models.Model):
    user = models.OneToOneField(User,blank=True,null=True)
    comunidad = models.ForeignKey(Comunidad,blank=True,null=True)
    
    def __unicode__(self):
        return str(self.user.username)
   
