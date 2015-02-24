"""
Django settings for gameshop project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2m1hic6!!$c%-n4p4%ctz5c=00p8abz!^1q87y^^$z*b5sc4-6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'game',
)

#FOR FACEBOOK AUTHENTICATION
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

#FOR FACEBOOK AUTHENTICATION
AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_FACEBOOK_KEY = 917666578246194
SOCIAL_AUTH_FACEBOOK_SECRET = "27cbe895c011190c4aa9dd77ec2f714a"
SOCIAL_AUTH_FACEBOOK_SCOPE = ['publish_actions', 'email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'locale': 'en_US'}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'gameshop.urls'

WSGI_APPLICATION = 'gameshop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

#Nämä on kaikki meidän omalisäämiä!

STATIC_URL = '/static/'

abspath = lambda *p: os.path.abspath(os.path.join(*p))

PROJECT_ROOT = abspath(os.path.dirname(__file__))

MEDIA_ROOT = abspath(PROJECT_ROOT, 'media')

MEDIA_URL = '/media/'

# Tällä ohjataan käyttäjä automaattisesti login-sivulle, jos
# käyttäjä yrittää kirjautumista vaativalle sivulle ilman loginia
# (esim. game/play/01)
LOGIN_URL = '/game/login/'
LOGIN_REDIRECT_URL = '/game/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'atrojuhalauriwsd2014@gmail.com'
EMAIL_HOST_PASSWORD = 'AtroJuhaLauri'
DEFAULT_FROM_EMAIL = 'WSD WebShop'
