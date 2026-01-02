#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/home/vboxuser/Documents/stock-management-system')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_management_system.settings')
django.setup()

from django.contrib.auth.models import User
from stock.models import Notification, StockTransfer

# Get user and existing transfer
user = User.objects.filter(is_active=True).first()
transfer = StockTransfer.objects.filter(status='pending').first()

if not user:
    print("No active users found!")
    sys.exit(1)

if not transfer:
    print("No pending transfers found!")
    sys.exit(1)

print(f"Testing transfer completion notification for user: {user.username}")
print(f"Using transfer: {transfer.id} - {transfer.stock.item_name}")
print(f"Current status: {transfer.status}")

# Count notifications before
before_count = Notification.objects.filter(recipient=user).count()
print(f"Notifications before: {before_count}")

# Complete the transfer
transfer.status = 'completed'
transfer.save()

print(f"Updated transfer status to: {transfer.status}")

# Count notifications after
after_count = Notification.objects.filter(recipient=user).count()
print(f"Notifications after: {after_count}")
print(f"New notifications created: {after_count - before_count}")

# Display the new notifications
if after_count > before_count:
    new_notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:after_count - before_count]
    for notification in new_notifications:
        print(f"✅ {notification.title}")
        print(f"   Type: {notification.notification_type}")
        print(f"   Message: {notification.message}")
else:
    print("❌ No completion notifications were created!")

print("\nTest completed!")