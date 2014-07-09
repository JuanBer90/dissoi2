from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models.aggregates import Sum
from django.forms.models import BaseInlineFormSet
from django.utils.functional import curry
#from sphinx.locale import _
from asientos_contables.models import AsientoContable, AsientoContableDetalle
from django.contrib.auth.models import User
from ajax_select.admin import AjaxSelectAdmin, AjaxSelectAdminTabularInline
from ajax_select import make_ajax_form
from cuentas.models import Cuenta

class AsientoContableDetalleInLine(AjaxSelectAdminTabularInline):
    model = AsientoContableDetalle
    form = make_ajax_form(AsientoContableDetalle, {'cuenta': 'cuenta'})
    extra = 3

class AsientoContableAdminFilter(AjaxSelectAdmin):

    def save_model(self, request, asientocontable, form, change):
        usuario_id = request.user.id
        usuario_objeto = User.objects.get(id=usuario_id)
        asientocontable.comunidad = usuario_objeto.usuario.comunidad
        asientocontable.save()

    def queryset(self, request):
        usuario_id = request.user.id
        usuario_objeto = User.objects.get(id=usuario_id)
        qs = super(AsientoContableAdminFilter, self).queryset(request)
        return qs.filter(comunidad=usuario_objeto.usuario.comunidad)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True # So they can see the change list page
        if request.user.is_superuser or obj.author == request.user:
            return True
        else:
            return False


class AsientoContableAdmin(AsientoContableAdminFilter):
    print __file__
    inlines = [AsientoContableDetalleInLine,]
    list_display = ('fecha','comunidad')
    list_filter = ['fecha']
    search_fields = ['fecha']
    fieldsets = [
        (None,               {'fields': ['fecha']}),
        ]



admin.site.register(AsientoContable, AsientoContableAdmin)
# Register your models here.
#
# class CompositionElementFormSet(BaseInlineFormSet):
#     '''
#     Validate formset data here
#     '''
#     def clean(self):
#         super(CompositionElementFormSet, self).clean()
#
#         percent = 0
#         for form in self.forms:
#             if not hasattr(form, 'cleaned_data'):
#                 continue
#             data = form.cleaned_data
#             percent += data.get('percent', 0)
#
#         if percent != 100:
#             raise ValidationError(_('Total of elements must be 100%%. Current : %(percent).2f%%') % {'percent': percent})
#
# class CompositionElementAdmin(admin.TabularInline):
#     model = AsientoContableDetalle
#     formset = CompositionElementFormSet
#
# class CompositionAdmin(admin.ModelAdmin):
#     inlines = (CompositionElementAdmin,)
#
# admin.site.register(AsientoContable, CompositionAdmin)