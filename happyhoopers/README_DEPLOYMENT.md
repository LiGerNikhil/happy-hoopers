# Happy Hoopers Production Deployment Guide

## Server Information
- **VPS IP**: 187.127.147.152
- **Domain**: happyhoopers.in
- **Database**: SQLite (for low traffic)

## Pre-Deployment Checklist

### 1. Local Setup
- [ ] Update `settings.py` with production settings (done)
- [ ] Create `.env` file with environment variables (done)
- [ ] Update `requirements.txt` with dependencies (done)
- [ ] Test locally with `DEBUG=False`

### 2. Files Ready for Upload
- [ ] `settings.py` (production-ready)
- [ ] `.env` (environment variables)
- [ ] `requirements.txt` (dependencies)
- [ ] `gunicorn_config.py` (WSGI config)
- [ ] `happyhoopers.service` (systemd service)
- [ ] `nginx.conf` (Nginx config)
- [ ] `deploy.sh` (deployment script)
- [ ] `db.sqlite3` (database file)
- [ ] `static/` and `media/` folders

## Deployment Steps

### 1. Connect to VPS
```bash
ssh root@187.127.147.152
```

### 2. Upload Project Files
```bash
# Option 1: Using SCP
scp -r /path/to/happyhoopers root@187.127.147.152:/var/www/

# Option 2: Using Git (recommended)
git clone https://github.com/yourusername/happyhoopers.git /var/www/happyhoopers
```

### 3. Run Deployment Script
```bash
cd /var/www/happyhoopers
chmod +x deploy.sh
./deploy.sh
```

### 4. Manual Steps (if needed)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start services
sudo systemctl start happyhoopers
sudo systemctl restart nginx
```

## Post-Deployment Verification

### Check Service Status
```bash
sudo systemctl status happyhoopers
sudo systemctl status nginx
```

### Check Logs
```bash
# Gunicorn logs
sudo journalctl -u happyhoopers -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Test Website
- Visit: http://happyhoopers.in
- Check static files are loading
- Test admin panel: http://happyhoopers.in/admin

## Important Notes

### Security
- SECRET_KEY is in `.env` file
- DEBUG is set to False
- Security headers configured
- SSL recommended for production

### Database
- SQLite database: `db.sqlite3`
- Backup regularly: `cp db.sqlite3 db_backup.sqlite3`
- For higher traffic, consider PostgreSQL

### Performance
- Gunicorn workers: CPU cores * 2 + 1
- Nginx static file serving
- Gzip compression enabled
- Browser caching configured

### Troubleshooting
```bash
# Restart services
sudo systemctl restart happyhoopers
sudo systemctl restart nginx

# Check permissions
sudo chown -R www-data:www-data /var/www/happyhoopers
sudo chmod -R 755 /var/www/happyhoopers

# Test Django application
cd /var/www/happyhoopers
source venv/bin/activate
python manage.py check --deploy
```

## GitHub Upload Instructions

### 1. Create Repository
```bash
git init
git add .
git commit -m "Initial commit - Production ready"
git branch -M main
git remote add origin https://github.com/yourusername/happyhoopers.git
git push -u origin main
```

### 2. Exclude Sensitive Files
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "db.sqlite3" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
```

### 3. Upload to GitHub
```bash
git add .
git commit -m "Production ready setup"
git push origin main
```

## Domain Configuration

### DNS Settings for happyhoopers.in
- **A Record**: @ -> 187.127.147.152
- **A Record**: www -> 187.127.147.152
- **Optional**: CAA records for SSL certificates

### SSL Certificate (Recommended)
```bash
# Install Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d happyhoopers.in -d www.happyhoopers.in

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring

### Basic Monitoring
```bash
# System resources
htop
df -h
free -h

# Application logs
sudo journalctl -u happyhoopers -f
sudo tail -f /var/log/nginx/access.log
```

### Backup Script
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/happyhoopers_$DATE.tar.gz /var/www/happyhoopers
```

Your Django project is now production-ready for deployment!
