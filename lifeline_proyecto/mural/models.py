# mural/models.py
# Crea este archivo NUEVO en la carpeta de tu app mural.
# Si no tienes app mural todavía, créala con:
#   python manage.py startapp mural
# Luego agrégala a INSTALLED_APPS en settings.py

import re
from django.db import models
from django.conf import settings


class Publicacion(models.Model):
    """Publicación del mural de la comunidad"""

    TIPO_CHOICES = [
        ('APOYO',       '💙 Apoyo'),
        ('EXPERIENCIA', '🌱 Experiencia'),
        ('CONSEJO',     '💡 Consejo'),
        ('PREGUNTA',    '❓ Pregunta'),
    ]

    autor          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publicaciones'   # acceso: usuario.publicaciones.all()
    )
    contenido      = models.TextField(max_length=2000)
    tipo           = models.CharField(max_length=20, choices=TIPO_CHOICES, default='APOYO')
    imagen         = models.ImageField(upload_to='mural/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    likes          = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='pubs_liked'      # acceso: usuario.pubs_liked.all()
    )

    class Meta:
        ordering            = ['-fecha_creacion']
        verbose_name        = 'Publicación'
        verbose_name_plural = 'Publicaciones'

    def __str__(self):
        return f"{self.autor.username}: {self.contenido[:60]}"

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def hashtags_list(self):
        """Devuelve lista de hashtags encontrados en el contenido, sin el #"""
        return re.findall(r'#(\w+)', self.contenido)


class Comentario(models.Model):
    """Comentario en una publicación del mural"""

    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='comentarios'     # acceso: publicacion.comentarios.all()
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios_mural'   # ← DIFERENTE al de usuarios para evitar conflicto
    )
    contenido      = models.TextField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ['fecha_creacion']
        verbose_name        = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f"{self.autor.username} → pub {self.publicacion.id}: {self.contenido[:40]}"