# reportes/views.py
# JHOAN — Reporte emocional arreglado + PDF de productos + Protección Admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from usuarios.models import Usuario
import datetime

# --- HELPER DE SEGURIDAD ---
def solo_admin(user):
    """Verifica si el usuario es staff de Django o tiene el rol de ADMIN en el modelo."""
    return user.is_staff or getattr(user, 'rol', '') == 'ADMIN'

def _filtrar_clientes(request):
    nombre = request.GET.get('nombre', '').strip()
    desde  = request.GET.get('desde',  '').strip()
    hasta  = request.GET.get('hasta',  '').strip()
    qs = Usuario.objects.all().order_by('-date_joined')
    if nombre:
        qs = qs.filter(username__icontains=nombre)
    if desde:
        try: qs = qs.filter(date_joined__date__gte=datetime.date.fromisoformat(desde))
        except ValueError: pass
    if hasta:
        try: qs = qs.filter(date_joined__date__lte=datetime.date.fromisoformat(hasta))
        except ValueError: pass
    return qs, nombre, desde, hasta


# ── Clientes ───────────────────────────────────────────────────────────────

@login_required
def vista_clientes(request):
    if not solo_admin(request.user):
        return redirect('home')
    
    clientes, nombre, desde, hasta = _filtrar_clientes(request)
    return render(request, 'reportes/clientes.html', {
        'clientes': clientes, 'nombre_filtro': nombre,
        'desde_filtro': desde, 'hasta_filtro': hasta, 'total': clientes.count(),
    })

@login_required
def vista_reporte_pdf(request):
    if not solo_admin(request.user):
        return redirect('home')

    clientes, nombre, desde, hasta = _filtrar_clientes(request)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_clientes_lifeline.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(letter),
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.7*inch, bottomMargin=0.5*inch)
    estilos = getSampleStyleSheet()
    tit = ParagraphStyle('T', parent=estilos['Heading1'], fontSize=20,
                         textColor=colors.HexColor('#1D3461'), alignment=TA_CENTER, spaceAfter=6)
    sub = ParagraphStyle('S', parent=estilos['Normal'], fontSize=11,
                         textColor=colors.grey, alignment=TA_CENTER, spaceAfter=20)
    elementos = [Paragraph("LifeLine — Reporte de Clientes", tit)]
    subtitulo = f"Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if nombre: subtitulo += f"  |  Nombre: '{nombre}'"
    elementos += [Paragraph(subtitulo, sub), Spacer(1, 0.2*inch)]
    filas = [['ID', 'Nombre', 'Correo', 'Documento', 'Rol', 'Fecha Registro']]
    for c in clientes:
        filas.append([str(c.id), c.username, c.email or '—',
                      c.numero_documento or '—', c.get_rol_display(),
                      c.date_joined.strftime("%d/%m/%Y")])
    if len(filas) == 1:
        filas.append(['—', 'Sin resultados', '—', '—', '—', '—'])
    tabla = Table(filas, colWidths=[0.6*inch, 2*inch, 2.8*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1D3461')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,0),11),
        ('ALIGN',(0,0),(-1,0),'CENTER'),('BOTTOMPADDING',(0,0),(-1,0),10),
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,1),(-1,-1),10),
        ('TOPPADDING',(0,1),(-1,-1),8),('BOTTOMPADDING',(0,1),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#EEF2FB')]),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#CCCCCC')),
        ('BOX',(0,0),(-1,-1),1.5,colors.HexColor('#1D3461')),
    ]))
    elementos.append(tabla)
    elementos += [Spacer(1,0.3*inch),
                  Paragraph(f"Total: {len(filas)-1}  |  LifeLine © {datetime.datetime.now().year}",
                               ParagraphStyle('P',parent=estilos['Normal'],fontSize=9,
                                            textColor=colors.grey,alignment=TA_CENTER))]
    doc.build(elementos)
    return response


# ── Productos ──────────────────────────────────────────────────────────────

@login_required
def vista_productos_reporte(request):
    if not solo_admin(request.user):
        return redirect('home')

    from productos.models import Producto
    categoria_filtro = request.GET.get('categoria', '').strip()
    productos = Producto.objects.all().select_related('categoria').order_by('-fecha_creacion')
    if categoria_filtro:
        productos = productos.filter(categoria__nombre__icontains=categoria_filtro)
    categorias = Producto.objects.values_list('categoria__nombre', flat=True).distinct()
    return render(request, 'reportes/productos_reporte.html', {
        'productos': productos, 'categoria_filtro': categoria_filtro,
        'categorias': categorias, 'total': productos.count(),
    })


