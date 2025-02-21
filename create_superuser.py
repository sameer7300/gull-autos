import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gull_autos.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gullautos.com', 'admin123')
