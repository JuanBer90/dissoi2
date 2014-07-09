from django.db import models
from treebeard.mp_tree import MP_Node

TIPOS_DE_CUENTA = (
    ('AC', 'Activo'),
    ('PA', 'Pasivo'),
    ('PN', 'Patrimonio Neto'),
    ('GA', 'Ganancias'),
    ('PE', 'Perdidas'),
)

class Cuenta(MP_Node):
    cuenta = models.CharField(max_length=200)
    tipo = models.CharField(max_length=2, choices=TIPOS_DE_CUENTA)
    codigo = models.CharField(max_length=30)
    
    debe = 0
    haber = 0
    cargado = False
    
    node_order_by = ['cuenta']

    def __unicode__(self):
        return self.cuenta
    
    def saldo(self):
        return self.debe - self.haber
    
    
    def cuenta_depth(self):
        return "____"*(self.depth-1) + self.codigo + "  " + self.cuenta
    
    def have_child(self):
        if self.numchild == 0:
            return False
        else:
            return True
 

        
# Create your models here.