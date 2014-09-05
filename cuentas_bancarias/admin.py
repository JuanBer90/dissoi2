from django.contrib import admin
from cuentas_bancarias.models import CuentaBancaria
from django.contrib.auth.models import User

class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ('cuenta_bancaria','nro_de_cuenta','saldo')
    fieldsets = [
        (None,               {'fields': ['cuenta_bancaria','nro_de_cuenta','saldo','observacion']}),
        ]
    def save_model(self, request, cuentabancaria, form, change):
        usuario_id = request.user.id
        usuario_objeto = User.objects.get(id=usuario_id)
        cuentabancaria.comunidad = usuario_objeto.usuario.comunidad
        cuentabancaria.save()

    def queryset(self, request):
        usuario_id = request.user.id
        usuario_objeto = User.objects.get(id=usuario_id)
        qs = super(CuentaBancariaAdmin, self).queryset(request)
        return qs.filter(comunidad=usuario_objeto.usuario.comunidad)

    def has_change_permission(self, request, obj=None):
       return True

    def has_add_permission(self, request, obj=None):
       return True

admin.site.register(CuentaBancaria, CuentaBancariaAdmin)

# Register your models here.
