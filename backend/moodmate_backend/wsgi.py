"""
WSGI config for MoodMate backend.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moodmate_backend.settings')
application = get_wsgi_application()
