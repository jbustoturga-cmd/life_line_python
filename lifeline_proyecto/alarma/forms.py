# alarma/forms.py — MEJORAS
# KAROL — Validaciones: nombre medicamento con letras, dosis solo números,
#         unidades con choices ml/mg/comprimido/cápsula, hora solo tipo time

import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Alarma, HistorialDosis


class FormularioAlarma(forms.ModelForm):

    class Meta:
        model  = Alarma
        fields = ['medicamento', 'dosis', 'unidad', 'frecuencia', 'cada_x_horas', 'hora_toma']
        widgets = {
            'medicamento': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Metronidazol, Ibuprofeno...',
                # ✅ HTML5: patrón que exige al menos una letra
                'pattern': r'.*[a-zA-ZáéíóúÁÉÍÓÚñÑ].*',
                'title':   'El nombre debe contener letras, no solo números o signos.'
            }),
            'dosis': forms.NumberInput(attrs={
                'class': 'form-input',
                'step':  '0.01',
                'min':   '0.01',
                'placeholder': 'Ej: 500',
                # ✅ Solo números (NumberInput ya lo garantiza)
                'inputmode': 'decimal'
            }),
            # ✅ Unidad con choices ampliados: ml, mg, comprimido, cápsula, gota, unidad
            'unidad': forms.Select(attrs={'class': 'form-input'}),
            'frecuencia': forms.Select(attrs={
                'class': 'form-input', 'id': 'id_frecuencia'
            }),
            'cada_x_horas': forms.NumberInput(attrs={
                'class': 'form-input', 'min': '1', 'max': '24',
                'placeholder': 'Ej: 8', 'id': 'id_cada_x_horas',
                'inputmode': 'numeric'
            }),
            # ✅ Hora: type="time" garantiza que solo se ingresen números en formato HH:MM
            'hora_toma': forms.TimeInput(attrs={
                'class': 'form-input', 'type': 'time'
            }),
        }

    # ── Validaciones ───────────────────────────────────────────────────────

    def clean_medicamento(self):
        """✅ El nombre del medicamento debe contener al menos una letra."""
        nombre = self.cleaned_data.get('medicamento', '').strip()
        if len(nombre) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres.')
        if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]', nombre):
            raise ValidationError(
                'El nombre del medicamento no puede ser solo números o signos. '
                'Debe contener letras (ej: Ibuprofeno, Metronidazol).'
            )
        return nombre

    def clean_dosis(self):
        """✅ La dosis debe ser un número positivo (NumberInput ya garantiza que sea número)."""
        dosis = self.cleaned_data.get('dosis')
        if dosis is None:
            raise ValidationError('La dosis es obligatoria.')
        if dosis <= 0:
            raise ValidationError('La dosis debe ser mayor a 0.')
        if dosis > 10000:
            raise ValidationError('Verifica la dosis ingresada, parece demasiado alta.')
        return dosis

    def clean_hora_toma(self):
        """✅ La hora es obligatoria (el widget type='time' ya valida el formato HH:MM)."""
        hora = self.cleaned_data.get('hora_toma')
        if not hora:
            raise ValidationError('La hora de toma es obligatoria.')
        return hora

    def clean(self):
        cleaned    = super().clean()
        frecuencia = cleaned.get('frecuencia')
        cada_x     = cleaned.get('cada_x_horas')

        if frecuencia == 'cada_x_horas':
            if not cada_x:
                self.add_error('cada_x_horas', 'Debes indicar cada cuántas horas.')
            elif cada_x < 1 or cada_x > 24:
                self.add_error('cada_x_horas', 'El intervalo debe estar entre 1 y 24 horas.')
        return cleaned


class FormularioRegistrarDosis(forms.ModelForm):
    """Formulario para marcar una dosis como tomada, omitida o tarde."""
    class Meta:
        model  = HistorialDosis
        fields = ['estado', 'nota']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-input'}),
            'nota':   forms.Textarea(attrs={
                'class':       'form-input',
                'rows':        2,
                'placeholder': '¿Tuviste algún síntoma inusual? (opcional)',
                'maxlength':   500
            }),
        }