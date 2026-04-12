# calendario/models.py — FASE 3
# KAROL — Modelo de citas médicas

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class CitaMedica(models.Model):

    TIPO_CHOICES = [
        ('quimioterapia',  'Quimioterapia'),
        ('radioterapia',   'Radioterapia'),
        ('examenes',       'Exámenes de laboratorio'),
        ('nutricion',      'Nutrición'),
        ('psicologia',     'Psicología'),
        ('oncologia',      'Oncología'),
        ('otro',           'Otro'),
    ]
    ESTADO_CHOICES = [
        ('pendiente',   'Pendiente'),
        ('completada',  'Completada'),
        ('cancelada',   'Cancelada'),
    ]
    RECORDATORIO_CHOICES = [
        ('24h',    '24 horas antes'),
        ('2h',     '2 horas antes'),
        ('correo', 'Por correo'),
        ('ninguno','Sin recordatorio'),
    ]

    usuario      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='citas')
    tipo         = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de cita')
    titulo       = models.CharField(max_length=200, verbose_name='Título / descripción')
    fecha        = models.DateField(verbose_name='Fecha')
    hora         = models.TimeField(verbose_name='Hora')
    lugar        = models.CharField(max_length=200, blank=True, verbose_name='Lugar')
    profesional  = models.CharField(max_length=200, blank=True, verbose_name='Profesional')
    recordatorio = models.CharField(max_length=10, choices=RECORDATORIO_CHOICES, default='24h')
    estado       = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cita Médica'
        verbose_name_plural = 'Citas Médicas'
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.fecha} {self.hora}"

    def clean(self):
        if self.fecha and self.fecha < timezone.now().date():
            raise ValidationError('La fecha de la cita debe ser futura.')

    def es_proxima(self):
        """True si la cita es en los próximos 7 días."""
        from datetime import timedelta
        hoy = timezone.now().date()
        return hoy <= self.fecha <= hoy + timedelta(days=7)
