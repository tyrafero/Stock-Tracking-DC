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
from stock.models import (
    Notification, Manufacturer, DeliveryPerson, Store, 
    PurchaseOrder, PurchaseOrderItem
)

# Get or create test data
user = User.objects.filter(is_active=True).first()
if not user:
    print("No active users found!")
    sys.exit(1)

# Get or create manufacturer
manufacturer, created = Manufacturer.objects.get_or_create(
    company_name="Test Electronics Inc",
    defaults={
        'company_email': 'test@electronics.com',
        'street_address': '123 Test St',
        'city': 'Test City',
        'country': 'Test Country',
        'region': 'Test Region',
        'postal_code': '12345',
        'company_telephone': '123-456-7890'
    }
)

# Get or create delivery person
delivery_person, created = DeliveryPerson.objects.get_or_create(
    name="Test Delivery Person",
    defaults={'phone_number': '123-456-7890'}
)

# Get or create store
store, created = Store.objects.get_or_create(
    name="Test Store",
    defaults={'location': 'Test Location'}
)

print(f"Testing notification triggers for user: {user.username}")

# Count notifications before
before_count = Notification.objects.filter(recipient=user).count()
print(f"Notifications before: {before_count}")

# Create a purchase order to trigger notifications
po = PurchaseOrder.objects.create(
    manufacturer=manufacturer,
    delivery_person=delivery_person,
    store=store,
    creating_store=store,
    created_by=user,
    note_for_manufacturer="Test purchase order for notification testing"
)

# Add an item to the PO
po_item = PurchaseOrderItem.objects.create(
    purchase_order=po,
    product="Test Product - Notification Trigger",
    price_inc=100.00,
    quantity=5
)

print(f"Created purchase order: {po.reference_number}")

# Count notifications after
after_count = Notification.objects.filter(recipient=user).count()
print(f"Notifications after: {after_count}")
print(f"New notifications created: {after_count - before_count}")

# Display the new notifications
new_notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:after_count - before_count]
for notification in new_notifications:
    print(f"- {notification.title}")
    print(f"  Type: {notification.notification_type}")
    print(f"  Priority: {notification.priority}")
    print(f"  Message: {notification.message}")
    print()

print("Test completed successfully!")