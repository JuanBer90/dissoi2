from ajax_select.fields import AutoCompleteSelectField
from django import forms
from django.forms import ModelForm

class UsuarioLimitadoForm(ModelForm):
    comunidad = AutoCompleteSelectField('comunidad', required=False,
                     help_text=None, plugin_options = {'autoFocus': True, 'minLength': 1})
    def clean_comunidad(self):
        if self.cleaned_data['comunidad'] == None:
             raise forms.ValidationError("Debe seleccionar una comunidad")
        return self.cleaned_data['comunidad']    

class UsuarioForm(ModelForm):
    comunidad = AutoCompleteSelectField('comunidad', required=False,
                     help_text=None, plugin_options = {'autoFocus': True, 'minLength': 1})
