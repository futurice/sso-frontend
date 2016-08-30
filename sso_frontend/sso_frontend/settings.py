import os.path
import ast

# Django settings for sso_frontend project.
INTERNAL_IPS=["127.0.0.1"]
URL_PREFIX = ""

BASE_DIR = os.getenv("BASE_DIR", os.path.dirname(os.path.dirname(__file__)))
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
TEMPLATE_DEBUG = DEBUG

TOP_DOMAIN = os.getenv("TOP_DOMAIN", "futurice.com")
DOMAIN = os.getenv("DOMAIN", "login.futurice.com")
SCHEME = os.getenv("SCHEME", "http")
SECURE_COOKIES = os.getenv('SECURE_COOKIES', 'true').lower() == 'true'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS
LOGIN_URL = URL_PREFIX+"/internal_login"

HUEY = {
    'backend': 'huey.backends.redis_backend',  # required.
    'name': 'sso_frontend',
    'connection': {'host': 'localhost', 'port': 6379},
    'always_eager': False, # Defaults to False when running via manage.py run_huey

    # Options to pass into the consumer when running ``manage.py run_huey``
    'consumer_options': {'workers': 4},
}

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'), # mysql,postgresql_psycopg2,sqlite3
        'NAME': os.getenv('DB_NAME', 'login'),
        'USER': os.getenv('DB_USER', 'login'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'login'),
        'HOST': os.getenv('DB_HOST', "postgres"),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 1,
            'PASSWORD': '',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'MAX_ENTRIES': 500000,
        },
    },
    'ratelimit': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 2,
            'PASSWORD': '',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'MAX_ENTRIES': 500000,
        },
    },
    'user_hashes': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 3,
            'PASSWORD': '',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'MAX_ENTRIES': 500000,
        },
    },
    'user_mapping': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 4,
            'PASSWORD': '',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'MAX_ENTRIES': 500000,
        },
    },
    'browsers': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 5,
            'PASSWORD': '',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'MAX_ENTRIES': 500000,
        },
    },
    'users': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 6,
            'PASSWORD': '',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'MAX_ENTRIES': 500000,
        },
    }
}

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '../')
GEOIP_DB = "/opt/static/GeoLite2-City.mmdb"
LOG_DIR = os.getenv("LOG_DIR", PROJECT_ROOT + "/logs/")
SAML_CERTS_DIR = os.getenv("SAML_CERTS_DIR", PROJECT_ROOT)


LOGIN_REDIRECT_URL = URL_PREFIX+'/idp/sso/post/response/preview/'

# SAML2IDP metadata settings
SAML2IDP_CONFIG = {
    'autosubmit': False,
    'issuer': '%s://%s'%(SCHEME,DOMAIN),
    'signing': True,
    'certificate_file': SAML_CERTS_DIR + '/saml2idp/keys/certificate.pem',
    'private_key_file': SAML_CERTS_DIR + '/saml2idp/keys/private-key.pem'
}
SAML2IDP_REMOTES = {
    # Group of SP CONFIGs.
    # friendlyname: SP config
    'google_apps': {
        'acs_url': 'https://www.google.com/a/futurice.com/acs',
        'processor': 'saml2idp.google_apps.Processor',
    }
}

RATELIMIT_ENABLE=True
RATELIMIT_USE_CACHE="ratelimit"


DATETIME_FORMAT='Y-m-d H:i:s'
DATE_FORMAT='Y-m-d'
TIME_FORMAT='H:i'
SHORT_DATE_FORMAT='Y-m-d'
SHORT_DATETIME_FORMAT='Y-m-d H:i'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ast.literal_eval(os.getenv('ALLOWED_HOSTS', '[\'%s\']' %DOMAIN))

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Helsinki'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/opt/media/")

SESSION_COOKIE_AGE=24*60*60*7
SESSION_SERIALIZER="django.contrib.sessions.serializers.PickleSerializer"
SESSION_ENGINE='redis_sessions.session'
SESSION_REDIS_PREFIX="dsess"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", "/opt/static/")

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)



# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'login_frontend.middleware.real_remote_ip.RealRemoteIP',
    'login_frontend.middleware.request_timing.InLoggingMiddleware',
    'login_frontend.middleware.urlcheck.UrlCheckMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'login_frontend.middleware.request_timing.OutLoggingMiddleware', # logging middleware should be before browsermiddleware, as browsermiddleware might abort on process_request.
    'login_frontend.middleware.browser.BrowserMiddleware',
    'login_frontend.middleware.p0f_middleware.P0fMiddleware',
    'login_frontend.middleware.vulnerabilities.VulnerableBrowser',
    'login_frontend.middleware.request_timing.ViewLoggingMiddleware',
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'login_frontend.middleware.location.LocationMiddleware',
    'login_frontend.middleware.real_remote_ip.RealRemoteIP', # this should be both first and last, as when processing responses, middlewares are executed in reverse order.
)

DISABLE_TIMING_LOGGING=False

from django.contrib import messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "login_frontend.context_processors.add_misc_info",
    "login_frontend.context_processors.add_user",
    "login_frontend.context_processors.add_session_info",
)

CSRF_COOKIE_SECURE=SECURE_COOKIES
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https' if CSRF_COOKIE_SECURE else 'http')
CSRF_COOKIE_HTTPONLY=True
CSRF_FAILURE_VIEW="login_frontend.error_views.error_csrf"

handler400 = "login_frontend.error_views.error_400"
handler403 = "login_frontend.error_views.error_403"
handler404 = "login_frontend.error_views.error_404"
handler500 = "login_frontend.error_views.error_500"


ROOT_URLCONF = 'sso_frontend.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sso_frontend.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

COMPRESS_ENABLED = os.getenv('COMPRESS_ENABLED', 'false').lower() == 'true'
COMPRESS_OFFLINE = os.getenv('COMPRESS_OFFLINE', 'true').lower() == 'true'
COMPRESS_REBUILD_TIMEOUT=86400*365*10 # Don't force rebuilds

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'login_frontend',
    'openid_provider',
    #'south',
    'huey.contrib.djhuey',
    'saml2idp',
    'admin_frontend',
    'cspreporting',
    'django_extensions',
    'django_statsd',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%Y-%m-%d %H:%M:%S"
        },
        'plain': {
            'format' : "[%(asctime)s] %(message)s",
            'datefmt' : "%Y-%m-%d %H:%M:%S"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile_main': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': LOG_DIR + "main",
            'formatter': 'standard',
        },
        'logfile_audit': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR + "audit",
            'formatter': 'plain',
        },

        'logfile_saml': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': LOG_DIR + "saml",
            'formatter': 'standard',
        },

        'logfile_openid': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': LOG_DIR + "openid",
            'formatter': 'standard',
        },

        'logfile_users': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': LOG_DIR + "users",
            'formatter': 'standard',
        },

        'logfile_django': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': LOG_DIR + "django",
            'formatter': 'standard',
        },

        'logfile_errors': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': LOG_DIR + "errors",
            'formatter': 'standard',
        },

        'logfile_timing': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': LOG_DIR + "timing",
            'formatter': 'standard',
        },

        'logfile_p0f': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': LOG_DIR + "p0f_data",
            'formatter': 'plain',
        },


        'logfile_request_timing': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': LOG_DIR + "request_timing",
            'formatter': 'standard',
        },

    },
    'loggers': {
        'django': {
          'handlers': ['logfile_django'],
          'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'logfile_errors'],
            'level': 'ERROR',
            'propagate': True,
        },
        'request_timing': {
          'handlers': ['logfile_request_timing'],
          'propagate': False,
          'level': 'INFO',
        },
        'p0f': {
          'handlers': ['logfile_p0f'],
          'propagate': False,
          'level': 'INFO',
        },
        'users': {
          'handlers': ['logfile_users'],
          'propagate': True,
          'level': 'INFO',
        },
        'openid_provider': {
          'handlers': ['logfile_openid'],
          'propagate': True,
          'level': 'INFO',
        },
        'saml2idp': {
          'handlers': ['logfile_saml'],
          'propagate': True,
          'level': 'INFO',
        },
        'timing_data': {
          'handlers': ['logfile_timing'],
          'propagate': False,
          'level': 'INFO',
        },
        'audit': {
          'handlers': ['logfile_audit'],
          'propagate': True,
          'level': 'INFO',
        },
        '': {
          'handlers': ['logfile_main'],
          'propagate': True,
          'level': 'INFO',
        },
    }
}




