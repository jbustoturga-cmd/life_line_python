# calendario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                           views.vista_calendario,      name='calendario'),
    path('completar/<int:cita_id>/',   views.vista_completar_cita,  name='completar_cita'),
    path('cancelar/<int:cita_id>/',    views.vista_cancelar_cita,   name='cancelar_cita'),
    path('eliminar/<int:cita_id>/',    views.vista_eliminar_cita,   name='eliminar_cita'),
]