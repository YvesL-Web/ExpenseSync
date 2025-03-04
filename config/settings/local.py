from os import getenv, path

from dotenv import load_dotenv

from .base import * #noqa 
from .base import BASE_DIR


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("DJANGO_SECRET_KEY","T0YYpLgmHwTXpTAGv1TekS36MoSu9-UfUnJ6YE8r85vFxVS7BqI")

ALLOWED_HOSTS = ["localhost","127.0.0.1","0.0.0.0"]

DOMAIN = getenv("DOMAIN")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format":"%(levelname)s %(name)-12s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        }
    },
    "handlers": {
        "console":{
            "level": "DEBUG",
            "class":"logging.StreamHandler",
            "formatter": "verbose"
        }
    },
    "root":{
        "level":"INFO",
        "handlers":["console"]
    }
}

# Cors headers setup
CORS_ALLOWED_ORIGINS = getenv("CORS_ALLOWED_ORIGINS","http://localhost:3000, http://127.0.0.1:3000").split(",")
CORS_ALLOW_CREDENTIALS = True