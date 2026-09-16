"""
ASGI config for Cloud Screen.

Prepared for Django Channels (Phase 2 - real-time updates).
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
