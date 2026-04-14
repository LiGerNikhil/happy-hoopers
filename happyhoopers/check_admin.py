#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happyhoopers.settings')
django.setup()

from django.contrib.auth.models import User
from arena.models import AdminUser

def check_admin_users():
    """Check existing admin users"""
    print("🔍 Checking admin users...")
    
    # Check all users
    users = User.objects.all()
    print(f"\n📋 Total users: {users.count()}")
    
    for user in users:
        print(f"  👤 Username: {user.username}")
        print(f"     Email: {user.email}")
        print(f"     Is Staff: {user.is_staff}")
        print(f"     Is Superuser: {user.is_superuser}")
        print(f"     Is Active: {user.is_active}")
        
        # Check if AdminUser record exists
        try:
            admin_user = AdminUser.objects.get(user=user)
            print(f"     ✅ AdminUser record exists")
            print(f"     🏷️  Is Super Admin: {admin_user.is_super_admin}")
        except AdminUser.DoesNotExist:
            print(f"     ❌ No AdminUser record found")
        print()
    
    # Check AdminUser records
    admin_users = AdminUser.objects.all()
    print(f"🏢 AdminUser records: {admin_users.count()}")
    
    for admin_user in admin_users:
        print(f"  👤 User: {admin_user.user.username}")
        print(f"     Super Admin: {admin_user.is_super_admin}")
        print(f"     Created: {admin_user.created_at}")

def create_missing_admin_records():
    """Create AdminUser records for existing superusers"""
    print("\n🔧 Creating missing AdminUser records...")
    
    superusers = User.objects.filter(is_superuser=True)
    for user in superusers:
        try:
            AdminUser.objects.get(user=user)
            print(f"  ✅ {user.username} already has AdminUser record")
        except AdminUser.DoesNotExist:
            AdminUser.objects.create(user=user, is_super_admin=True)
            print(f"  ✅ Created AdminUser record for {user.username}")

if __name__ == '__main__':
    check_admin_users()
    create_missing_admin_records()
    print("\n🎉 Check complete!")
