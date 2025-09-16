#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/home/vboxuser/Documents/stock-management-system')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_management_system.settings')
django.setup()

from stock.models import Notification

# Check notifications
notifications = Notification.objects.all()
print(f"Total notifications: {notifications.count()}")

if notifications.exists():
    print("\nRecent notifications:")
    for notification in notifications.order_by('-created_at')[:5]:
        print(f"- {notification.title} ({notification.priority}) - {notification.recipient.username}")
        print(f"  {notification.message[:80]}...")
        print(f"  Created: {notification.created_at}")
        print()
else:
    print("No notifications found")