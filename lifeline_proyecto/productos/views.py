# productos/views.py — ACTUALIZADO
# LEIDY — CRUD + tienda con filtro de categorías + vista de detalle completa

import os
import datetime
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Producto, Categoria
from .forms import FormularioProducto, FormularioCategoria


# ── CRUD ADMIN ────────────────────────────────────────────────────────────

@login_required
def vista_lista_productos(request):
    productos  = Producto.objects.all().select_related('categoria')
    from django.utils import timezone
    stock_bajo = productos.filter(cantidad__lt=5, estado=True)

    # ✅ Productos que vencen en los próximos 30 días
    hoy = timezone.now().date()
    limite = hoy + datetime.timedelta(days=30)
    proximos_vencer = productos.filter(
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=limite,
        estado=True
    )

    return render(request, 'productos/lista.html', {
        'productos':             productos,
        'stock_bajo':            stock_bajo,
        'total_stock_bajo':      stock_bajo.count(),
        'proximos_vencer':       proximos_vencer,
        'total_proximos_vencer': proximos_vencer.count(),
    })


@login_required
def vista_nuevo_producto(request):
    if request.method == 'POST':
        formulario = FormularioProducto(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, '¡Producto creado correctamente!')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        formulario = FormularioProducto()
    return render(request, 'productos/formulario.html', {
        'formulario': formulario, 'titulo': 'Nuevo Producto', 'producto': None
    })


@login_required
def vista_editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        formulario = FormularioProducto(request.POST, request.FILES, instance=producto)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, f'"{producto.nombre}" actualizado.')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        formulario = FormularioProducto(instance=producto)
    return render(request, 'productos/formulario.html', {
        'formulario': formulario, 'titulo': 'Editar Producto', 'producto': producto
    })


@login_required
def vista_eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        if producto.imagen and os.path.isfile(producto.imagen.path):
            os.remove(producto.imagen.path)
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'"{nombre}" eliminado.')
        return redirect('lista_productos')
    return render(request, 'productos/confirmar_eliminar.html', {'producto': producto})


@login_required
def vista_detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'productos/detalle.html', {'producto': producto})


# ── CATEGORÍAS ────────────────────────────────────────────────────────────

@login_required
def vista_lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'productos/categorias.html', {'categorias': categorias})


@login_required
def vista_nueva_categoria(request):
    if request.method == 'POST':
        formulario = FormularioCategoria(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, '¡Categoría creada!')
            return redirect('lista_categorias')
    else:
        formulario = FormularioCategoria()
    return render(request, 'productos/formulario_categoria.html', {
        'formulario': formulario, 'titulo': 'Nueva Categoría'
    })


# ── TIENDA PÚBLICA ────────────────────────────────────────────────────────

@login_required
def vista_tienda(request):
    """✅ Tienda con filtro de categorías funcional."""
    query            = request.GET.get('q', '').strip()
    categoria_id     = request.GET.get('categoria', '').strip()
    uso_filtro       = request.GET.get('uso', '').strip()

    productos = Producto.objects.filter(estado=True).select_related('categoria')

    if query:
        productos = productos.filter(nombre__icontains=query)
    if categoria_id:
        try:
            productos = productos.filter(categoria__id=int(categoria_id))
        except ValueError:
            pass
    if uso_filtro:
        productos = productos.filter(uso_recomendado=uso_filtro)

    categorias = Categoria.objects.all()

    return render(request, 'productos/tienda.html', {
        'productos':      productos,
        'query':          query,
        'categoria_id':   categoria_id,
        'uso_filtro':     uso_filtro,
        'categorias':     categorias,
        'uso_choices':    Producto.USO_CHOICES,
    })


@login_required
def vista_detalle_tienda(request, producto_id):
    """✅ Vista de detalle del producto en la tienda pública."""
    producto   = get_object_or_404(Producto, id=producto_id, estado=True)
    categorias = Categoria.objects.all()
    return render(request, 'productos/detalle_tienda.html', {
        'producto':   producto,
        'categorias': categorias,
    })


# ── CARRITO (sesión) ──────────────────────────────────────────────────────

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, estado=True)

    if producto.esta_vencido:
        messages.error(request, f'"{producto.nombre}" está vencido.')
        return redirect('tienda')
    if not producto.tiene_stock:
        messages.error(request, f'"{producto.nombre}" está agotado.')
        return redirect('tienda')

    carrito = request.session.get('carrito', {})
    str_id  = str(producto_id)
    cant    = carrito.get(str_id, 0)

    if cant >= producto.cantidad:
        messages.error(request, 'No hay más stock disponible.')
        return redirect('tienda')

    carrito[str_id]          = cant + 1
    request.session['carrito'] = carrito
    request.session.modified   = True

    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    # Si viene de detalle, volver a la tienda
    next_url = request.POST.get('next', 'tienda')
    return redirect(next_url)


@login_required
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    items   = []
    total   = 0
    for prod_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=int(prod_id))
            subtotal = producto.precio_final * cantidad
            total   += subtotal
            items.append({'producto': producto, 'cantidad': cantidad, 'subtotal': subtotal})
        except Producto.DoesNotExist:
            pass
    return render(request, 'productos/carrito.html', {'items': items, 'total': total})


@login_required
def actualizar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    str_id  = str(producto_id)
    accion  = request.POST.get('accion')

    if str_id in carrito:
        if accion == 'aumentar':
            try:
                producto = Producto.objects.get(id=producto_id)
                if carrito[str_id] < producto.cantidad:
                    carrito[str_id] += 1
                else:
                    messages.error(request, 'No hay más stock disponible.')
            except Producto.DoesNotExist:
                pass
        elif accion == 'disminuir':
            carrito[str_id] -= 1
            if carrito[str_id] <= 0:
                del carrito[str_id]
        elif accion == 'eliminar':
            del carrito[str_id]

    request.session['carrito']  = carrito
    request.session.modified    = True
    return redirect('ver_carrito')


@login_required
def vaciar_carrito(request):
    request.session['carrito'] = {}
    request.session.modified   = True
    messages.success(request, 'Carrito vaciado.')
    return redirect('ver_carrito')