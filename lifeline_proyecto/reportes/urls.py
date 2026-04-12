# reportes/urls.py — ACTUALIZADO
from django.urls import path
from . import views

urlpatterns = [
    path('clientes/',          views.vista_clientes,           name='clientes'),
    path('clientes/pdf/',      views.vista_reporte_pdf,        name='reporte_pdf'),
    path('productos/',         views.vista_productos_reporte,  name='reporte_productos'),
    path('productos/pdf/',     views.vista_productos_pdf,      name='reporte_productos_pdf'),  # ✅ NUEVO
    path('stock/',             views.vista_reporte_stock,      name='reporte_stock'),
    path('medicamentos/',      views.vista_reporte_medicamentos, name='reporte_medicamentos'),
    path('emocional/',         views.vista_reporte_emocional,  name='reporte_emocional'),
    path('tienda/',            views.vista_reporte_tienda,     name='reporte_tienda'),
]