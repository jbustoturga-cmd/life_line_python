# productos/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Configuración para gestionar categorías en el panel admin."""
    list_display  = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering      = ('nombre',)
#admin.py

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración avanzada para Productos.
    Incluye alertas visuales de stock y filtros por uso recomendado.
    """

    # Columnas visibles en la lista (Mezcla Fase 2 y 3)
    list_display = (
        'nombre', 
        'categoria', 
        'precio_final', 
        'cantidad', 
        'alerta_stock',  # Método personalizado abajo
        'estado', 
        'fecha_creacion'
    )

    # Filtros laterales (Incluye el nuevo campo uso_recomendado de Fase 3)
    list_filter = ('estado', 'categoria', 'uso_recomendado')

    # Barra de búsqueda (Eliminé 'categoria' porque ahora es un objeto, no un texto)
    search_fields = ('nombre', 'descripcion')

    # Orden por defecto (Más reciente primero)
    ordering = ('-fecha_creacion',)

    # Edición rápida desde la tabla
    list_editable = ('estado', 'cantidad')

    # --- Métodos de visualización personalizada ---

    def alerta_stock(self, obj):
        """Muestra etiquetas de colores según el inventario."""
        if obj.cantidad == 0:
            return format_html(
                '<span style="color:#d9534f; font-weight:bold;">❌ Agotado</span>'
            )
        # Nota: stock_bajo es una @property en el modelo
        elif obj.stock_bajo:
            return format_html(
                '<span style="color:#f0ad4e; font-weight:bold;">⚠ Bajo</span>'
            )
        return format_html(
            '<span style="color:#5cb85c;">✔ OK</span>'
        )
    
    alerta_stock.short_description = 'Estado Stock'