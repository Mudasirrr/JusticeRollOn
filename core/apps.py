"""
Application configuration for the 'core' app.

This file defines the configuration class for the core application.
Django uses AppConfig classes to store metadata and perform initialization
tasks for each app.

By explicitly defining this, we gain more control over app loading,
ready() signals, and future customizations (e.g., custom ready logic,
label/name overrides).

For more information:
https://docs.djangoproject.com/en/5.2/ref/applications/
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration class for the 'core' application.

    Attributes:
        default_auto_field (str): The default primary key field type to use
            for models in this app. 'BigAutoField' is recommended for new projects
            as it uses 64-bit integers (avoids running out of IDs).
        name (str): The full Python path to the application (required).
    """

    # Use BigAutoField for all models that don't specify a primary key
    # This is the Django-recommended default since Django 3.2
    default_auto_field = 'django.db.models.BigAutoField'

    # The name of the app as imported in the project
    # Must match the directory name ('core')
    name = 'core'

    # Optional: Human-readable name for the admin and other interfaces
    verbose_name = "Justice RollOn Core"

    # Optional: Custom ready() method can be added here later
    # def ready(self):
    #     """Perform initialization tasks when the app is ready."""
    #     import core.signals  # noqa: F401 - Import signals to connect them
    #     # Or register checks, start background tasks, etc.