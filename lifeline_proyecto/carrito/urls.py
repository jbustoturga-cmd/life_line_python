# carrito/urls.py — ACTUALIZADO
from django.urls import path
from . import views

urlpatterns = [
    path('',                             views.ver_carrito,       name='ver_carrito'),
    path('agregar/<int:producto_id>/',   views.agregar_al_carrito,name='agregar_carrito'),
    path('actualizar/<int:item_id>/',    views.actualizar_carrito, name='actualizar_carrito'),
    path('vaciar/',                      views.vaciar_carrito,    name='vaciar_carrito'),

    # ✅ Pasarela de pagos
    path('pago/',                        views.vista_pago,        name='pago'),
    path('pago/confirmar/',              views.confirmar_pago,    name='confirmar_pago'),

    # Pedidos y envíos
    path('pedidos/',                     views.mis_pedidos,       name='mis_pedidos'),
    path('seguimiento/',                 views.seguimiento_envio, name='seguimiento_envio'),
    path('facturas/',                    views.facturas,          name='facturas'),
]