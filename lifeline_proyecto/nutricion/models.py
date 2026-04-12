# nutricion/models.py — FASE 3
# JHOAN — Modelos del módulo de nutrición oncológica

from django.db import models
from django.conf import settings

#models.py
class PlanNutricional(models.Model):
    """Plan semanal según el tipo de tratamiento."""

    TRATAMIENTO_CHOICES = [
        ('quimioterapia',  'Quimioterapia'),
        ('radioterapia',   'Radioterapia'),
        ('hormonoterapia', 'Hormonoterapia'),
        ('cirugia',        'Post-cirugía'),
        ('general',        'General'),
    ]

    tratamiento   = models.CharField(max_length=20, choices=TRATAMIENTO_CHOICES, unique=True)
    descripcion   = models.TextField(verbose_name='Descripción del plan')
    recomendacion = models.TextField(verbose_name='Recomendaciones generales')

    class Meta:
        verbose_name = 'Plan Nutricional'
        verbose_name_plural = 'Planes Nutricionales'

    def __str__(self):
        return f"Plan — {self.get_tratamiento_display()}"


class SugerenciaRapida(models.Model):
    """Sugerencias de comida según el síntoma del usuario."""

    SINTOMA_CHOICES = [
        ('nauseas',         'Náuseas y vómitos'),
        ('fatiga',          'Fatiga / pérdida de apetito'),
        ('diarrea',         'Diarrea o estreñimiento'),
        ('boca_seca',       'Boca seca y llagas'),
        ('cambio_gusto',    'Cambios en el gusto'),
        ('general',         'General'),
    ]

    sintoma     = models.CharField(max_length=20, choices=SINTOMA_CHOICES)
    sugerencia  = models.TextField(verbose_name='Sugerencia de alimentos')
    alimentos   = models.TextField(verbose_name='Lista de alimentos recomendados',
                                   help_text='Uno por línea')

    class Meta:
        verbose_name = 'Sugerencia Rápida'
        verbose_name_plural = 'Sugerencias Rápidas'

    def __str__(self):
        return f"Sugerencia — {self.get_sintoma_display()}"

    def alimentos_lista(self):
        """Retorna los alimentos como lista Python."""
        return [a.strip() for a in self.alimentos.split('\n') if a.strip()]


class RegistroNutricional(models.Model):
    """Registro de seguimiento nutricional del usuario."""

    usuario     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='registros_nutricionales')
    sintoma     = models.CharField(max_length=20,
                                   choices=SugerenciaRapida.SINTOMA_CHOICES, default='general')
    nota        = models.TextField(blank=True, verbose_name='Nota del día')
    fecha       = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro Nutricional'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} — {self.fecha}"