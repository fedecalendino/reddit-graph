import os
from pathlib import Path


# App =========================================================================

SUBREDDITS_ONLY = os.getenv("SUBREDDITS_ONLY", "false") == "true"
WIKI_PAGES_LIMIT = int(os.getenv("WIKI_PAGES_LIMIT", "200"))


# Applications ================================================================

INSTALLED_APPS = ["app"]


# Settings ====================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DEBUG", "false") == "true"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

REDDIT = {
    "USERAGENT": os.environ.get("REDDIT_USERAGENT"),
    "USERNAME": os.environ.get("REDDIT_USERNAME"),
    "PASSWORD": os.environ.get("REDDIT_PASSWORD"),
    "CLIENT_ID": os.environ.get("REDDIT_CLIENTID"),
    "CLIENT_SECRET": os.environ.get("REDDIT_CLIENTSECRET"),
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DATABASE_NAME", "reddit-graph"),
        "USER": os.environ.get("DATABASE_USER", "reddit-graph"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD", "password"),
        "HOST": os.environ.get("DATABASE_HOST", "localhost"),
        "PORT": int(os.environ.get("DATABASE_PORT", "5432")),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(levelname)s] > %(message)s",
            # "format": "[%(levelname)s][%(asctime)s] > %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
        "propagate": False,
    },
    "loggers": {
        "django.server": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        }
    },
}


# Internationalization ========================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Finish ======================================================================

print(f" * DEBUG = {DEBUG}")
print(f" * LOG_LEVEL = {LOG_LEVEL}")
print(f" * USERNAME = {REDDIT['USERNAME']}")
print(f" * SUBREDDITS_ONLY = {SUBREDDITS_ONLY}")
print(f" * WIKI_PAGES_LIMIT = {WIKI_PAGES_LIMIT}")

