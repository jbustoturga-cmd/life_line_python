# usuarios/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import FormularioRegistro, FormularioLogin, FormularioEditarPerfil
from .models import Usuario


# ── Página pública de inicio (landing) ────────────────────────────────────
def vista_logi(request):
    return render(request, 'usuarios/logi.html')


# ── Registro ───────────────────────────────────────────────────────────────
def vista_registro(request):
    if request.method == 'POST':
        formulario = FormularioRegistro(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Cuenta creada exitosamente. Inicia sesión.')
            return redirect('login')
    else:
        formulario = FormularioRegistro()
    return render(request, 'usuarios/registro.html', {'formulario': formulario})


# ── Login ──────────────────────────────────────────────────────────────────
def vista_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        formulario = FormularioLogin(request, data=request.POST)
        if formulario.is_valid():
            user = formulario.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        formulario = FormularioLogin()
    return render(request, 'usuarios/login.html', {'formulario': formulario})


# ── Logout ─────────────────────────────────────────────────────────────────
def vista_logout(request):
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


# ── Home / Dashboard ───────────────────────────────────────────────────────
@login_required
def vista_home(request):
    usuario = request.user

    if usuario.rol == 'ADMIN':
        try:
            from mural.models import Publicacion
            total_publicaciones = Publicacion.objects.count()
            publicaciones_recientes = Publicacion.objects.select_related('autor').order_by('-fecha_creacion')[:5]
            total_likes = sum(p.total_likes for p in Publicacion.objects.all())
            from django.utils import timezone
            inicio_semana = timezone.now() - __import__('datetime').timedelta(days=7)
            publicaciones_semana = Publicacion.objects.filter(fecha_creacion__gte=inicio_semana).count()
        except Exception:
            total_publicaciones = publicaciones_recientes = total_likes = publicaciones_semana = 0

        try:
            from productos.models import Producto
            total_productos = Producto.objects.count()
            stock_bajo_qs = Producto.objects.filter(cantidad__lt=5, estado=True).select_related('categoria')
            total_stock_bajo = stock_bajo_qs.count()
            stock_bajo = stock_bajo_qs[:5]
        except Exception:
            total_productos = total_stock_bajo = 0
            stock_bajo = []

        try:
            from carrito.models import Pedido
            total_pedidos = Pedido.objects.count()
            pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
        except Exception:
            total_pedidos = pedidos_pendientes = 0

        try:
            from alarma.models import Alarma
            alarmas_hoy = Alarma.objects.filter(activa=True).select_related('usuario').order_by('hora_toma')[:6]
        except Exception:
            alarmas_hoy = []

        from django.utils import timezone as tz
        total_usuarios = Usuario.objects.count()
        inicio_mes = tz.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        nuevos_usuarios_mes = Usuario.objects.filter(date_joined__gte=inicio_mes).count()
        usuarios_recientes = Usuario.objects.order_by('-date_joined')[:5]

        def pct(rol):
            return round(Usuario.objects.filter(rol=rol).count() / max(total_usuarios, 1) * 100)

        pct_pacientes = pct('PACIENTE')
        pct_cuidadores = pct('CUIDADOR')
        pct_profesionales = pct('PROFESIONAL')
        pct_users = 100 - pct_pacientes - pct_cuidadores - pct_profesionales

        context = {
            'usuario': usuario,
            'total_usuarios': total_usuarios,
            'nuevos_usuarios_mes': nuevos_usuarios_mes,
            'usuarios_recientes': usuarios_recientes,
            'pct_pacientes': pct_pacientes,
            'pct_cuidadores': pct_cuidadores,
            'pct_profesionales': pct_profesionales,
            'pct_users': pct_users,
            'total_publicaciones': total_publicaciones,
            'publicaciones_recientes': publicaciones_recientes,
            'publicaciones_semana': publicaciones_semana,
            'total_likes': total_likes,
            'total_productos': total_productos,
            'total_stock_bajo': total_stock_bajo,
            'stock_bajo': stock_bajo,
            'total_pedidos': total_pedidos,
            'pedidos_pendientes': pedidos_pendientes,
            'alarmas_hoy': alarmas_hoy,
        }
        return render(request, 'usuarios/dashboard.html', context)

    return render(request, 'usuarios/home.html', {'usuario': usuario})


# ── Perfil ─────────────────────────────────────────────────────────────────
@login_required
def vista_perfil(request):
    usuario = request.user
    if request.method == 'POST':
        formulario = FormularioEditarPerfil(request.POST, request.FILES, instance=usuario)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('perfil')
    else:
        formulario = FormularioEditarPerfil(instance=usuario)

    # Publicaciones del usuario (si existe la app mural)
    try:
        from mural.models import Publicacion
        mis_publicaciones = Publicacion.objects.filter(autor=usuario).order_by('-fecha_creacion')
    except Exception:
        mis_publicaciones = []

    return render(request, 'usuarios/perfil.html', {
        'formulario': formulario,
        'usuario': usuario,
        'mis_publicaciones': mis_publicaciones,
    })



# ── dashboard ─────────────────────────────────────────────────────────────────

@login_required
def vista_dashboard(request):
    if not request.user.es_admin():
        return redirect('home')

    usuario = request.user

    try:
        from mural.models import Publicacion
        total_publicaciones = Publicacion.objects.count()
        publicaciones_recientes = Publicacion.objects.select_related('autor').order_by('-fecha_creacion')[:5]
        total_likes = sum(p.total_likes for p in Publicacion.objects.all())
        from django.utils import timezone
        inicio_semana = timezone.now() - __import__('datetime').timedelta(days=7)
        publicaciones_semana = Publicacion.objects.filter(fecha_creacion__gte=inicio_semana).count()
    except Exception:
        total_publicaciones = 0
        publicaciones_recientes = []
        total_likes = 0
        publicaciones_semana = 0

    try:
        from productos.models import Producto
        total_productos = Producto.objects.count()
        stock_bajo_qs = Producto.objects.filter(cantidad__lt=5, estado=True).select_related('categoria')
        total_stock_bajo = stock_bajo_qs.count()
        stock_bajo = stock_bajo_qs[:5]
    except Exception:
        total_productos = 0
        total_stock_bajo = 0
        stock_bajo = []

    try:
        from carrito.models import Pedido
        total_pedidos = Pedido.objects.count()
        pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    except Exception:
        total_pedidos = 0
        pedidos_pendientes = 0

    try:
        from alarma.models import Alarma
        alarmas_hoy = Alarma.objects.filter(activa=True).select_related('usuario').order_by('hora_toma')[:6]
    except Exception:
        alarmas_hoy = []

    from django.utils import timezone as tz
    total_usuarios = Usuario.objects.count()
    inicio_mes = tz.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    nuevos_usuarios_mes = Usuario.objects.filter(date_joined__gte=inicio_mes).count()
    usuarios_recientes = Usuario.objects.order_by('-date_joined')[:5]

    def pct(rol):
        return round(Usuario.objects.filter(rol=rol).count() / max(total_usuarios, 1) * 100)

    context = {
        'usuario': usuario,
        'total_usuarios': total_usuarios,
        'nuevos_usuarios_mes': nuevos_usuarios_mes,
        'usuarios_recientes': usuarios_recientes,
        'pct_pacientes': pct('PACIENTE'),
        'pct_cuidadores': pct('CUIDADOR'),
        'pct_profesionales': pct('PROFESIONAL'),
        'pct_users': 100 - pct('PACIENTE') - pct('CUIDADOR') - pct('PROFESIONAL'),
        'total_publicaciones': total_publicaciones,
        'publicaciones_recientes': publicaciones_recientes,
        'publicaciones_semana': publicaciones_semana,
        'total_likes': total_likes,
        'total_productos': total_productos,
        'total_stock_bajo': total_stock_bajo,
        'stock_bajo': stock_bajo,
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'alarmas_hoy': alarmas_hoy,
    }

    return render(request, 'usuarios/dashboard.html', context)
# ── Registro TXT ───────────────────────────────────────────────────────────
def vista_registro_txt(request):
    from .registro import registrar_usuario, listar_usuarios
    usuarios_txt = listar_usuarios()
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        email = request.POST.get('email', '')
        if nombre and email:
            registrar_usuario(nombre, email)
            return redirect('registro_txt')
    return render(request, 'usuarios/registro_txt.html', {'usuarios': usuarios_txt})


# ── Contáctanos ────────────────────────────────────────────────────────────
def vista_contactanos(request):
    return render(request, 'usuarios/contactanos.html')


# ── CRUD Usuarios (solo ADMIN) ─────────────────────────────────────────────
@login_required
def vista_lista_usuarios(request):
    if not request.user.es_admin():
        return redirect('home')
    usuarios = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


@login_required
def vista_crear_usuario(request):
    from .forms import FormularioCrearUsuarioAdmin
    if not request.user.es_admin():
        return redirect('home')
    if request.method == 'POST':
        formulario = FormularioCrearUsuarioAdmin(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('lista_usuarios')
    else:
        formulario = FormularioCrearUsuarioAdmin()
    return render(request, 'usuarios/crear_usuario.html', {'formulario': formulario})


@login_required
def vista_editar_usuario(request, usuario_id):
    if not request.user.es_admin():
        return redirect('home')
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        formulario = FormularioEditarPerfil(request.POST, instance=usuario)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Usuario actualizado.')
            return redirect('lista_usuarios')
    else:
        formulario = FormularioEditarPerfil(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'formulario': formulario, 'usuario': usuario})


@login_required
def vista_eliminar_usuario(request, usuario_id):
    if not request.user.es_admin():
        return redirect('home')
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado.')
        return redirect('lista_usuarios')
    return render(request, 'usuarios/confirmar_eliminar.html', {'usuario': usuario})


# ── Error 404 personalizado ────────────────────────────────────────────────
def error_404(request, exception):
    return render(request, '404.html', status=404)