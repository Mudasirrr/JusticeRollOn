#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

This script serves as the entry point for running Django management commands
(such as runserver, migrate, createsuperuser, etc.) from the command line.
It sets up the necessary environment and delegates execution to Django's
management utility.
"""

import os
import sys


def main() -> None:
    """Execute Django management commands from the command line.

    This function configures the Django settings module and then hands over
    control to Django's management utility, which parses the command-line
    arguments and runs the appropriate command.

    Raises:
        ImportError: If Django is not installed or not available in the current
                     Python environment.
    """
    # Set the default settings module for the Django project.
    # This allows Django to locate the project's settings without requiring
    # the DJANGO_SETTINGS_MODULE environment variable to be explicitly set.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'justice_rollon.settings')

    try:
        # Import and execute Django's command-line management utility.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Provide a clear, user-friendly error message if Django cannot be imported.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Pass the command-line arguments (e.g., ['manage.py', 'runserver']) directly
    # to Django's management system for processing.
    execute_from_command_line(sys.argv)


# Standard Python idiom to ensure the main function runs only when this script
# is executed directly (not when imported as a module).
if __name__ == '__main__':
    main()