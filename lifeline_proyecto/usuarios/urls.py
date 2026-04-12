# usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Página pública de inicio
    path('', views.vista_logi, name='logi'),
    path('registro/', views.vista_registro, name='registro'),
    path('login/', views.vista_login, name='login'),
    path('logout/', views.vista_logout, name='logout'),
    path('home/', views.vista_home, name='home'),
    path('perfil/', views.vista_perfil, name='perfil'),
    path('registro-txt/', views.vista_registro_txt, name='registro_txt'),
    path('contactanos/', views.vista_contactanos, name='contactanos'),
    path('dashboard/', views.vista_dashboard, name='dashboard'),

    # --- NUEVO FASE 2: CRUD usuarios (MÉTELO DENTRO DE LOS CORCHETES) ---
    path('admin-usuarios/', views.vista_lista_usuarios, name='lista_usuarios'),
    path('admin-usuarios/crear/', views.vista_crear_usuario, name='crear_usuario'),
    path('admin-usuarios/editar/<int:usuario_id>/', views.vista_editar_usuario, name='editar_usuario'),
    path('admin-usuarios/eliminar/<int:usuario_id>/', views.vista_eliminar_usuario, name='eliminar_usuario'),
    path('admin-usuarios/', views.vista_lista_usuarios, name='lista_usuarios'),

    
] # <--- Asegúrate de que el corchete de cierre esté al final de todo