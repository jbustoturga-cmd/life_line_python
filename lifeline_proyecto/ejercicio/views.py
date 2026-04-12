# ejercicio/views.py — FASE 3
# KAROL

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SesionEjercicio

# Rutinas predefinidas por nivel de energía
RUTINAS = {
    'alta': {
        'titulo':      'Alta Energía — Resistencia',
        'descripcion': 'Para días en que te sientes fuerte. Mejora la resistencia cardiovascular.',
        'duracion':    30,
        'ejercicios':  ['Caminata rápida 10 min', 'Sentadillas suaves x10', 'Estiramiento de brazos x5', 'Respiración profunda 5 min'],
    },
    'media': {
        'titulo':      'Energía Media — Movilidad y Flexibilidad',
        'descripcion': 'Rutina de estiramientos y movimientos en silla. Alivia la rigidez articular post-quimio.',
        'duracion':    15,
        'ejercicios':  ['Rotaciones de cuello x5', 'Estiramiento de hombros', 'Rotaciones de tobillo en silla', 'Respiración diafragmática 5 min'],
    },
    'dificil': {
        'titulo':      'Día Difícil — Respiración y Relajación',
        'descripcion': 'Foco en respiración y relajación. Movimientos mínimos y conscientes.',
        'duracion':    10,
        'ejercicios':  ['Respiración 4-7-8 x3', 'Relajación de manos', 'Movimiento suave de muñecas', 'Meditación guiada 5 min'],
    },
}


@login_required
def vista_ejercicio(request):
    nivel = request.GET.get('nivel', 'media')
    if nivel not in RUTINAS:
        nivel = 'media'

    rutina   = RUTINAS[nivel]
    historial = SesionEjercicio.objects.filter(usuario=request.user)[:10]

    return render(request, 'ejercicio/ejercicio.html', {
        'nivel':    nivel,
        'rutina':   rutina,
        'historial': historial,
    })


@login_required
def vista_completar_sesion(request):
    if request.method == 'POST':
        nivel = request.POST.get('nivel', 'media')
        nota  = request.POST.get('nota', '').strip()
        rutina = RUTINAS.get(nivel, RUTINAS['media'])

        SesionEjercicio.objects.create(
            usuario=request.user,
            nivel_energia=nivel,
            duracion_min=rutina['duracion'],
            completada=True,
            nota=nota,
        )
        messages.success(request, f'¡Sesión de {rutina["titulo"]} completada! ¡Excelente trabajo!')
    return redirect('ejercicio')