# lifeline/settings.py
# JHOAN - Configuración completa del proyecto LifeLine - FASE 2

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
#settings.py
# ============================================================
# SEGURIDAD
# ============================================================
SECRET_KEY = 'django-insecure-lifeline-proyecto-sena-adso-cambiar-en-produccion'

# En desarrollo: True. En PythonAnywhere cambiar a False
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
# En PythonAnywhere descommentar:
# ALLOWED_HOSTS = ['tuusuario.pythonanywhere.com']

# ============================================================
# APLICACIONES INSTALADAS - FASE 2
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto LifeLine
    'usuarios',     # Karol
    'productos',    # Leidy
    'carrito',      # Leidy  ← NUEVA FASE 2
    'reportes',     # Jhoan
    'mural',        # Jhoan  ← NUEVA FASE 2
    #fase 3
    'alarma', 'calendario', 'ejercicio',
    'nutricion',

]

# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lifeline.urls'

# ============================================================
# TEMPLATES
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'carrito.context_processors.carrito_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'lifeline.wsgi.application'

# ============================================================
# BASE DE DATOS
# ============================================================
import os
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(
        'postgresql://postgres:hmQZTOZdsopLCRgKbQfdZlmfgXjTXqWn@acela.proxy.rlwy.net:46669/railway',
        conn_max_age=600,
        ssl_require=True
    )
}
# ============================================================
# MODELO DE USUARIO PERSONALIZADO
# ⚠️ CRÍTICO: debe estar configurado ANTES de la primera migración
# ============================================================
AUTH_USER_MODEL = 'usuarios.Usuario'

# ============================================================
# AUTENTICACIÓN
# ============================================================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/'



# ============================================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# INTERNACIONALIZACIÓN
# ============================================================
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ============================================================
# ARCHIVOS ESTÁTICOS (Génesis)
# ============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ============================================================
# ARCHIVOS MEDIA — imágenes subidas por usuarios (Leidy y Jhoan)
# ============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================
# PRIMARY KEY
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ALLOWED_HOSTS = [
    "lifelinepython-production.up.railway.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://lifelinepython-production.up.railway.app",
]