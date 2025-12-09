"""
WSGI config for web_2025 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Check if we're in production
is_production = os.path.exists('/var/www/fefu_lab')

if is_production:
    # Load environment variables from .env file
    env_path = Path(__file__).resolve().parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_2025.settings_production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_2025.settings')

application = get_wsgi_application()
