from django.contrib import admin
from .models import SesionEjercicio
#admin.py
@admin.register(SesionEjercicio)
class SesionAdmin(admin.ModelAdmin):
    list_display = ('usuario','nivel_energia','duracion_min','completada','fecha')
    list_filter  = ('nivel_energia','completada')