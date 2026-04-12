# alarma/models.py — MEJORAS
# KAROL — UNIDAD_CHOICES ampliados con ml, mg, comprimido, cápsula, gota, unidad

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
#models.py

class Alarma(models.Model):

    # ✅ Unidades ampliadas según el tipo de medicamento
    UNIDAD_CHOICES = [
        ('ml',          'ml (mililitros)'),
        ('mg',          'mg (miligramos)'),
        ('comprimido',  'Comprimido'),
        ('capsula',     'Cápsula'),
        ('gota',        'Gota'),
        ('unidad',      'Unidad'),
        ('sobre',       'Sobre'),
        ('ampolla',     'Ampolla'),
    ]

    FRECUENCIA_CHOICES = [
        ('diaria',       'Diaria'),
        ('cada_x_horas', 'Recurrente (Cada X horas)'),
        ('prn',          'Según Necesidad (PRN)'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alarmas'
    )
    medicamento = models.CharField(max_length=200, verbose_name='Medicamento')
    dosis = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name='Dosis'
    )
    unidad = models.CharField(
        max_length=15, choices=UNIDAD_CHOICES,
        default='comprimido', verbose_name='Unidad'
    )
    frecuencia = models.CharField(
        max_length=20, choices=FRECUENCIA_CHOICES,
        default='diaria', verbose_name='Frecuencia'
    )
    cada_x_horas = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name='Cada cuántas horas',
        help_text='Solo si la frecuencia es "Cada X horas"'
    )
    hora_toma = models.TimeField(verbose_name='Hora de toma')
    activa    = models.BooleanField(default=True, verbose_name='Activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Alarma'
        verbose_name_plural = 'Alarmas'
        ordering = ['hora_toma']

    def __str__(self):
        return f"{self.medicamento} — {self.hora_toma} ({self.usuario.username})"

    def clean(self):
        if self.frecuencia == 'cada_x_horas':
            if not self.cada_x_horas:
                raise ValidationError('Debes indicar cada cuántas horas.')
            if self.cada_x_horas < 1 or self.cada_x_horas > 24:
                raise ValidationError('El intervalo debe estar entre 1 y 24 horas.')
        if self.dosis and self.dosis <= 0:
            raise ValidationError('La dosis debe ser mayor a 0.')


class HistorialDosis(models.Model):

    ESTADO_CHOICES = [
        ('tomada',  'Tomada'),
        ('omitida', 'Omitida'),
        ('tarde',   'Tomada tarde'),
    ]

    alarma = models.ForeignKey(Alarma, on_delete=models.CASCADE, related_name='historial')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    fecha  = models.DateField(default=timezone.now)
    hora   = models.TimeField(auto_now_add=True)
    nota   = models.TextField(blank=True, verbose_name='Síntoma / nota')

    class Meta:
        verbose_name = 'Historial de dosis'
        ordering     = ['-fecha', '-hora']

    def __str__(self):
        return f"{self.alarma.medicamento} — {self.estado} — {self.fecha}"