# nutricion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',          views.vista_nutricion,         name='nutricion'),
    path('registrar/',views.vista_registrar_sintoma,  name='registrar_sintoma'),
]