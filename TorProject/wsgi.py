"""
WSGI config for TorProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""
import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "/home/rfidlab/TorProject")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "/home/rfidlab/TorProject/myProjectEnv")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TorProject.settings")
#os.environ["DJANGO_SETTINGS_MODULE"] = "TorProject.settings"

application = get_wsgi_application()
