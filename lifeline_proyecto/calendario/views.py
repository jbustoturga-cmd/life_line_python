# calendario/views.py — FASE 3
# LEIDY

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CitaMedica
from .forms import FormularioCita


@login_required
def vista_calendario(request):
    citas_proximas = CitaMedica.objects.filter(
        usuario=request.user, estado='pendiente'
    ).order_by('fecha', 'hora')

    historial = CitaMedica.objects.filter(
        usuario=request.user, estado__in=['completada', 'cancelada']
    ).order_by('-fecha')[:10]

    if request.method == 'POST':
        formulario = FormularioCita(request.POST)
        if formulario.is_valid():
            cita = formulario.save(commit=False)
            cita.usuario = request.user
            cita.save()
            messages.success(request, f'Cita "{cita.titulo}" agendada para el {cita.fecha}.')
            return redirect('calendario')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        formulario = FormularioCita()

    return render(request, 'calendario/calendario.html', {
        'citas_proximas': citas_proximas,
        'historial': historial,
        'formulario': formulario,
    })


@login_required
def vista_completar_cita(request, cita_id):
    cita = get_object_or_404(CitaMedica, id=cita_id, usuario=request.user)
    if request.method == 'POST':
        cita.estado = 'completada'
        cita.save()
        messages.success(request, f'Cita "{cita.titulo}" marcada como completada.')
    return redirect('calendario')


@login_required
def vista_cancelar_cita(request, cita_id):
    cita = get_object_or_404(CitaMedica, id=cita_id, usuario=request.user)
    if request.method == 'POST':
        cita.estado = 'cancelada'
        cita.save()
        messages.success(request, f'Cita "{cita.titulo}" cancelada.')
    return redirect('calendario')


@login_required
def vista_eliminar_cita(request, cita_id):
    cita = get_object_or_404(CitaMedica, id=cita_id, usuario=request.user)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada.')
    return redirect('calendario')