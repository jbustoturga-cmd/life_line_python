# mural/views.py — ACTUALIZADO
# Solo se agrega filtro de palabras ofensivas. Todo lo demás igual.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Publicacion, Comentario
#views.py

# ── Lista de palabras no permitidas (básico) ───────────────────────────────
PALABRAS_PROHIBIDAS = [
    'idiota', 'estupido', 'estupida', 'imbecil', 'maldito', 'maldita',
    'inutil', 'basura', 'asco', 'odio', 'hdp', 'hp', 'gonorrea',
    'marica', 'hijueputa', 'puta', 'mierda', 'pendejo', 'pendeja',
    'carajo', 'verga', 'coño', 'joder', 'polla', 'culo', 'cabron',
    'cabrona', 'zorra', 'puto', 'pelotudo', 'tarado', 'tarada',
]

def _contiene_ofensa(texto):
    """Retorna True si el texto contiene alguna palabra prohibida."""
    texto_lower = texto.lower()
    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in texto_lower:
            return True
    return False


# ── Vista principal ────────────────────────────────────────────────────────

@login_required
def vista_mural(request):
    publicaciones = Publicacion.objects.select_related('autor').prefetch_related(
        'likes', 'comentarios__autor'
    ).all()

    usuario = request.user
    mis_publicaciones_count = usuario.publicaciones.count()
    total_likes = sum(p.total_likes for p in usuario.publicaciones.all())
    total_comentarios = usuario.comentarios_mural.count()

    return render(request, 'mural/mural.html', {
        'publicaciones':           publicaciones,
        'usuario':                 usuario,
        'mis_publicaciones_count': mis_publicaciones_count,
        'total_likes':             total_likes,
        'total_comentarios':       total_comentarios,
    })


# ── Crear publicación ──────────────────────────────────────────────────────

@login_required
def crear_publicacion(request):
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        tipo      = request.POST.get('tipo', 'APOYO')
        imagen    = request.FILES.get('imagen')

        if not contenido:
            messages.error(request, 'El contenido no puede estar vacío.')
            return redirect('mural')

        # ✅ Filtro de lenguaje ofensivo en publicaciones
        if _contiene_ofensa(contenido):
            messages.error(request, 'Tu publicación contiene lenguaje inapropiado. Por favor revísala.')
            return redirect('mural')

        Publicacion.objects.create(autor=request.user, contenido=contenido,
                                    tipo=tipo, imagen=imagen)
        messages.success(request, '¡Publicación creada!')
    return redirect('mural')


# ── Eliminar publicación ───────────────────────────────────────────────────

@login_required
def eliminar_publicacion(request, pub_id):
    pub = get_object_or_404(Publicacion, id=pub_id)
    if request.method == 'POST':
        if request.user == pub.autor or request.user.es_admin():
            pub.delete()
            messages.success(request, 'Publicación eliminada.')
        else:
            messages.error(request, 'No tienes permiso para eliminar esta publicación.')
    return redirect('mural')


# ── Like ───────────────────────────────────────────────────────────────────

@login_required
def dar_like(request, pub_id):
    pub = get_object_or_404(Publicacion, id=pub_id)
    if request.method == 'POST':
        if request.user in pub.likes.all():
            pub.likes.remove(request.user)
        else:
            pub.likes.add(request.user)
    return redirect('mural')


# ── Comentar ───────────────────────────────────────────────────────────────

@login_required
def agregar_comentario(request, pub_id):
    pub = get_object_or_404(Publicacion, id=pub_id)
    if request.method == 'POST':
        contenido = request.POST.get('comentario', '').strip()

        if not contenido:
            messages.error(request, 'El comentario no puede estar vacío.')
            return redirect('mural')

        # ✅ Filtro de lenguaje ofensivo en comentarios
        if _contiene_ofensa(contenido):
            messages.error(request, 'Tu comentario contiene lenguaje inapropiado. Por favor cámbialo.')
            return redirect('mural')

        if len(contenido) > 500:
            messages.error(request, 'El comentario no puede superar 500 caracteres.')
            return redirect('mural')

        Comentario.objects.create(publicacion=pub, autor=request.user, contenido=contenido)
        messages.success(request, 'Comentario agregado.')
    return redirect('mural')


# ── Eliminar comentario ────────────────────────────────────────────────────

@login_required
def eliminar_comentario(request, com_id):
    comentario = get_object_or_404(Comentario, id=com_id)
    if request.method == 'POST':
        if request.user == comentario.autor or request.user.es_admin():
            comentario.delete()
            messages.success(request, 'Comentario eliminado.')
        else:
            messages.error(request, 'No tienes permiso.')
    return redirect('mural')


# ── Editar perfil ──────────────────────────────────────────────────────────

@login_required
def vista_editar_perfil(request):
    usuario = request.user
    if request.method == 'POST':
        username         = request.POST.get('username', '').strip()
        email            = request.POST.get('email', '').strip()
        fecha_nacimiento = request.POST.get('fecha_nacimiento') or None
        tipo_documento   = request.POST.get('tipo_documento', '')
        numero_documento = request.POST.get('numero_documento', '').strip()
        new_password1    = request.POST.get('new_password1', '')
        new_password2    = request.POST.get('new_password2', '')
        foto             = request.FILES.get('foto_perfil')

        errores = []
        from usuarios.models import Usuario
        if username and username != usuario.username:
            if Usuario.objects.filter(username=username).exclude(pk=usuario.pk).exists():
                errores.append('Ese nombre de usuario ya está en uso.')
        if email and email != usuario.email:
            if Usuario.objects.filter(email=email).exclude(pk=usuario.pk).exists():
                errores.append('Ese correo ya está registrado.')
        if new_password1 or new_password2:
            if new_password1 != new_password2:
                errores.append('Las contraseñas no coinciden.')
            elif len(new_password1) < 8:
                errores.append('La contraseña debe tener al menos 8 caracteres.')

        if errores:
            for e in errores: messages.error(request, e)
        else:
            if username: usuario.username = username
            if email:    usuario.email = email
            if fecha_nacimiento:
                from datetime import date
                try: usuario.fecha_nacimiento = date.fromisoformat(fecha_nacimiento)
                except ValueError: pass
            usuario.tipo_documento   = tipo_documento
            usuario.numero_documento = numero_documento
            if foto: usuario.foto_perfil = foto
            if new_password1 and new_password1 == new_password2:
                usuario.set_password(new_password1)
            usuario.save()
            messages.success(request, '¡Perfil actualizado!')
            return redirect('editar_perfil')

    from django.utils import timezone
    return render(request, 'usuarios/editar_perfil.html', {
        'usuario': usuario, 'hoy': timezone.now().date(),
    })