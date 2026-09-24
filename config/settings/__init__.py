# config/settings/__init__.py

import os
from environs import Env

# اول .env را بخوان تا DJANGO_ENV داخل آن هم اعمال شود
env = Env()
env.read_env()

environment = env.str("DJANGO_ENV", os.getenv("DJANGO_ENV", "development")).lower()

if environment == "production":
    from .production import *
else:
    from .development import *
