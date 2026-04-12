# usuarios/forms.py — MEJORAS
# KAROL — Validaciones: nombre con letras, roles, documento mínimo 10 dígitos único

import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Usuario

#forms.py
# ─────────────────────────────────────────────────────────────────────────────
# Función helper reutilizable
# ─────────────────────────────────────────────────────────────────────────────

def _validar_nombre_con_letras(valor, campo="El campo"):
    """Lanza ValidationError si el valor no contiene al menos una letra."""
    if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]', valor):
        raise ValidationError(
            f'{campo} no puede contener solo números o signos. Debe tener letras.'
        )


# ─────────────────────────────────────────────────────────────────────────────
# Formulario de REGISTRO PÚBLICO
# Roles disponibles: solo USUARIO y PACIENTE
# ─────────────────────────────────────────────────────────────────────────────

class FormularioRegistro(UserCreationForm):
    """
    Registro que llena cualquier usuario desde /registro/
    CAMBIOS:
    - username debe contener al menos una letra
    - Roles: solo USUARIO y PACIENTE
    - Documento: mínimo 10 dígitos, solo números, no repetido
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingresa tu Correo', 'class': 'form-input'
        })
    )

    hoy       = timezone.now().date()
    min_fecha = hoy.replace(year=hoy.year - 120)

    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date', 'class': 'form-input',
            'max': str(timezone.now().date()),
            'min': str(timezone.now().date().replace(year=timezone.now().date().year - 120))
        })
    )

    tipo_documento = forms.ChoiceField(
        choices=[('', 'Elige tu Documento')] + Usuario.TIPO_DOC_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    numero_documento = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Número de documento (mín. 10 dígitos)',
            'class': 'form-input',
            'inputmode': 'numeric'
        })
    )

    # ✅ Solo USUARIO y PACIENTE en el registro público
    rol = forms.ChoiceField(
    choices=[
        ('USER',     'Usuario'),
        ('PACIENTE', 'Paciente'),
    ],
    initial='USER',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    estadio = forms.ChoiceField(
        choices=[('', 'Elige tu Estadio')] + Usuario.ESTADIO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model  = Usuario
        fields = [
            'username', 'email', 'fecha_nacimiento',
            'tipo_documento', 'numero_documento', 'rol', 'estadio',
            'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Nombre de usuario', 'class': 'form-input'
            }),
        }

    # ── Validaciones individuales ──────────────────────────────────────────

    def clean_username(self):
        """✅ El nombre de usuario debe contener al menos una letra."""
        username = self.cleaned_data.get('username', '').strip()
        _validar_nombre_con_letras(username, 'El nombre de usuario')
        return username

    def clean_numero_documento(self):
        """✅ Mínimo 10 dígitos, solo números, no repetido en la BD."""
        doc = self.cleaned_data.get('numero_documento', '').strip()
        if not doc:
            return doc  # No es obligatorio en el registro
        if not doc.isdigit():
            raise ValidationError('El documento solo debe contener números.')
        if len(doc) < 10:
            raise ValidationError('El documento debe tener mínimo 10 dígitos.')
        # Verificar que no exista en otro usuario
        qs = Usuario.objects.filter(numero_documento=doc)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe un usuario con ese número de documento.')
        return doc

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha:
            hoy = timezone.now().date()
            if fecha > hoy:
                raise ValidationError('La fecha de nacimiento no puede ser futura.')
            edad_anios = (hoy - fecha).days // 365
            if edad_anios < 5:
                raise ValidationError('El usuario debe tener al menos 5 años.')
            if edad_anios > 120:
                raise ValidationError('Por favor ingresa una fecha de nacimiento válida.')
        return fecha

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email            = self.cleaned_data.get('email', '')
        user.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        user.tipo_documento   = self.cleaned_data.get('tipo_documento', '')
        user.numero_documento = self.cleaned_data.get('numero_documento', '')
        user.rol              = self.cleaned_data.get('rol', 'USER')
        user.estadio          = self.cleaned_data.get('estadio', '')
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────────────────────────────────────
# Formulario de CREACIÓN DE USUARIO (panel admin)
# Roles disponibles: USUARIO, PACIENTE, ADMIN
# ─────────────────────────────────────────────────────────────────────────────

class FormularioCrearUsuarioAdmin(UserCreationForm):
    """
    Formulario que usa el admin para crear usuarios desde el panel.
    Tiene las mismas validaciones de nombre y documento,
    PERO permite el rol ADMIN además de usuario y paciente.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Correo electrónico'})
    )

    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )

    tipo_documento = forms.ChoiceField(
        choices=[('', 'Seleccionar')] + Usuario.TIPO_DOC_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    numero_documento = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input', 'placeholder': 'Mín. 10 dígitos',
            'inputmode': 'numeric'
        })
    )

    # ✅ ADMIN puede asignar también el rol ADMIN
    rol = forms.ChoiceField(
        choices=[
            ('USUARIO',   'Usuario'),
            ('PACIENTE',  'Paciente'),
            ('ADMIN',     'Administrador'),
        ],
        initial='USUARIO',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    estadio = forms.ChoiceField(
        choices=[('', 'Sin estadio')] + Usuario.ESTADIO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model  = Usuario
        fields = [
            'username', 'email', 'fecha_nacimiento',
            'tipo_documento', 'numero_documento', 'rol', 'estadio',
            'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Nombre de usuario'
            }),
        }

    def clean_username(self):
        """✅ Mismo que en registro: debe tener letras."""
        username = self.cleaned_data.get('username', '').strip()
        _validar_nombre_con_letras(username, 'El nombre de usuario')
        return username

    def clean_numero_documento(self):
        """✅ Mínimo 10 dígitos, solo números, único."""
        doc = self.cleaned_data.get('numero_documento', '').strip()
        if not doc:
            return doc
        if not doc.isdigit():
            raise ValidationError('El documento solo debe contener números.')
        if len(doc) < 10:
            raise ValidationError('El documento debe tener mínimo 10 dígitos.')
        qs = Usuario.objects.filter(numero_documento=doc)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe un usuario con ese número de documento.')
        return doc

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email            = self.cleaned_data.get('email', '')
        user.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        user.tipo_documento   = self.cleaned_data.get('tipo_documento', '')
        user.numero_documento = self.cleaned_data.get('numero_documento', '')
        user.rol              = self.cleaned_data.get('rol', 'USUARIO')
        user.estadio          = self.cleaned_data.get('estadio', '')
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────────────────────────────────────
# Formulario de EDICIÓN DE PERFIL (usuario logueado)
# ─────────────────────────────────────────────────────────────────────────────

