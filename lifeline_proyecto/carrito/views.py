# carrito/views.py — ACTUALIZADO
# LEIDY — Carrito + Pasarela de pagos con dirección y validaciones

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CarritoItem, Pedido, ItemPedido
from productos.models import Producto
from django.utils import timezone
import datetime
import re
from django.http import JsonResponse


# ── Helpers ────────────────────────────────────────────────────────────────

def _get_items(request):
    return CarritoItem.objects.filter(usuario=request.user).select_related('producto')


# ── Carrito ────────────────────────────────────────────────────────────────

@login_required
def ver_carrito(request):
    items = _get_items(request)
    total = sum(item.subtotal() for item in items)
    return render(request, 'carrito/carrito.html', {'items': items, 'total': total})

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, estado=True)
    es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if producto.esta_vencido:
        if es_ajax:
            return JsonResponse({'ok': False, 'error': f'"{producto.nombre}" está vencido.'})
        messages.error(request, f'"{producto.nombre}" está vencido.')
        return redirect('tienda')

    if not producto.tiene_stock:
        if es_ajax:
            return JsonResponse({'ok': False, 'error': f'"{producto.nombre}" está agotado.'})
        messages.error(request, f'"{producto.nombre}" está agotado.')
        return redirect('tienda')

    item, creado = CarritoItem.objects.get_or_create(
        usuario=request.user, producto=producto, defaults={'cantidad': 1}
    )
    if not creado:
        if item.cantidad >= producto.cantidad:
            if es_ajax:
                return JsonResponse({'ok': False, 'error': 'No hay más stock.'})
            messages.error(request, 'No hay más stock.')
            return redirect('tienda')
        item.cantidad += 1
        item.save()

    if es_ajax:
        from django.db.models import Sum
        total = CarritoItem.objects.filter(
            usuario=request.user
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        return JsonResponse({'ok': True, 'total': total})

    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return redirect(request.POST.get('next', 'tienda'))


# carrito/context_processors.py
def carrito_count(request):
    if request.user.is_authenticated:
        try:
            from .models import CarritoItem
            count = CarritoItem.objects.filter(
                carrito__usuario=request.user
            ).aggregate(
                total=__import__('django.db.models', fromlist=['Sum']).Sum('cantidad')
            )['total'] or 0
        except Exception:
            count = 0
    else:
        count = 0
    return {'carrito_count': count}
@login_required
def actualizar_carrito(request, item_id):
    item   = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    accion = request.POST.get('accion')

    if accion == 'aumentar':
        if item.cantidad < item.producto.cantidad:
            item.cantidad += 1
            item.save()
        else:
            messages.error(request, 'No hay más stock disponible.')
    elif accion == 'disminuir':
        if item.cantidad > 1:
            item.cantidad -= 1
            item.save()
        else:
            item.delete()
    elif accion == 'eliminar':
        item.delete()

    return redirect('ver_carrito')


@login_required
def vaciar_carrito(request):
    CarritoItem.objects.filter(usuario=request.user).delete()
    messages.success(request, 'Carrito vaciado.')
    return redirect('ver_carrito')


# ── PASARELA DE PAGOS ─────────────────────────────────────────────────────
@login_required
def vista_pago(request):
    items = _get_items(request)
    if not items.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('ver_carrito')

    total = sum(item.subtotal() for item in items)
    errores = {}
    datos_form = {}

    if request.method == 'POST':
        # Campos de dirección
        nombre_completo = request.POST.get('nombre_completo', '').strip()
        telefono        = request.POST.get('telefono', '').strip()
        direccion       = request.POST.get('direccion', '').strip()
        ciudad          = request.POST.get('ciudad', '').strip()
        departamento    = request.POST.get('departamento', '').strip()
        codigo_postal   = request.POST.get('codigo_postal', '').strip()

        # Campos de pago (simulados)
        numero_tarjeta  = request.POST.get('numero_tarjeta', '').replace(' ', '').strip()
        nombre_tarjeta  = request.POST.get('nombre_tarjeta', '').strip()
        fecha_exp       = request.POST.get('fecha_exp', '').strip()
        cvv             = request.POST.get('cvv', '').strip()

        # ── Validaciones de dirección ──────────────────────────────────────
        if not nombre_completo or len(nombre_completo) < 3:
            errores['nombre_completo'] = 'Ingresa tu nombre completo (mínimo 3 caracteres).'
        elif not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]', nombre_completo):
            errores['nombre_completo'] = 'El nombre debe contener letras.'

        if not telefono:
            errores['telefono'] = 'El teléfono es obligatorio.'
        elif not telefono.replace('+', '').replace(' ', '').isdigit():
            errores['telefono'] = 'El teléfono solo debe contener números.'
        elif len(re.sub(r'\D', '', telefono)) < 7:
            errores['telefono'] = 'El teléfono debe tener al menos 7 dígitos.'

        if not direccion or len(direccion) < 5:
            errores['direccion'] = 'Ingresa una dirección válida (mínimo 5 caracteres).'

        if not ciudad or len(ciudad) < 2:
            errores['ciudad'] = 'La ciudad es obligatoria.'

        if not departamento:
            errores['departamento'] = 'El departamento es obligatorio.'

        # ── Validaciones de tarjeta ────────────────────────────────────────
        if not numero_tarjeta:
            errores['numero_tarjeta'] = 'El número de tarjeta es obligatorio.'
        elif not numero_tarjeta.isdigit() or len(numero_tarjeta) not in [15, 16]:
            errores['numero_tarjeta'] = 'El número de tarjeta debe tener 15 o 16 dígitos.'

        if not nombre_tarjeta or len(nombre_tarjeta) < 3:
            errores['nombre_tarjeta'] = 'Ingresa el nombre como aparece en la tarjeta.'

        if not fecha_exp:
            errores['fecha_exp'] = 'La fecha de vencimiento es obligatoria.'
        elif not re.match(r'^\d{2}/\d{2}$', fecha_exp):
            errores['fecha_exp'] = 'Formato inválido. Usa MM/YY.'
        else:
            try:
                mes, anio = fecha_exp.split('/')
                mes  = int(mes)
                anio = int('20' + anio)
                hoy  = timezone.now().date()
                if mes < 1 or mes > 12:
                    errores['fecha_exp'] = 'El mes debe estar entre 01 y 12.'
                elif datetime.date(anio, mes, 1) < hoy.replace(day=1):
                    errores['fecha_exp'] = 'La tarjeta está vencida.'
            except (ValueError, OverflowError):
                errores['fecha_exp'] = 'Fecha de vencimiento inválida.'

        if not cvv:
            errores['cvv'] = 'El CVV es obligatorio.'
        elif not cvv.isdigit() or len(cvv) not in [3, 4]:
            errores['cvv'] = 'El CVV debe tener 3 o 4 dígitos.'

        if not errores:
            # Guardar datos de dirección en sesión para usar en confirmación
            request.session['datos_pago'] = {
                'nombre_completo': nombre_completo,
                'telefono':        telefono,
                'direccion':       direccion,
                'ciudad':          ciudad,
                'departamento':    departamento,
                'codigo_postal':   codigo_postal,
            }
            return redirect('confirmar_pago')

        # Repoblar campos si hay errores
        datos_form = {
            'nombre_completo': nombre_completo, 'telefono': telefono,
            'direccion': direccion, 'ciudad': ciudad,
            'departamento': departamento, 'codigo_postal': codigo_postal,
            'nombre_tarjeta': nombre_tarjeta, 'fecha_exp': fecha_exp,
        }

    return render(request, 'carrito/pago.html', {
        'items': items, 'total': total,
        'errores': errores, 'datos_form': datos_form,
    })


