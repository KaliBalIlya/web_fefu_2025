#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    
    # Check if we're in production
    is_production = os.path.exists('/var/www/fefu_lab')
    
    if is_production:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_2025.settings_production')
        # Load environment variables from .env file
        env_path = Path(__file__).resolve().parent / '.env'
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_2025.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
