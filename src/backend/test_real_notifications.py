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
    PurchaseOrder, PurchaseOrderItem, Stock, Category
)

# Get user
user = User.objects.filter(is_active=True).first()
if not user:
    print("No active users found!")
    sys.exit(1)

print(f"Creating notifications with real related objects for: {user.username}")

# Get or create test data
manufacturer, _ = Manufacturer.objects.get_or_create(
    company_name="Apple Inc",
    defaults={
        'company_email': 'orders@apple.com',
        'street_address': '1 Apple Park Way',
        'city': 'Cupertino',
        'country': 'USA',
        'region': 'California',
        'postal_code': '95014',
        'company_telephone': '408-996-1010'
    }
)

delivery_person, _ = DeliveryPerson.objects.get_or_create(
    name="John Smith",
    defaults={'phone_number': '555-0123'}
)

store, _ = Store.objects.get_or_create(
    name="Main Store",
    defaults={'location': 'Downtown'}
)

category, _ = Category.objects.get_or_create(group="Electronics")

# Create a real purchase order
po = PurchaseOrder.objects.create(
    manufacturer=manufacturer,
    delivery_person=delivery_person,
    store=store,
    creating_store=store,
    created_by=user,
    note_for_manufacturer="Real purchase order for testing notifications"
)

# Add items to the PO
po_item1 = PurchaseOrderItem.objects.create(
    purchase_order=po,
    product="iPhone 15 Pro 256GB",
    price_inc=1199.00,
    quantity=10
)

po_item2 = PurchaseOrderItem.objects.create(
    purchase_order=po,
    product="MacBook Pro 14-inch",
    price_inc=2499.00,
    quantity=5
)

print(f"Created purchase order: {po.reference_number}")

# Create a stock item for low stock notification
stock_item = Stock.objects.create(
    category=category,
    item_name="iPad Pro 12.9-inch",
    quantity=2,
    re_order=10,
    location=store,
    created_by=user.username
)

print(f"Created stock item: {stock_item.item_name} with quantity {stock_item.quantity}")

# Create notification with real related objects
notification = Notification.objects.create(
    recipient=user,
    notification_type='purchase_order_created',
    title=f'Purchase Order Created: {po.reference_number}',
    message=f'Purchase order {po.reference_number} has been created for {manufacturer.company_name} with {po.items.count()} items.',
    priority='medium',
    related_object_type='purchase_order',
    related_object_id=po.id
)

print(f"Created notification with PO link: {notification.title}")

# Create stock notification
stock_notification = Notification.objects.create(
    recipient=user,
    notification_type='stock_low',
    title=f'Low Stock Alert: {stock_item.item_name}',
    message=f'{stock_item.item_name} is running low with only {stock_item.quantity} units available (reorder level: {stock_item.re_order}).',
    priority='high',
    related_object_type='stock',
    related_object_id=stock_item.id
)

print(f"Created stock notification with link: {stock_notification.title}")

print("✅ Created notifications with real related objects for testing click functionality!")