import os
import sys

# Add your project directory to the sys.path
path = '/home/your_pythonanywhere_username/gull-autos'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'gull_autos.settings'
os.environ['PYTHONPATH'] = '/home/your_pythonanywhere_username/gull-autos'

# Import your application
from gull_autos.wsgi import application  # noqa
