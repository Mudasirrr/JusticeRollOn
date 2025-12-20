"""
ASGI config for the justice_rollon project.

This file defines the ASGI (Asynchronous Server Gateway Interface) application
entry point for the Django project. It exposes a module-level variable named
``application`` that serves as the main callable for ASGI-compatible web servers
(such as Daphne, Uvicorn, or Hypercorn).

ASGI is the asynchronous successor to WSGI and enables handling of both
HTTP and WebSocket connections in the same application — essential for
real-time features like live notifications, chat, or streaming updates.

For more details, see:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

# Import Django's built-in ASGI application handler
from django.core.asgi import get_asgi_application


# =============================================================================
# DJANGO SETTINGS CONFIGURATION
# =============================================================================
# Set the default DJANGO_SETTINGS_MODULE environment variable if not already set.
# This ensures that the correct settings file (justice_rollon.settings) is used
# when the application is loaded by the ASGI server.
# It's safe to call multiple times and mirrors the pattern used in manage.py and wsgi.py.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'justice_rollon.settings')


# =============================================================================
# ASGI APPLICATION INSTANCE
# =============================================================================
# Create and expose the ASGI application instance.
# get_asgi_application() loads the Django settings (if not already loaded)
# and returns a fully configured ASGI callable ready to handle requests.
# This ``application`` variable is what ASGI servers (like Daphne or Uvicorn)
# expect to import and serve.
application = get_asgi_application()