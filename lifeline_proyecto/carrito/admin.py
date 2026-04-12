# carrito/admin.py
# LEIDY - Registro del carrito en el panel admin

from django.contrib import admin
from .models import CarritoItem


@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'subtotal', 'fecha_agregado')
    list_filter = ('usuario',)
    search_fields = ('usuario__username', 'producto__nombre')
    ordering = ('-fecha_agregado',)