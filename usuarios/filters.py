from comunidades.models import Pais,Comunidad
from django.contrib import admin
from models import Usuario

class PaisListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ('pais')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'pais'

    def lookups(self, request, model_admin):
        paises=Pais.objects.all()
        lista=[[0,'Sin Asignar']]
        for pais in paises:
            lista.append([pais.id,pais.pais])
        return lista
    
    def queryset(self, request, queryset):
        print self.value()
        if self.value() == None or self.value() == "?":
              return queryset.filter(is_superuser=False)
        
        comunidades=Comunidad.objects.filter(pais_id=self.value())
        list_id=[]
        for c in comunidades:
            list_id.append( c.id)
        usuarios=Usuario.objects.filter(comunidad_id__in=list_id)
        list_id=[]
        for u in usuarios:
            list_id.append(u.user_id)
        
        return queryset.filter(pk__in=list_id,is_superuser=False)
        


