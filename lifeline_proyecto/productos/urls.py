# productos/urls.py — ACTUALIZADO
from django.urls import path
from . import views
#urls.py
urlpatterns = [
    # CRUD admin
    path('',                              views.vista_lista_productos,  name='lista_productos'),
    path('nuevo/',                        views.vista_nuevo_producto,   name='nuevo_producto'),
    path('editar/<int:producto_id>/',     views.vista_editar_producto,  name='editar_producto'),
    path('eliminar/<int:producto_id>/',   views.vista_eliminar_producto,name='eliminar_producto'),
    path('detalle/<int:producto_id>/',    views.vista_detalle_producto, name='detalle_producto'),

    # Categorías
    path('categorias/',                   views.vista_lista_categorias, name='lista_categorias'),
    path('categorias/nueva/',             views.vista_nueva_categoria,  name='nueva_categoria'),

    # Tienda pública
    path('tienda/',                       views.vista_tienda,           name='tienda'),
    path('tienda/detalle/<int:producto_id>/', views.vista_detalle_tienda, name='detalle_tienda'),  # ✅ NUEVO

    # Carrito
    path('tienda/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('tienda/carrito/',                   views.ver_carrito,         name='ver_carrito'),
    path('tienda/carrito/actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('tienda/carrito/vaciar/',            views.vaciar_carrito,      name='vaciar_carrito'),
]