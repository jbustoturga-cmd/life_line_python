# usuarios/models.py
# Solo agrega foto_perfil al modelo Usuario existente.
# El resto queda EXACTAMENTE igual que antes.

import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime


def validar_fecha_nacimiento(fecha):
    """Valida que la fecha de nacimiento sea real y no futura"""
    hoy = timezone.now().date()
    if fecha > hoy:
        raise ValidationError("La fecha de nacimiento no puede ser futura.")
    if fecha.year < 1900:
        raise ValidationError("Ingresa una fecha de nacimiento válida.")
    edad = (hoy - fecha).days // 365
    if edad < 5:
        raise ValidationError("Debes tener al menos 5 años para registrarte.")
    if edad > 120:
        raise ValidationError("Ingresa una fecha de nacimiento válida.")


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('USER',     'Usuario'),
        ('PACIENTE', 'Paciente'),
        ('ADMIN',    'Administrador'),
    ]
    ESTADIO_CHOICES = [
        ('ESTADO1', 'Estadio 1'),
        ('ESTADO2', 'Estadio 2'),
        ('ESTADO3', 'Estadio 3'),
        ('ESTADO4', 'Estadio 4'),
    ]
    TIPO_DOC_CHOICES = [
        ('cc', 'Cédula de ciudadanía'),
        ('ti', 'Tarjeta de identidad'),
        ('ce', 'Cédula extranjera'),
    ]

    # ─── ÚNICO CAMPO NUEVO ────────────────────────────────────
    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil'
    )
    # ──────────────────────────────────────────────────────────

    rol              = models.CharField(max_length=20, choices=ROL_CHOICES, default='USER')
    estadio          = models.CharField(max_length=20, choices=ESTADIO_CHOICES, blank=True, null=True)
    tipo_documento   = models.CharField(max_length=5,  choices=TIPO_DOC_CHOICES, blank=True)
    numero_documento = models.CharField(max_length=15, blank=True)
    fecha_nacimiento = models.DateField(
        null=True, blank=True,
        validators=[validar_fecha_nacimiento]
    )
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name        = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.rol})"

    def es_paciente(self):
        return self.rol == 'PACIENTE'

    def es_admin(self):
        return self.is_staff or self.is_superuser