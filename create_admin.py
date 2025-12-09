#!/usr/bin/env python
"""
自动创建管理员账号的脚本
在 Render 部署后会自动运行
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hippocampus_project.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    """创建默认管理员账号（如果不存在）"""
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f'✅ 成功创建管理员账号: {username}')
    else:
        print(f'ℹ️  管理员账号已存在: {username}')

if __name__ == '__main__':
    create_admin()
