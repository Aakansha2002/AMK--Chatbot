from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "amk-demo-development-key-change-before-deployment")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,amk-chatbot-fuss.onrender.com").split(",") if host.strip()]
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.staticfiles", "chatbot"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware"]
ROOT_URLCONF = "amk.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "APP_DIRS": True, "OPTIONS": {"context_processors": []}}]
WSGI_APPLICATION = "amk.wsgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
META_VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN", "")
META_APP_SECRET = os.environ.get("META_APP_SECRET", "")
META_INSTAGRAM_ACCESS_TOKEN = os.environ.get("META_INSTAGRAM_ACCESS_TOKEN", "")
META_INSTAGRAM_ACCOUNT_ID = os.environ.get("META_INSTAGRAM_ACCOUNT_ID", "")
META_GRAPH_VERSION = os.environ.get("META_GRAPH_VERSION", "v26.0")
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME", "indianweddingplanners").lstrip("@").strip()
WHATSAPP_NUMBER = "".join(c for c in os.environ.get("WHATSAPP_NUMBER", "919251966666") if c.isdigit()) or "919251966666"
