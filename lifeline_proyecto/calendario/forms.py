# calendario/forms.py — MEJORAS
# KAROL — Validaciones: lugar solo letras/espacios, profesional solo letras,
#         título debe tener letras, hora con widget type="time"

import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import CitaMedica


class FormularioCita(forms.ModelForm):

    class Meta:
        model  = CitaMedica
        fields = ['tipo', 'titulo', 'fecha', 'hora', 'lugar', 'profesional', 'recordatorio']
        widgets = {
            'tipo':   forms.Select(attrs={'class': 'form-input'}),
            'titulo': forms.TextInput(attrs={
                'class':       'form-input',
                'placeholder': 'Ej: Quimioterapia Sesión #5',
                # ✅ HTML5: exige al menos una letra
                'pattern': r'.*[a-zA-ZáéíóúÁÉÍÓÚñÑ].*',
                'title':   'El título debe contener letras, no solo números o signos.'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date'
            }),
            # ✅ Hora: type="time" garantiza solo números en formato HH:MM
            'hora': forms.TimeInput(attrs={
                'class': 'form-input', 'type': 'time'
            }),
            'lugar': forms.TextInput(attrs={
                'class':       'form-input',
                'placeholder': 'Hospital, Consultorio, Clínica...',
                # ✅ HTML5: permite letras, espacios y signos básicos de dirección
                'pattern': r"[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s.,#\-]+",
                'title':   'Solo letras, números, espacios y signos básicos (.,#-)'
            }),
            'profesional': forms.TextInput(attrs={
                'class':       'form-input',
                'placeholder': 'Nombre del médico o profesional',
                # ✅ HTML5: solo letras y espacios
                'pattern': r'[a-zA-ZáéíóúÁÉÍÓÚñÑ\s.]+',
                'title':   'El nombre del profesional solo puede contener letras.'
            }),
            'recordatorio': forms.Select(attrs={'class': 'form-input'}),
        }

    # ── Validaciones Python (se ejecutan en el servidor) ──────────────────

    def clean_titulo(self):
        """✅ El título no puede ser solo números ni signos."""
        titulo = self.cleaned_data.get('titulo', '').strip()
        if len(titulo) < 3:
            raise ValidationError('El título debe tener al menos 3 caracteres.')
        if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]', titulo):
            raise ValidationError(
                'El título no puede ser solo números o signos. '
                'Debe contener letras (ej: Quimioterapia Sesión #5).'
            )
        return titulo

    def clean_fecha(self):
        """La fecha debe ser futura."""
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < timezone.now().date():
            raise ValidationError('La fecha de la cita debe ser futura.')
        return fecha

    def clean_hora(self):
        """✅ La hora es obligatoria (TimeInput ya valida el formato HH:MM)."""
        hora = self.cleaned_data.get('hora')
        if not hora:
            raise ValidationError('La hora de la cita es obligatoria.')
        return hora

    def clean_lugar(self):
        """✅ El lugar puede tener letras, números y signos básicos de dirección."""
        lugar = self.cleaned_data.get('lugar', '').strip()
        if lugar and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s.,#\-]+$', lugar):
            raise ValidationError(
                'El lugar solo puede contener letras, números, espacios y '
                'signos básicos (punto, coma, numeral, guión).'
            )
        return lugar

    def clean_profesional(self):
        """✅ El nombre del profesional solo puede tener letras y espacios."""
        prof = self.cleaned_data.get('profesional', '').strip()
        if prof and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s.]+$', prof):
            raise ValidationError(
                'El nombre del profesional solo puede contener letras y espacios. '
                'No se permiten números ni signos especiales.'
            )
        return prof