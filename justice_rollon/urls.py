"""
URL configuration for the justice_rollon project.

This is the root URL configuration file that defines how incoming HTTP requests
are routed to the appropriate views or included applications.

It acts as the central dispatcher:
- Routes admin requests to Django's built-in admin site
- Delegates all other requests to the 'core' app for handling
- Serves media files (uploads) during development

For more information:
https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


# =============================================================================
# ROOT URL PATTERNS
# =============================================================================
urlpatterns = [
    # Django Admin Interface
    # Accessible at: /admin/
    # Provides full CRUD interface for models registered in admin.py
    path("admin/", admin.site.urls),

    # Core Application URLs
    # All other routes (including homepage) are handled by the 'core' app
    # Example: /, /petitions/, /login/, etc. → defined in core/urls.py
    path("", include("core.urls")),
]


# =============================================================================
# MEDIA FILES SERVING (DEVELOPMENT ONLY)
# =============================================================================
# In development (DEBUG = True), Django can serve user-uploaded media files
# (e.g., evidence PDFs, profile images) directly from the MEDIA_ROOT directory.
#
# This is convenient for local testing but should NEVER be used in production.
# In production, use a proper web server (Nginx) or cloud storage (S3, etc.).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Optional: Also serve static files in debug mode if needed
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)