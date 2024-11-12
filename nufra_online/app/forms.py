from django import forms
from .models import Usuario

class AddUserForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.NumberInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.HiddenInput(),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'rol': forms.HiddenInput(),
        }