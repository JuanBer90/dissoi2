from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User,Permission
from django.utils.translation import ugettext_lazy as _
from comunidades.models import Pais,Comunidad
from django.contrib.auth.forms import UserChangeForm
from django.forms import ModelForm
from usuarios.models import Usuario
from forms import UsuarioForm,UsuarioLimitadoForm
from filters import PaisListFilter
from hijasdelacaridad.globales import USUARIO_LIMITADO

from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.contrib.admin.filters import FieldListFilter

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton

class UsuarioLimitado(User):
    class Meta:
        proxy = True
        
    def pais(self):
        usuario=Usuario.objects.filter(user_id=self.pk)
        if usuario.count()> 0:
            if usuario[0].comunidad != None:
                return usuario[0].comunidad.pais
        return "No asignado"
        
    def comunidad(self):
        usuario=Usuario.objects.filter(user_id=self.pk)
        if usuario.count()> 0:
            if usuario[0].comunidad != None:
                return usuario[0].comunidad
        return "No asignada"
            
    def nombre_completo(self):
        return self.get_full_name()




class PermissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Permission, PermissionAdmin)



class UsuarioInLine(admin.StackedInline):
    can_delete = False
    verbose_name_plural = 'Asignar Comunidad'
    fieldsets=((None, {'fields': ['user', 'comunidad']}),)
    model = Usuario
    form=UsuarioForm


class UsuarioAdmin(UserAdmin):
     inlines = (UsuarioInLine, )
     search_fields = ('username','first_name','last_name')
     list_filter=(PaisListFilter,)
     fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser','user_permissions' )}),  )
    
       



class UsuarioLimitadoInLine(UsuarioInLine):
    form = UsuarioLimitadoForm
            
        
class UsuarioLimitadoAdmin(UsuarioAdmin):
    inlines = (UsuarioLimitadoInLine,)
    list_display=('username','email','nombre_completo','comunidad','pais')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),    
    )
    
    def save_model(self, request, obj, form, change):
        permission = Permission.objects.get(codename='limitado')
        obj.user_permissions.add(permission)
        obj.is_staff=True
        obj.is_active=True
        obj.save()
    
    
  
    def queryset(self, request):
        return self.model.objects.filter(is_superuser=False)
    
    
 
    
admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
admin.site.register(UsuarioLimitado, UsuarioLimitadoAdmin)







class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    readonly_fields = LogEntry._meta.get_all_field_names()
    list_filter = ['user','content_type', 'action_flag' ]
    search_fields = [ 'object_repr','change_message' ]
    list_display = ['action_time', 'user','content_type', 'object_link','action_flag','change_message',]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'
    
    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')


admin.site.register(LogEntry, LogEntryAdmin)
