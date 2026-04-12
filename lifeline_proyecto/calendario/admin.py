from django.contrib import admin
from .models import CitaMedica

@admin.register(CitaMedica)
class CitaAdmin(admin.ModelAdmin):
    list_display  = ('titulo','tipo','fecha','hora','estado','usuario')
    list_filter   = ('tipo','estado')
    search_fields = ('titulo','usuario__username')
    ordering      = ('fecha','hora')