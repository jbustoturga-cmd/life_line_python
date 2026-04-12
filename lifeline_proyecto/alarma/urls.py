# alarma/urls.py — FASE 3
from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.vista_alarmas,        name='alarmas'),
    path('nueva/',                    views.vista_nueva_alarma,   name='nueva_alarma'),
    path('marcar/<int:alarma_id>/',   views.vista_marcar_dosis,   name='marcar_dosis'),
    path('eliminar/<int:alarma_id>/', views.vista_eliminar_alarma,name='eliminar_alarma'),
]