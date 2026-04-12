# usuarios/admin.py
# LEIDY - Registro del modelo Usuario en el panel de administración de Django

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
#admin.py

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración del panel admin para el modelo Usuario.
    Permite ver y gestionar usuarios desde /admin/
    """

    # Columnas que se muestran en la lista de usuarios
    list_display = ('username', 'email', 'rol', 'estadio', 'is_active', 'date_joined')

    # Filtros en la barra lateral
    list_filter = ('rol', 'estadio', 'is_active', 'is_staff')

    # Barra de búsqueda
    search_fields = ('username', 'email', 'numero_documento')

    # Orden por defecto
    ordering = ('-date_joined',)

    # Campos que se muestran al editar un usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información LifeLine', {
            'fields': (
                'rol', 'estadio', 'tipo_documento',
                'numero_documento', 'fecha_nacimiento'
            )
        }),
    )

    # Campos al crear un nuevo usuario desde el admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información LifeLine', {
            'fields': (
                'email', 'rol', 'estadio', 'tipo_documento',
                'numero_documento', 'fecha_nacimiento'
            )
        }),
    )