@login_required
def vista_productos_pdf(request):
    if not solo_admin(request.user):
        return redirect('home')

    from productos.models import Producto
    categoria_filtro = request.GET.get('categoria', '').strip()
    productos = Producto.objects.all().select_related('categoria').order_by('-fecha_creacion')
    if categoria_filtro:
        productos = productos.filter(categoria__nombre__icontains=categoria_filtro)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_productos_lifeline.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(letter),
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.7*inch, bottomMargin=0.5*inch)
    estilos = getSampleStyleSheet()
    tit = ParagraphStyle('T', parent=estilos['Heading1'], fontSize=20,
                         textColor=colors.HexColor('#1D3461'), alignment=TA_CENTER, spaceAfter=6)
    sub = ParagraphStyle('S', parent=estilos['Normal'], fontSize=11,
                         textColor=colors.grey, alignment=TA_CENTER, spaceAfter=20)
    elementos = [Paragraph("LifeLine — Reporte de Productos", tit)]
    subtitulo = f"Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if categoria_filtro: subtitulo += f"  |  Categoría: '{categoria_filtro}'"
    elementos += [Paragraph(subtitulo, sub), Spacer(1, 0.2*inch)]
    filas = [['ID', 'Nombre', 'Categoría', 'Precio (COP)', 'Stock', 'Estado', 'Vencimiento']]
    for p in productos:
        venc = p.fecha_vencimiento.strftime("%d/%m/%Y") if p.fecha_vencimiento else '—'
        filas.append([str(p.id), p.nombre, str(p.categoria),
                      f"${p.precio_final:,.0f}", str(p.cantidad),
                      'Activo' if p.estado else 'Inactivo', venc])
    if len(filas) == 1:
        filas.append(['—', 'Sin resultados', '—', '—', '—', '—', '—'])
    tabla = Table(filas, colWidths=[0.5*inch,2.4*inch,1.6*inch,1.4*inch,0.8*inch,1*inch,1.3*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1D3461')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,0),10),
        ('ALIGN',(0,0),(-1,0),'CENTER'),('BOTTOMPADDING',(0,0),(-1,0),10),
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,1),(-1,-1),9),
        ('TOPPADDING',(0,1),(-1,-1),7),('BOTTOMPADDING',(0,1),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#EEF2FB')]),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#CCCCCC')),
        ('BOX',(0,0),(-1,-1),1.5,colors.HexColor('#1D3461')),
    ]))
    elementos.append(tabla)
    elementos += [Spacer(1,0.3*inch),
                  Paragraph(f"Total: {len(filas)-1} productos | LifeLine © {datetime.datetime.now().year}",
                               ParagraphStyle('P',parent=estilos['Normal'],fontSize=9,
                                            textColor=colors.grey,alignment=TA_CENTER))]
    doc.build(elementos)
    return response


# ── Stock bajo ─────────────────────────────────────────────────────────────

@login_required
def vista_reporte_stock(request):
    if not solo_admin(request.user):
        return redirect('home')

    from productos.models import Producto
    stock_bajo = Producto.objects.filter(cantidad__lt=5, estado=True).select_related('categoria')
    return render(request, 'reportes/stock.html', {
        'stock_bajo': stock_bajo, 'total': stock_bajo.count(),
    })


# ── Medicamentos ───────────────────────────────────────────────────────────

@login_required
def vista_reporte_medicamentos(request):
    if not solo_admin(request.user):
        return redirect('home')

    try:
        from alarma.models import Alarma, HistorialDosis
        medicamentos_top = (Alarma.objects.values('medicamento')
                            .annotate(total=Count('id')).order_by('-total')[:10])
        total_dosis = HistorialDosis.objects.count()
        tomadas     = HistorialDosis.objects.filter(estado='tomada').count()
        omitidas    = HistorialDosis.objects.filter(estado='omitida').count()
        pct = round((tomadas / total_dosis * 100), 1) if total_dosis > 0 else 0
    except Exception:
        medicamentos_top = []; total_dosis = tomadas = omitidas = pct = 0
    return render(request, 'reportes/medicamentos.html', {
        'medicamentos_top': medicamentos_top,
        'total_dosis': total_dosis, 'tomadas': tomadas,
        'omitidas': omitidas, 'pct_cumplimiento': pct,
    })


# ── ✅ Emocional CORREGIDO ─────────────────────────────────────────────────

@login_required
def vista_reporte_emocional(request):
    if not solo_admin(request.user):
        return redirect('home')

    try:
        from mural.models import Publicacion, Comentario

        por_tipo = (
            Publicacion.objects
            .values('tipo')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        total_pub  = Publicacion.objects.count()
        total_com  = Comentario.objects.count()
        total_likes = sum(p.total_likes for p in Publicacion.objects.all())

        usuarios_activos = (
            Publicacion.objects
            .values('autor__username')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )

    except Exception:
        por_tipo = []; total_pub = total_com = total_likes = 0; usuarios_activos = []

    return render(request, 'reportes/emocional.html', {
        'por_categoria':    por_tipo,
        'total_pub':        total_pub,
        'total_com':        total_com,
        'total_likes':      total_likes,
        'usuarios_activos': usuarios_activos,
    })


# ── Tienda ─────────────────────────────────────────────────────────────────

@login_required
def vista_reporte_tienda(request):
    if not solo_admin(request.user):
        return redirect('home')

    try:
        from carrito.models import CarritoItem, Pedido
        from productos.models import Producto
        productos_populares = (CarritoItem.objects.values('producto__nombre')
                               .annotate(total=Count('id')).order_by('-total')[:10])
        total_pedidos     = Pedido.objects.count()
        pedidos_recientes = Pedido.objects.all().order_by('-fecha_pedido')[:10]
        stock_bajo        = Producto.objects.filter(cantidad__lt=5, estado=True).count()
    except Exception:
        productos_populares = []; total_pedidos = 0; pedidos_recientes = []; stock_bajo = 0
    return render(request, 'reportes/tienda_reporte.html', {
        'productos_populares': productos_populares,
        'total_pedidos': total_pedidos,
        'pedidos_recientes': pedidos_recientes,
        'stock_bajo': stock_bajo,
    })