from django import forms
from .models import MetaAhorro
from datetime import date, timedelta


class MetaAhorroForm(forms.ModelForm):
    class Meta:
        model = MetaAhorro
        fields = ['nombre', 'descripcion', 'monto_objetivo', 'moneda', 'fecha_objetivo', 'icono', 'color']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Viaje a Europa, Auto nuevo, etc.',
                'maxlength': 100
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe tu meta de ahorro...',
                'rows': 3,
                'maxlength': 500
            }),
            'monto_objetivo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '1000',
                'step': '1000'
            }),
            'fecha_objetivo': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
            }),
            'icono': forms.Select(attrs={
                'class': 'form-control'
            }),
            'color': forms.Select(attrs={
                'class': 'form-control'
            }),
            'moneda': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'nombre': 'Nombre de la meta',
            'descripcion': 'Descripción',
            'monto_objetivo': 'Monto objetivo ($)',
            'fecha_objetivo': 'Fecha objetivo',
            'icono': 'Ícono',
            'color': 'Color',
            'moneda': 'Moneda'
        }

    def clean_monto_objetivo(self):
        monto = self.cleaned_data.get('monto_objetivo')
        if monto and monto < 1000:
            raise forms.ValidationError('El monto objetivo debe ser de al menos $1,000')
        return monto

    def clean_fecha_objetivo(self):
        fecha = self.cleaned_data.get('fecha_objetivo')
        if fecha and fecha <= date.today() + timedelta(days=29):
            raise forms.ValidationError('La fecha objetivo debe ser al menos 30 días en el futuro')
        return fecha


class AgregarAhorroForm(forms.Form):
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Monto a agregar',
            'min': '1',
            'step': '1',
            'oninput': 'this.value = Math.abs(this.value)'
        }),
        label='Monto a agregar ($)'
    )
    
    descripcion = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Descripción del ahorro (opcional)'
        }),
        label='Descripción'
    )

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto and monto < 1:
            raise forms.ValidationError('El monto debe ser mayor a 0')
        return monto


class EditarMetaForm(forms.ModelForm):
    class Meta:
        model = MetaAhorro
        fields = ['nombre', 'descripcion', 'fecha_objetivo', 'icono', 'color', 'moneda', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 100
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': 500
            }),
            'fecha_objetivo': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'icono': forms.Select(attrs={
                'class': 'form-control'
            }),
            'color': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'moneda': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'nombre': 'Nombre de la meta',
            'descripcion': 'Descripción',
            'fecha_objetivo': 'Fecha objetivo',
            'icono': 'Ícono',
            'color': 'Color',
            'moneda': 'Moneda',
            'estado': 'Estado'
        }

    def clean_fecha_objetivo(self):
        fecha = self.cleaned_data.get('fecha_objetivo')
        estado = self.cleaned_data.get('estado')
        
        # Solo validar fecha futura si la meta está activa
        if estado == 'activa' and fecha and fecha <= date.today():
            raise forms.ValidationError('La fecha objetivo debe ser futura para metas activas')
        return fecha