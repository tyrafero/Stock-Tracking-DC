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
from stock.models import Notification, Stock, StockTransfer

# Get user and a stock item for testing
user = User.objects.filter(is_active=True).first()
stock_item = Stock.objects.first()

if not user:
    print("No active users found!")
    sys.exit(1)

if not stock_item:
    print("No stock items found!")
    sys.exit(1)

print(f"Testing stock transfer notification for user: {user.username}")
print(f"Using stock item: {stock_item.item_name}")

# Count notifications before
before_count = Notification.objects.filter(recipient=user).count()
print(f"Notifications before: {before_count}")

# Create a stock transfer
# First we need to get a destination store or create one
to_store = stock_item.location  # For simplicity, use same store as destination

transfer = StockTransfer.objects.create(
    stock=stock_item,
    quantity=2,
    from_location=stock_item.location,
    to_location=to_store,
    transfer_reason="Testing notifications",
    created_by=user
)

print(f"Created stock transfer: {transfer.id}")

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
    print("❌ No notifications were created!")

# Now test completing the transfer
print("\n--- Testing transfer completion ---")
before_count = after_count

# Update transfer status to completed
transfer.status = 'completed'
transfer.save()

print(f"Updated transfer status to: {transfer.status}")

# Count notifications after completion
after_count = Notification.objects.filter(recipient=user).count()
print(f"Notifications after completion: {after_count}")
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