@login_required
def confirmar_pago(request):
    """
    Confirma el pedido: crea el Pedido en la BD, vacía el carrito
    y muestra la pantalla de éxito con el número de seguimiento.
    """
    datos = request.session.get('datos_pago')
    if not datos:
        messages.error(request, 'No hay datos de pago. Intenta de nuevo.')
        return redirect('ver_carrito')

    items = _get_items(request)
    if not items.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('ver_carrito')

    total         = sum(item.subtotal() for item in items)
    fecha_entrega = timezone.now().date() + datetime.timedelta(days=7)

    direccion_completa = (
        f"{datos['direccion']}, {datos['ciudad']}, "
        f"{datos['departamento']}"
        + (f" ({datos['codigo_postal']})" if datos.get('codigo_postal') else '')
    )

    pedido = Pedido.objects.create(
        usuario=request.user,
        total=total,
        direccion_envio=direccion_completa,
        fecha_estimada_entrega=fecha_entrega,
    )
    for item in items:
        ItemPedido.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio=item.producto.precio_final,
        )

    # Vaciar carrito y datos de sesión
    items.delete()
    if 'datos_pago' in request.session:
        del request.session['datos_pago']

    return render(request, 'carrito/pago_exitoso.html', {
        'pedido':      pedido,
        'datos':       datos,
        'fecha_entrega': fecha_entrega,
    })


# ── Mis pedidos / envíos ───────────────────────────────────────────────────

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('items__producto')
    return render(request, 'carrito/envios.html', {
        'pedidos': pedidos, 'seccion': 'mis_pedidos'
    })


@login_required
def seguimiento_envio(request):
    codigo = request.GET.get('codigo', '').strip().upper()
    pedido = None
    no_encontrado = False
    if codigo:
        try:
            pedido = Pedido.objects.get(numero_seguimiento=codigo)
        except Pedido.DoesNotExist:
            no_encontrado = True
    return render(request, 'carrito/envios.html', {
        'codigo': codigo, 'pedido': pedido,
        'no_encontrado': no_encontrado, 'seccion': 'seguimiento'
    })


@login_required
def facturas(request):
    pedidos = Pedido.objects.filter(
        usuario=request.user, estado='entregado'
    ).prefetch_related('items__producto')
    return render(request, 'carrito/envios.html', {
        'pedidos': pedidos, 'seccion': 'facturas'
    })