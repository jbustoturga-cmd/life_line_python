# nutricion/views.py — FASE 3
# JHOAN — Vistas del módulo de nutrición oncológica

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PlanNutricional, SugerenciaRapida, RegistroNutricional

# Sugerencias predefinidas (no requieren base de datos)
SUGERENCIAS_PREDEFINIDAS = {
    'nauseas': {
        'titulo':    'Para Náuseas y Vómitos',
        'emoji':     '🤢',
        'alimentos': [
            '🥣 Sopa de caldo suave (baja en grasa)',
            '🍞 Galletas saladas o tostadas simples',
            '🫖 Té de jengibre (caliente o frío)',
            '🍋 Agua con limón fría a pequeños sorbos',
            '🍚 Arroz blanco sin condimentos',
        ],
        'evitar': ['Alimentos fritos o grasosos', 'Comidas con olores fuertes', 'Lácteos enteros'],
        'consejo': 'Come porciones muy pequeñas cada 2-3 horas. Evita acostarte justo después de comer.',
    },
    'fatiga': {
        'titulo':    'Para Fatiga y Pérdida de Apetito',
        'emoji':     '😴',
        'alimentos': [
            '🥤 Batidos nutritivos con frutas y proteína',
            '🥑 Aguacate (alto en calorías saludables)',
            '🥜 Mantequilla de maní en tostadas',
            '🧀 Queso fresco en pequeñas porciones',
            '🍌 Banano maduro (fácil de digerir)',
        ],
        'evitar': ['Saltarse comidas', 'Alimentos bajos en calorías', 'Bebidas con cafeína en exceso'],
        'consejo': 'Prioriza alimentos densos en nutrientes. Come aunque no tengas hambre.',
    },
    'diarrea': {
        'titulo':    'Para Diarrea o Estreñimiento',
        'emoji':     '🌿',
        'alimentos': [
            '🍚 Arroz blanco cocido',
            '🍌 Banano maduro',
            '🍎 Compota de manzana sin azúcar',
            '🍞 Pan blanco o galletas de soda',
            '💧 Agua y suero oral para hidratación',
        ],
        'evitar': ['Lácteos', 'Frutas con semillas', 'Alimentos picantes', 'Cafeína y alcohol'],
        'consejo': 'Hidrátate constantemente. Si persiste, consulta a tu médico.',
    },
    'boca_seca': {
        'titulo':    'Para Boca Seca y Llagas',
        'emoji':     '💧',
        'alimentos': [
            '🍦 Helados o paletas de frutas naturales',
            '🥤 Batidos suaves y líquidos fríos',
            '🍲 Sopas tibias con consistencia suave',
            '🍓 Frutas blandas: melón, sandía, durazno',
            '🧊 Cubitos de hielo para chupar',
        ],
        'evitar': ['Alimentos ácidos o picantes', 'Comidas muy calientes', 'Frituras crujientes'],
        'consejo': 'Mantén la boca húmeda con agua. Usa enjuague bucal sin alcohol.',
    },
    'cambio_gusto': {
        'titulo':    'Para Cambios en el Gusto',
        'emoji':     '👅',
        'alimentos': [
            '🌿 Hierbas frescas para realzar el sabor',
            '🍋 Limón o naranja para neutralizar sabor metálico',
            '🍗 Pollo frío o a temperatura ambiente',
            '🥗 Ensaladas frescas con aderezos suaves',
            '🍓 Frutas frescas de sabor suave',
        ],
        'evitar': ['Cubiertos de metal (usar plástico si hay sabor metálico)', 'Carnes rojas si producen sabor extraño'],
        'consejo': 'Experimenta con temperaturas y texturas. Lo frío suele tener menos sabor fuerte.',
    },
    'general': {
        'titulo':    'Recomendaciones Generales',
        'emoji':     '🥗',
        'alimentos': [
            '🥦 Verduras cocidas al vapor',
            '🐟 Pescado a la plancha o al vapor',
            '🫘 Legumbres bien cocidas',
            '🌾 Cereales integrales en porciones moderadas',
            '🫐 Frutas antioxidantes: arándanos, fresas',
        ],
        'evitar': ['Alcohol', 'Azúcares refinados en exceso', 'Ultraprocesados'],
        'consejo': 'Mantén una dieta variada y consulta siempre con tu nutricionista.',
    },
}

