from django.contrib import admin
from comunidades.models import Pais, Comunidad
from ajax_select import make_ajax_form

class PaisAdmin(admin.ModelAdmin):
	list_display = ('pais','moneda')

class ComunidadAdmin(admin.ModelAdmin):
	list_display = ('comunidad','pais')
	list_filter = ['pais']
	search_fields = ['comunidad']
	
admin.site.register(Pais, PaisAdmin)
admin.site.register(Comunidad, ComunidadAdmin)


# Register your models here.
