from django.contrib import admin
from .models import Alarma, HistorialDosis

@admin.register(Alarma)
class AlarmaAdmin(admin.ModelAdmin):
    list_display = ('medicamento','usuario','hora_toma','frecuencia','activa')
    list_filter  = ('activa','frecuencia')
    search_fields= ('medicamento','usuario__username')

@admin.register(HistorialDosis)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('alarma','estado','fecha','hora')
    list_filter  = ('estado','fecha')
    #admin.py