# ejercicio/models.py — FASE 3
# lara

from django.db import models
from django.conf import settings
from django.utils import timezone


class SesionEjercicio(models.Model):

    NIVEL_CHOICES = [
        ('alta',   'Alta Energía'),
        ('media',  'Energía Media'),
        ('dificil','Día Difícil'),
    ]

    usuario       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sesiones_ejercicio')
    nivel_energia = models.CharField(max_length=10, choices=NIVEL_CHOICES, verbose_name='Nivel de energía')
    duracion_min  = models.PositiveIntegerField(default=15, verbose_name='Duración (minutos)')
    completada    = models.BooleanField(default=False)
    nota          = models.TextField(blank=True, verbose_name='Cómo me sentí')
    fecha         = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = 'Sesión de ejercicio'
        verbose_name_plural = 'Sesiones de ejercicio'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} — {self.get_nivel_energia_display()} — {self.fecha}"