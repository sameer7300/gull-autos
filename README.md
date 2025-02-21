# Gull Autos Website

A modern website for Gull Autos built with Django, Three.js, and Framer Motion.

## Features

- Interactive 3D product visualization using Three.js
- Smooth animations and transitions with Framer Motion
- Responsive design with Tailwind CSS
- Product catalog with categories and filters
- Blog system
- Contact form
- Admin panel for content management

## Requirements

- Python 3.8+
- Django 5.0+
- Node.js (for frontend development)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gull-autos.git
cd gull-autos
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The website will be available at http://localhost:8000

## Project Structure

- `core/` - Main Django app containing models, views, and templates
- `static/` - Static files (CSS, JavaScript, images)
  - `css/` - Custom CSS styles
  - `js/` - JavaScript files including Three.js and Framer Motion animations
- `templates/` - HTML templates
- `media/` - User-uploaded files

## Development

1. Make migrations after model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

2. Collect static files:
```bash
python manage.py collectstatic
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