class FormularioEditarPerfil(forms.ModelForm):
    class Meta:
        model  = Usuario
        fields = ['username', 'email', 'fecha_nacimiento', 'tipo_documento', 'numero_documento']
        widgets = {
            'username':         forms.TextInput(attrs={'class': 'form-input'}),
            'email':            forms.EmailInput(attrs={'class': 'form-input'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'tipo_documento':   forms.Select(attrs={'class': 'form-input'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-input', 'inputmode': 'numeric'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        _validar_nombre_con_letras(username, 'El nombre de usuario')
        # Verificar que no esté en uso por otro usuario
        qs = Usuario.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ese nombre de usuario ya está en uso.')
        return username

    def clean_numero_documento(self):
        doc = self.cleaned_data.get('numero_documento', '').strip()
        if not doc:
            return doc
        if not doc.isdigit():
            raise ValidationError('El documento solo debe contener números.')
        if len(doc) < 10:
            raise ValidationError('El documento debe tener mínimo 10 dígitos.')
        qs = Usuario.objects.filter(numero_documento=doc)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe un usuario con ese número de documento.')
        return doc
    
    from django.contrib.auth.forms import AuthenticationForm

class FormularioLogin(AuthenticationForm):
    """Formulario de inicio de sesión reutilizando AuthenticationForm de Django."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={
            'placeholder': 'Nombre de usuario',
            'class': 'form-input',
            'id': 'id_username'
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-input',
            'id': 'id_password'
        })