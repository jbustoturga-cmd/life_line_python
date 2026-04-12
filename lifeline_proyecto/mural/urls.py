# ============================================================
#  urls_mural.py — Agrega estas rutas a tu urls.py principal
#  o al urls.py de la app mural
# ============================================================

from django.urls import path
from . import views   # Ajusta el import según tu estructura de apps

# Une todas tus rutas en esta única variable:
urlpatterns = [
    # Mural principal
    path('mural/', views.vista_mural, name='mural'),
#urls.py
    # Publicaciones
    path('mural/crear/', views.crear_publicacion, name='crear_publicacion'),
    path('mural/eliminar/<int:pub_id>/', views.eliminar_publicacion, name='eliminar_publicacion'),
    path('mural/like/<int:pub_id>/', views.dar_like, name='dar_like'),

    # Comentarios
    path('mural/comentar/<int:pub_id>/', views.agregar_comentario, name='agregar_comentario'),
    path('mural/comentario/eliminar/<int:com_id>/', views.eliminar_comentario, name='eliminar_comentario'),

    # Perfil
    path('perfil/editar/', views.vista_editar_perfil, name='editar_perfil'),
]