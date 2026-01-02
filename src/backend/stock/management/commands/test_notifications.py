from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from stock.models import Notification, PurchaseOrder, Manufacturer, DeliveryPerson, Store


class Command(BaseCommand):
    help = 'Create test notifications for development'

    def handle(self, *args, **options):
        # Get a test user (admin or first user)
        user = User.objects.filter(is_active=True).first()
        if not user:
            self.stdout.write(self.style.ERROR('No active users found. Please create a user first.'))
            return

        self.stdout.write(f'Creating test notifications for user: {user.username}')

        # Create test notifications of different types and priorities
        test_notifications = [
            {
                'notification_type': 'purchase_order_created',
                'title': 'New Purchase Order Created: PO-TEST-001',
                'message': 'Purchase order PO-TEST-001 has been created for ABC Electronics.',
                'priority': 'medium'
            },
            {
                'notification_type': 'stock_low',
                'title': 'Low Stock Alert: iPhone 15 Pro',
                'message': 'iPhone 15 Pro is running low with only 2 units available (reorder level: 5).',
                'priority': 'high'
            },
            {
                'notification_type': 'stock_transfer_completed',
                'title': 'Stock Transfer Completed: MacBook Pro',
                'message': 'Transfer of 3 units of MacBook Pro has been completed from Warehouse to Store A.',
                'priority': 'medium'
            },
            {
                'notification_type': 'invoice_created',
                'title': 'New Invoice: INV-2024-001',
                'message': 'Invoice INV-2024-001 for $2,500.00 has been created for PO-TEST-001.',
                'priority': 'medium'
            },
            {
                'notification_type': 'stock_committed',
                'title': 'Stock Committed: iPad Pro',
                'message': '2 units of iPad Pro have been committed for order ORD-001.',
                'priority': 'low'
            },
            {
                'notification_type': 'stock_audit_completed',
                'title': 'Stock Audit Completed: AUDIT-2024-001',
                'message': 'Stock audit "Monthly Inventory Check" has been completed with 5 variances found.',
                'priority': 'high'
            }
        ]

        # Create notifications
        for notification_data in test_notifications:
            notification = Notification.objects.create(
                recipient=user,
                **notification_data
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created notification: {notification.title} (Priority: {notification.priority})'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(test_notifications)} test notifications!'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'Note: These are test notifications and may not have valid related objects.'
            )
        )