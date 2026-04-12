# carrito/models.py — FASE 3
# LEIDY — CarritoItem + Pedido para seguimiento de envíos

from django.db import models
from django.conf import settings
from productos.models import Producto
import uuid
#models.py

class CarritoItem(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrito_items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='carrito_items'
    )
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item del carrito'
        verbose_name_plural = 'Items del carrito'
        unique_together = ('usuario', 'producto')

    def __str__(self):
        return f"{self.usuario.username} — {self.producto.nombre} x{self.cantidad}"

    def subtotal(self):
        return self.producto.precio_final * self.cantidad


class Pedido(models.Model):
    """
    NUEVO FASE 3 — Representa un pedido realizado por un usuario.
    Sirve para el módulo de seguimiento de envíos (envios.html).
    """
    ESTADO_CHOICES = [
        ('pendiente',   'Pendiente'),
        ('procesando',  'Procesando'),
        ('enviado',     'Enviado'),
        ('en_transito', 'En Tránsito'),
        ('entregado',   'Entregado'),
        ('cancelado',   'Cancelado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    # Código de seguimiento único — se genera automáticamente
    numero_seguimiento = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Número de seguimiento'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado del pedido'
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True, verbose_name='Fecha del pedido')
    fecha_estimada_entrega = models.DateField(
        null=True, blank=True, verbose_name='Entrega estimada'
    )
    total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name='Total'
    )
    direccion_envio = models.TextField(blank=True, verbose_name='Dirección de envío')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']

    def save(self, *args, **kwargs):
        # Generar código de seguimiento automáticamente si no tiene
        if not self.numero_seguimiento:
            self.numero_seguimiento = 'LL-' + str(uuid.uuid4()).upper()[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido {self.numero_seguimiento} — {self.usuario.username}"


class ItemPedido(models.Model):
    """Detalle de cada producto dentro de un pedido."""
    pedido   = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio   = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.precio * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"