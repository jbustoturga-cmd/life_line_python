# lifeline/urls.py
# JHOAN - URLs principales del proyecto LifeLine - FASE 2
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
#urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('productos/', include('productos.urls')),
    path('carrito/', include('carrito.urls')),
    path('reportes/', include('reportes.urls')),
    path('mural/', include('mural.urls')),
    path('alarma/', include('alarma.urls')),
    path('calendario/', include('calendario.urls')),
    path('ejercicio/', include('ejercicio.urls')),
    path('nutricion/',  include('nutricion.urls')),
]

# Archivos media (solo una vez)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error 404 personalizado
handler404 = 'usuarios.views.error_404'