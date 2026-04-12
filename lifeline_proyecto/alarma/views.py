# alarma/views.py — FASE 3
# KAROL — Vistas de alarmas de medicación

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Alarma, HistorialDosis
from .forms import FormularioAlarma, FormularioRegistrarDosis

#views.py
@login_required
def vista_alarmas(request):
    """Página principal de alarmas: activas, pendientes e historial."""
    alarmas_activas = Alarma.objects.filter(
        usuario=request.user, activa=True
    ).order_by('hora_toma')

    historial = HistorialDosis.objects.filter(
        alarma__usuario=request.user
    ).select_related('alarma')[:20]

    # Alarmas cuya hora ya pasó hoy y no tienen registro de hoy
    ahora = timezone.now().time()
    hoy   = timezone.now().date()

    pendientes = []
    for alarma in alarmas_activas:
        ya_registrada = HistorialDosis.objects.filter(
            alarma=alarma, fecha=hoy
        ).exists()
        if alarma.hora_toma < ahora and not ya_registrada:
            pendientes.append(alarma)

    return render(request, 'alarma/alarma.html', {
        'alarmas_activas': alarmas_activas,
        'pendientes': pendientes,
        'historial': historial,
    })


@login_required
def vista_nueva_alarma(request):
    if request.method == 'POST':
        formulario = FormularioAlarma(request.POST)
        if formulario.is_valid():
            alarma = formulario.save(commit=False)
            alarma.usuario = request.user
            alarma.save()
            messages.success(request, f'Alarma para "{alarma.medicamento}" creada.')
            return redirect('alarmas')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        formulario = FormularioAlarma()
    return render(request, 'alarma/alarma.html', {
        'formulario': formulario, 'mostrar_modal': True
    })


@login_required
def vista_marcar_dosis(request, alarma_id):
    """Marcar una dosis como tomada, omitida o tarde."""
    alarma = get_object_or_404(Alarma, id=alarma_id, usuario=request.user)

    if request.method == 'POST':
        formulario = FormularioRegistrarDosis(request.POST)
        if formulario.is_valid():
            dosis = formulario.save(commit=False)
            dosis.alarma = alarma
            dosis.save()
            messages.success(request, f'Dosis de "{alarma.medicamento}" registrada.')
        return redirect('alarmas')
    return redirect('alarmas')


@login_required
def vista_eliminar_alarma(request, alarma_id):
    alarma = get_object_or_404(Alarma, id=alarma_id, usuario=request.user)
    if request.method == 'POST':
        nombre = alarma.medicamento
        alarma.delete()
        messages.success(request, f'Alarma de "{nombre}" eliminada.')
    return redirect('alarmas')
