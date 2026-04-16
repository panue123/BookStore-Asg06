from .base import *
import os

DEBUG = True
DATABASES['default']['HOST'] = os.getenv('DB_HOST', 'localhost')
