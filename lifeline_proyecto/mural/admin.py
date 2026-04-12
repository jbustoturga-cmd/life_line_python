# mural/admin.py
# lara - Registro de los modelos del mural en el panel admin

from django.contrib import admin
from .models import Publicacion, Comentario

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ('autor', 'tipo', 'fecha_creacion', 'total_likes')
    list_filter  = ('tipo', 'fecha_creacion')
    search_fields = ('contenido', 'autor__username')
    readonly_fields = ('fecha_creacion',)

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'publicacion', 'fecha_creacion')
    search_fields = ('contenido', 'autor__username')
    readonly_fields = ('fecha_creacion',)