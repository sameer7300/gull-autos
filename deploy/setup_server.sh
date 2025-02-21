#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    mysql-server \
    libmysqlclient-dev \
    nginx \
    git \
    supervisor \
    build-essential \
    pkg-config

# Install virtualenv
sudo pip3 install virtualenv

# Create project directory
sudo mkdir -p /var/www/gull-autos
sudo chown ubuntu:ubuntu /var/www/gull-autos

# Create virtual environment
cd /var/www/gull-autos
virtualenv venv
source venv/bin/activate

# Install project dependencies
pip install -r requirements.txt

# Setup MySQL
sudo mysql_secure_installation

# Create MySQL database and user
sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${RDS_DB_NAME};"
sudo mysql -e "CREATE USER IF NOT EXISTS '${RDS_USERNAME}'@'localhost' IDENTIFIED BY '${RDS_PASSWORD}';"
sudo mysql -e "GRANT ALL PRIVILEGES ON ${RDS_DB_NAME}.* TO '${RDS_USERNAME}'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Configure Nginx
sudo rm -f /etc/nginx/sites-enabled/default
sudo tee /etc/nginx/sites-available/gull-autos << EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/gull-autos;
    }

    location /media/ {
        root /var/www/gull-autos;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/gull-autos /etc/nginx/sites-enabled/

# Configure Gunicorn
sudo tee /etc/supervisor/conf.d/gull-autos.conf << EOF
[program:gull-autos]
directory=/var/www/gull-autos
command=/var/www/gull-autos/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock gull_autos.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/gull-autos.err.log
stdout_logfile=/var/log/gull-autos.out.log
user=ubuntu
group=www-data
environment=
    DJANGO_SETTINGS_MODULE="gull_autos.settings_prod",
    DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY}",
    RDS_DB_NAME="${RDS_DB_NAME}",
    RDS_USERNAME="${RDS_USERNAME}",
    RDS_PASSWORD="${RDS_PASSWORD}",
    RDS_HOSTNAME="localhost",
    RDS_PORT="3306"

[group:gull-autos]
programs=gull-autos
EOF

# Create necessary directories
mkdir -p /var/www/gull-autos/static
mkdir -p /var/www/gull-autos/media

# Set permissions
sudo chown -R ubuntu:www-data /var/www/gull-autos
sudo chmod -R 755 /var/www/gull-autos

# Restart services
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart gull-autos
