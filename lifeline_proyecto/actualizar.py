import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifeline.settings')
django.setup()

from productos.models import Producto

actualizaciones = [
    ('Bolsa Isotérmica', 'img/BOLSO TER.jpeg'),
    ('Ungüento de Caléndula', 'img/HUNGUENT.jpeg'),
    ('Sujetador Post', 'img/BRA.jpeg'),
    ('Vendas Adhesivas', 'img/CINTA.jpeg'),
    ('Cubierta Protectora', 'img/CUBIERTA.jpeg'),
    ('Organizador de Pastillas', 'img/pastillAS.jpeg'),
    ('Almohada Axilar', 'img/almoha cora.jpeg'),
    ('Crema Ultra', 'img/Cuidado de la piel en arte digital.png'),
    ('Turbantes', 'img/Mujer con turbante y colores vibrantes.png'),
    ('Infusiones', 'img/te.png'),
    ('Almohada Ergonómica', 'img/almohada.jpg'),
    ('Libreta', 'img/libreta.webp'),
    ('Bálsamo Labial', 'img/labial.webp'),
    ('Guantes Suaves', 'img/guantes.webp'),
    ('Mascarillas', 'img/mascarilla.webp'),
    ('Toallitas', 'img/tuallitas h.jpeg'),
    ('Manta Ponderada', 'img/cobija.jpeg'),
    ('Almohadilla Térmica', 'img/almohada ter.jpeg'),
    ('Protector Solar', 'img/bloqueador.png'),
    ('Sérum Capilar', 'img/cerum.png'),
    ('Jabón Corporal', 'img/jabon.png'),
    ('Pijamas', 'img/pijama life.jpeg'),
    ('Snacks', 'img/snack.jpeg'),
    ('Jengibre', 'img/gomitas.jpeg'),
    ('Linfoedema', 'img/kit.png'),
]

for nombre, imagen in actualizaciones:
    productos = Producto.objects.filter(nombre__icontains=nombre)
    if productos.exists():
        for p in productos:
            p.imagen = imagen
            p.cantidad = 50
            p.estado = True
            p.save()
            print(f'Actualizado: {p.nombre}')
    else:
        print(f'No encontrado: {nombre}')

print('Listo!')