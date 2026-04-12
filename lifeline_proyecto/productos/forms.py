# productos/forms.py — ACTUALIZADO
# Validación: nombre debe contener al menos una letra (no solo números)
# Campo variantes: opcional

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Producto, Categoria
import re


class FormularioProducto(forms.ModelForm):

    # ✅ Campo variantes — OPCIONAL, no es campo del modelo (se guarda en descripcion o extra)
    variantes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Rojo, Azul, Verde  |  S, M, L, XL  |  50ml, 100ml, 250ml'
        }),
        label='Variantes (opcional)',
        help_text='Colores, tallas, tamaños, etc. Separa con coma. Déjalo vacío si no aplica.'
    )

    class Meta:
        model  = Producto
        fields = [
            'nombre', 'descripcion', 'categoria', 'precio_final',
            'cantidad', 'estado', 'uso_recomendado', 'imagen', 'fecha_vencimiento'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto (mín. 3 caracteres, debe contener letras)'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Descripción detallada del producto'
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'precio_final': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01',
                'min': '0.01', 'max': '9999999', 'placeholder': 'Precio en COP'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'placeholder': 'Unidades en stock'
            }),
            'estado': forms.Select(
                choices=[(True, 'Activo ✔'), (False, 'Inactivo ❌')],
                attrs={'class': 'form-select'}
            ),
            'uso_recomendado': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        if len(nombre) > 100:
            raise ValidationError('El nombre no puede superar 100 caracteres.')
        # ✅ NUEVO: el nombre debe contener al menos una letra (no solo números)
        if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]', nombre):
            raise ValidationError('El nombre debe contener al menos una letra, no puede ser solo números.')
        return nombre

    def clean_precio_final(self):
        precio = self.cleaned_data.get('precio_final')
        if precio is None or precio <= 0:
            raise ValidationError('El precio debe ser un valor positivo mayor a 0.')
        if precio > 9999999:
            raise ValidationError('El precio máximo permitido es $9.999.999.')
        return precio

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad < 0:
            raise ValidationError('El stock no puede ser negativo.')
        return cantidad

    def clean_fecha_vencimiento(self):
        fecha = self.cleaned_data.get('fecha_vencimiento')
        if fecha and fecha <= timezone.now().date():
            raise ValidationError('La fecha de vencimiento debe ser futura.')
        return fecha

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen and hasattr(imagen, 'size'):
            if imagen.size > 5 * 1024 * 1024:
                raise ValidationError('La imagen no puede superar 5MB.')
            tipos_validos = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(imagen, 'content_type') and imagen.content_type not in tipos_validos:
                raise ValidationError('Solo se permiten imágenes JPG, PNG o WebP.')
        return imagen

    def clean(self):
        cleaned   = super().clean()
        nombre    = cleaned.get('nombre')
        categoria = cleaned.get('categoria')
        if nombre and categoria:
            qs = Producto.objects.filter(nombre__iexact=nombre, categoria=categoria)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    f'Ya existe un producto llamado "{nombre}" en la categoría "{categoria}".'
                )
        return cleaned

    def save(self, commit=True):
        """
        Si hay variantes, las agregamos al final de la descripción del producto.
        No es un campo del modelo, así que se fusiona con la descripción.
        """
        instance  = super().save(commit=False)
        variantes = self.cleaned_data.get('variantes', '').strip()

        if variantes:
            desc_actual = instance.descripcion or ''
            if '\n\nVariantes:' not in desc_actual:
                instance.descripcion = f"{desc_actual}\n\nVariantes: {variantes}".strip()

        if commit:
            instance.save()
        return instance


class FormularioCategoria(forms.ModelForm):
    class Meta:
        model  = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Descripción breve (opcional)'
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 2:
            raise ValidationError('El nombre de la categoría es demasiado corto.')
        return nombre