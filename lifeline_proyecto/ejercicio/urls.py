# ejercicio/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',           views.vista_ejercicio,        name='ejercicio'),
    path('completar/', views.vista_completar_sesion,  name='completar_sesion'),
] #urls.py