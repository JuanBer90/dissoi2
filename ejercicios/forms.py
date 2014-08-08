from django import forms
from ejercicios.models import Ejercicio


class EjercicioForm(forms.ModelForm):

    class Meta:
        model = Ejercicio
    def clean_anho(self):
        if Ejercicio.objects.filter(anho=self.cleaned_data['anho']).exists():
            raise forms.ValidationError("Ya existe un ejercicio en este anho!")
        return self.cleaned_data['anho']