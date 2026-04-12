# carrito/context_processors.py

def carrito_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            from carrito.models import CarritoItem
            from django.db.models import Sum
            count = CarritoItem.objects.filter(
                usuario=request.user
            ).aggregate(total=Sum('cantidad'))['total'] or 0
        except Exception:
            count = 0
    return {'carrito_count': count}