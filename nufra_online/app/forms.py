from django import forms
from .models import Producto, Usuario
from django.core.exceptions import ValidationError

class AddUserForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'12345678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Matias'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'matias.me@gmail.com'}),
            'telefono': forms.NumberInput(attrs={'class': 'form-control', 'placeholder':'2145894'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Calle Real 2812'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'estado': forms.HiddenInput(),
            'rol': forms.HiddenInput(),
        }

    def calcular_dv(self, rut):
        # Invertir el número del RUT y convertirlo en una lista de enteros
        rut = str(rut)[::-1]
        multiplicadores = [2, 3, 4, 5, 6, 7, 2, 3, 4, 5, 6, 7]
        suma = 0

        # Realizar la multiplicación de los dígitos por los multiplicadores
        for i in range(len(rut)):
            suma += int(rut[i]) * multiplicadores[i]

        # Calcular el residuo de la suma
        residuo = suma % 11

        # Calcular el dígito verificador
        dv = 11 - residuo

        if dv == 10:
            return 'K'
        elif dv == 11:
            return '0'
        else:
            return str(dv)
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut', '')
        
        if not rut:
            return rut
        rut = rut.replace('.', '').replace('-', '').upper()
        
        if len(rut) < 2:
            raise ValidationError('El RUT Ingresado no es Válido')
        
        numero_base = rut[:-1]
        dv_usuario = rut[-1]

        dv_calculado = self.calcular_dv(numero_base)

        if dv_calculado != dv_usuario:
            # raise ValidationError(f'El RUT ingresado es incorrecto. El dígito verificador correcto es {dv_calculado}.')
            raise ValidationError(f'El RUT ingresado es incorrecto.')
    
        rut_formateado = f"{numero_base}-{dv_usuario}"

        # DUPLICADO
        if Usuario.objects.filter(rut=rut_formateado).exists():
            raise ValidationError("El RUT ingresado ya está registrado.")

        return rut
