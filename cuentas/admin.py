from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from cuentas.models import Cuenta

class CuentaAdmin(admin.ModelAdmin):
    form = movenodeform_factory(Cuenta)
    list_display = ('codigo','cuenta')
    list_filter = ['tipo']
    
   
          
    def save_model(self, request, cuenta, form, change):
        cuenta.codigo_ordenado = cuenta.codigo_conversion()
        cuenta.save()
        
        
    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
         
        Force get_ordering to return None (if no ordering specified)
        to prevent  from applying ordering.
        """
        from django.contrib.admin.views.main import ChangeList
         
        
        class SortedChangeList(ChangeList):
            
            def get_query_set(self, *args, **kwargs):
                qs = super(SortedChangeList, self).get_query_set(*args, **kwargs)
                return qs.order_by('codigo_ordenado')
                 
        if request.GET.get('o'):
            return ChangeList
             
        return SortedChangeList
    
        
admin.site.register(Cuenta, CuentaAdmin)