IP_NETWORKS = [
]

FQDN = DOMAIN

LDAP_SERVER = os.getenv('LDAP_SERVER', None) # for example, "ldaps://ldap.example.com"
LDAP_USER_BASE_DN = os.getenv('LDAP_USER_BASE_DN', None) # for example, "uid=%s,ou=People,dc=example,dc=com"
LDAP_GROUPS_BASE_DN = os.getenv('LDAP_GROUPS_BASE_DN', None) # for example, "ou=Groups,dc=example,dc=com"
LDAP_IGNORE_SSL = os.getenv('LDAP_IGNORE_SSL', 'false').lower() == 'true'
# skip LDAP SSL certificate checks
TOKEN_MAP = ast.literal_eval(os.getenv('TOKEN_MAP', "{}")) #  map of LDAP groups to pubtkt tokens. For example, {"Administrators": "admins", "ExternalContractors": "ext"}

FAKE_TESTING = os.getenv('FAKE_TESTING', 'false').lower() == 'true' # This uses LDAP stub and static SMS codes. Useful for smoke testing, but never set in production.
ADMIN_CONTACT_EMAIL = os.getenv("ADMIN_CONTACT_EMAIL", "help@%s" % DOMAIN)

SEND_EMAILS = os.getenv('SEND_EMAILS', 'true').lower() == 'true' # send "new device" and "new authenticator" emails

EMAIL_HOST = os.getenv('EMAIL_HOST', None)
EMAIL_PORT = os.getenv('EMAIL_PORT', None)
NOTICES_FROM_EMAIL = os.getenv('NOTICES_FROM_EMAIL', None)

AUTHENTICATOR_NAME = "%s@hostname -%s-"

P0F_SOCKET = None


PUBTKT_PRIVKEY=None
PUBTKT_PUBKEY = os.getenv('PUBTKT_PUBKEY', None)
PUBTKT_ALLOWED_DOMAINS=[]
SAML_PUBKEY = os.getenv('SAML_PUBKEY', None)

FUM_ADDRESS=os.getenv('FUM_ADDRESS', None)
FUM_API_ENDPOINT=os.getenv('FUM_API_ENDPOINT', None)
FUM_ACCESS_TOKEN=os.getenv('FUM_ACCESS_TOKEN', None)

SMS_GATEWAY_URL=os.getenv('SMS_GATEWAY_URL', None)
SMS_USERNAME=os.getenv('SMS_USERNAME', None)
SMS_PASSWORD=os.getenv('SMS_PASSWORD', None)

EMERGENCY_FONT = PROJECT_ROOT+"data/Consolas.ttf"

OPENID_PROVIDER_AX_EXTENSION=True
OPENID_FAILED_DISCOVERY_AS_VALID=False
OPENID_TRUSTED_ROOTS=[]

SECRET_KEY = os.getenv('SECRET_KEY')
P0FSOCKET = "/var/local/p0f/p0f.sock"

try:
    from local_settings import *
except ImportError as e:
    print(e)

check_keys = ["FQDN", "PUBTKT_PRIVKEY", "PUBTKT_PUBKEY", "SAML_PUBKEY", "LDAP_SERVER", "LDAP_USER_BASE_DN", "LDAP_GROUPS_BASE_DN", "NOTICES_FROM_EMAIL"]
for key_name in check_keys:
    if key_name not in locals():
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured("%s is not defined." % key_name)


if DEBUG and not FAKE_TESTING:
    INSTALLED_APPS += (
     # "debug_toolbar",
    )
