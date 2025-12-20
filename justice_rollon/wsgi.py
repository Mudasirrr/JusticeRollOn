"""
WSGI config for the justice_rollon project.

This file defines the WSGI (Web Server Gateway Interface) application entry point
for the Django project. It exposes a module-level variable named ``application``
that serves as the main callable for WSGI-compatible web servers and deployment
platforms (such as Gunicorn, uWSGI, mod_wsgi, Waitress, etc.).

WSGI is the standard synchronous interface between Python web applications and
web servers. It is used for traditional HTTP request/response handling.

Note: For asynchronous features (e.g., WebSockets), use asgi.py instead.

For more details, see:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

# Import Django's built-in WSGI application handler
from django.core.wsgi import get_wsgi_application


# =============================================================================
# DJANGO SETTINGS CONFIGURATION
# =============================================================================
# Set the default DJANGO_SETTINGS_MODULE environment variable if not already set.
# This ensures the correct settings file (justice_rollon.settings) is used when
# the application is loaded by the WSGI server.
# This pattern is safe, idempotent, and consistent with manage.py and asgi.py.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'justice_rollon.settings')


# =============================================================================
# WSGI APPLICATION INSTANCE
# =============================================================================
# Create and expose the WSGI application instance.
# get_wsgi_application() loads Django settings (if not already loaded) and
# returns a fully configured WSGI callable ready to handle HTTP requests.
#
# WSGI servers (like Gunicorn or uWSGI) import this ``application`` variable
# and use it to serve the Django project.
application = get_wsgi_application()