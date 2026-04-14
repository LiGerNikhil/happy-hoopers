#!/bin/bash

# Happy Hoopers Deployment Script
# Run this on your VPS (187.127.147.152)

echo "Starting Happy Hoopers deployment..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx sqlite3 git

# Create project directory
sudo mkdir -p /var/www/happyhoopers
sudo chown $USER:$USER /var/www/happyhoopers

# Navigate to project directory
cd /var/www/happyhoopers

# Clone your repository (replace with your actual repo URL)
# git clone https://github.com/yourusername/happyhoopers.git .

# For now, copy files manually
echo "Please copy your project files to /var/www/happyhoopers"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Set up database (SQLite)
python manage.py migrate

# Create superuser (optional)
# python manage.py createsuperuser

# Set permissions
sudo chown -R www-data:www-data /var/www/happyhoopers
sudo chmod -R 755 /var/www/happyhoopers

# Copy systemd service file
sudo cp happyhoopers.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable happyhoopers
sudo systemctl start happyhoopers

# Copy Nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/happyhoopers
sudo ln -s /etc/nginx/sites-available/happyhoopers /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Configure firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

echo "Deployment completed!"
echo "Your site should be available at: http://happyhoopers.in"
echo "Check service status: sudo systemctl status happyhoopers"
echo "Check logs: sudo journalctl -u happyhoopers"
