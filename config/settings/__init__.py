# config/settings/__init__.py

import os

environment = os.getenv("DJANGO_ENV", "development").lower()

if environment == "production":
    from .production import *
else:
    from .development import *
