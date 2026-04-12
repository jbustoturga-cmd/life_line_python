# productos/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.utils import timezone

class Categoria(models.Model):
    """
    NUEVO FASE 3 — Categoría como modelo propio (FK).
    """#models.py
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    # Opciones de uso recomendadas (Fase 3)
    USO_CHOICES = [
        ('nauseas',   'Para náuseas'),
        ('fatiga',    'Para fatiga'),
        ('dolor',     'Para dolor'),
        ('nutricion', 'Nutrición'),
        ('higiene',   'Higiene y cuidado'),
        ('general',   'Uso general'),
    ]

    nombre = models.CharField(
        max_length=200, 
        verbose_name='Nombre',
        validators=[MinLengthValidator(3, 'El nombre debe tener al menos 3 caracteres.')]
    )
    descripcion = models.TextField(verbose_name='Descripción')

    # ✅ FASE 3: Ahora es una relación ForeignKey (Protegida)
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT, 
        verbose_name='Categoría'
    )

    precio_final = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Precio (COP)',
        validators=[
            MinValueValidator(0.01, 'El precio debe ser mayor a 0.'),
            MaxValueValidator(9999999, 'El precio máximo permitido es $9.999.999.')
        ]
    )
    
    cantidad = models.IntegerField(
        default=0, 
        verbose_name='Stock',
        validators=[MinValueValidator(0, 'El stock no puede ser negativo.')]
    )
    
    estado = models.BooleanField(default=True, verbose_name='Activo')
    
    imagen = models.ImageField(
        upload_to='productos/', 
        blank=True, 
        null=True, 
        verbose_name='Imagen'
    )

    # ✅ FASE 3: Nuevo campo de uso
    uso_recomendado = models.CharField(
        max_length=20, 
        choices=USO_CHOICES, 
        default='general',
        verbose_name='Uso recomendado'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha creación')
    
    fecha_vencimiento = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Fecha de vencimiento',
        help_text='Dejar vacío si el producto no vence.'
    )

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
        # ✅ FASE 3: No permite mismo nombre en la misma categoría
        unique_together = ('nombre', 'categoria')

    def __str__(self):
        return self.nombre

    # ── @property: Mantengo tus decoradores para no romper tus vistas ─────

    @property
    def tiene_stock(self):
        """True si hay al menos 1 unidad disponible."""
        return self.cantidad > 0

    @property
    def esta_vencido(self):
        """True si la fecha de vencimiento ya pasó."""
        if self.fecha_vencimiento:
            return self.fecha_vencimiento < timezone.now().date()
        return False

    @property
    def dias_para_vencer(self):
        """Días que faltan para vencer (None si no tiene fecha)."""
        if self.fecha_vencimiento:
            return (self.fecha_vencimiento - timezone.now().date()).days
        return None

    @property
    def stock_bajo(self):
        """True si hay menos de 5 unidades — Útil para alertas."""
        return 0 <= self.cantidad < 5