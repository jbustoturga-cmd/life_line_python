# nutricion/admin.py
from django.contrib import admin
from .models import PlanNutricional, SugerenciaRapida, RegistroNutricional

@admin.register(PlanNutricional)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('tratamiento', 'descripcion')

@admin.register(SugerenciaRapida)
class SugerenciaAdmin(admin.ModelAdmin):
    list_display = ('sintoma', 'sugerencia')
    list_filter  = ('sintoma',)

@admin.register(RegistroNutricional)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'sintoma', 'fecha')
    list_filter  = ('sintoma', 'fecha')
    ordering     = ('-fecha',)