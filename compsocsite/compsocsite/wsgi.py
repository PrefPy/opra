"""
WSGI config for compsocsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os,sys

from django.core.wsgi import get_wsgi_application
#from whitenoise.django import DjangoWhiteNoise
sys.path.append('/home/usr/local/lib/python3.6/dist-packages')
sys.path.append('/home/OPRAH/opra')

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "compsocsite.settings")

application = get_wsgi_application()
#application = DjangoWhiteNoise(application)
