#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happyhoopers.settings')
django.setup()

from django.contrib.auth.models import User
from arena.models import AdminUser

def create_admin_user():
    """Create admin user for dashboard access"""
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    # Create Django user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    # Create admin user record
    admin_user = AdminUser.objects.create(
        user=user,
        is_super_admin=True
    )
    
    print(f"✅ Admin user '{username}' created successfully!")
    print(f"📍 Login URL: http://127.0.0.1:8001/admin-login/")
    print(f"👤 Username: {username}")
    print(f"🔐 Password: [Your entered password]")

if __name__ == '__main__':
    create_admin_user()