PLANES_TRATAMIENTO = {
    'quimioterapia': {
        'titulo': 'Plan para Quimioterapia',
        'descripcion': 'Enfocado en mantener la fuerza y manejar los efectos secundarios más comunes.',
        'semana': [
            {'dia': 'Lunes', 'desayuno': 'Avena con banano', 'almuerzo': 'Sopa de pollo con arroz', 'cena': 'Yogur y galletas'},
            {'dia': 'Martes', 'desayuno': 'Batido de frutas', 'almuerzo': 'Pollo a la plancha con puré', 'cena': 'Compota de manzana'},
            {'dia': 'Miércoles', 'desayuno': 'Tostadas con mantequilla de maní', 'almuerzo': 'Pescado al vapor con arroz', 'cena': 'Caldo de verduras'},
        ],
    },
    'radioterapia': {
        'titulo': 'Plan para Radioterapia',
        'descripcion': 'Alimentos que favorecen la recuperación tisular y reducen la inflamación.',
        'semana': [
            {'dia': 'Lunes', 'desayuno': 'Jugo natural + tostada', 'almuerzo': 'Lentejas suaves', 'cena': 'Sopa de verduras'},
            {'dia': 'Martes', 'desayuno': 'Yogur con frutas blandas', 'almuerzo': 'Arroz con pollo desmechado', 'cena': 'Gelatina natural'},
        ],
    },
    'hormonoterapia': {
        'titulo': 'Plan para Hormonoterapia',
        'descripcion': 'Énfasis en calcio, vitamina D y control de peso saludable.',
        'semana': [
            {'dia': 'Lunes', 'desayuno': 'Leche descremada + cereal', 'almuerzo': 'Salmón con ensalada', 'cena': 'Fruta fresca'},
        ],
    },
    'general': {
        'titulo': 'Plan General',
        'descripcion': 'Alimentación equilibrada y variada para mantener la energía.',
        'semana': [
            {'dia': 'Lunes', 'desayuno': 'Huevo + fruta', 'almuerzo': 'Arroz, proteína y ensalada', 'cena': 'Sopa suave'},
        ],
    },
}


@login_required
def vista_nutricion(request):
    """Página principal de nutrición oncológica."""
    sintoma_seleccionado  = request.GET.get('sintoma', '')
    tratamiento_seleccionado = request.GET.get('tratamiento', '')

    sugerencia = None
    plan       = None

    if sintoma_seleccionado and sintoma_seleccionado in SUGERENCIAS_PREDEFINIDAS:
        sugerencia = SUGERENCIAS_PREDEFINIDAS[sintoma_seleccionado]

    if tratamiento_seleccionado and tratamiento_seleccionado in PLANES_TRATAMIENTO:
        plan = PLANES_TRATAMIENTO[tratamiento_seleccionado]

    return render(request, 'nutricion/nutricion.html', {
        'sintomas':               SUGERENCIAS_PREDEFINIDAS,
        'planes':                 PLANES_TRATAMIENTO,
        'sintoma_seleccionado':   sintoma_seleccionado,
        'tratamiento_seleccionado': tratamiento_seleccionado,
        'sugerencia':             sugerencia,
        'plan':                   plan,
    })


@login_required
def vista_registrar_sintoma(request):
    """Registra el síntoma del día del usuario."""
    if request.method == 'POST':
        sintoma = request.POST.get('sintoma', 'general')
        nota    = request.POST.get('nota', '').strip()
        RegistroNutricional.objects.create(
            usuario=request.user,
            sintoma=sintoma,
            nota=nota,
        )
        messages.success(request, '¡Registro guardado correctamente!')
    return redirect('nutricion')