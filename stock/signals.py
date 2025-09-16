"""
Django signals for stock app
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import (
    UserRole, PurchaseOrder, StockTransfer, CommittedStock, Stock, 
    StockAudit, Invoice, Payment, StockReservation, 
    PurchaseOrderReceiving, Notification
)


@receiver(post_save, sender=User)
def create_user_role(sender, instance, created, **kwargs):
    """Create UserRole with 'pending' status for new users"""
    if created:
        # Check if UserRole doesn't already exist (in case of data migrations etc)
        if not hasattr(instance, 'role'):
            UserRole.objects.create(
                user=instance,
                role='pending'
            )


@receiver(post_save, sender=User)
def save_user_role(sender, instance, **kwargs):
    """Ensure UserRole is saved when User is saved"""
    if hasattr(instance, 'role'):
        instance.role.save()


# =============================================================================
# NOTIFICATION SIGNALS
# =============================================================================

@receiver(post_save, sender=PurchaseOrder)
def create_purchase_order_notification(sender, instance, created, **kwargs):
    """Create notification when purchase order is created or status changes"""
    if created:
        # PO Created
        recipients = Notification.get_recipients_for_activity('purchase_order_created', instance)
        if recipients:
            Notification.create_notification(
                recipients=recipients,
                notification_type='purchase_order_created',
                title=f'New Purchase Order Created: {instance.reference_number}',
                message=f'Purchase order {instance.reference_number} has been created for {instance.manufacturer.company_name}.',
                related_object=instance,
                priority='medium'
            )
    else:
        # Check for status changes
        if hasattr(instance, '_state') and instance._state.adding is False:
            try:
                old_instance = PurchaseOrder.objects.get(pk=instance.pk)
            except PurchaseOrder.DoesNotExist:
                return
            
            # Status changed to confirmed
            if old_instance.status != 'confirmed' and instance.status == 'confirmed':
                recipients = Notification.get_recipients_for_activity('purchase_order_confirmed', instance)
                if recipients:
                    Notification.create_notification(
                        recipients=recipients,
                        notification_type='purchase_order_confirmed',
                        title=f'Purchase Order Confirmed: {instance.reference_number}',
                        message=f'Purchase order {instance.reference_number} has been confirmed.',
                        related_object=instance,
                        priority='medium'
                    )


@receiver(post_save, sender=StockTransfer)
def create_stock_transfer_notification(sender, instance, created, **kwargs):
    """Create notification when stock transfer is created or completed"""
    if created:
        # Transfer initiated
        recipients = Notification.get_recipients_for_activity('stock_transfer_initiated', instance)
        if recipients:
            Notification.create_notification(
                recipients=recipients,
                notification_type='stock_transfer_initiated',
                title=f'Stock Transfer Initiated: {instance.stock.item_name}',
                message=f'Transfer of {instance.quantity} units of {instance.stock.item_name} from {instance.from_location} to {instance.to_location} has been initiated.',
                related_object=instance,
                priority='medium'
            )
    else:
        # Check for status changes - use pre_save to capture old status
        if instance.status == 'completed':
            # Check if this is a recent status change by checking if there's already a completion notification
            existing_completion = Notification.objects.filter(
                notification_type='stock_transfer_completed',
                related_object_type='stock_transfer',
                related_object_id=instance.id
            ).exists()
            
            # Only create notification if one doesn't already exist
            if not existing_completion:
                recipients = Notification.get_recipients_for_activity('stock_transfer_completed', instance)
                if recipients:
                    Notification.create_notification(
                        recipients=recipients,
                        notification_type='stock_transfer_completed',
                        title=f'Stock Transfer Completed: {instance.stock.item_name}',
                        message=f'Transfer of {instance.quantity} units of {instance.stock.item_name} has been completed.',
                        related_object=instance,
                        priority='medium'
                    )


@receiver(post_save, sender=CommittedStock)
def create_stock_commitment_notification(sender, instance, created, **kwargs):
    """Create notification when stock is committed"""
    if created:
        recipients = Notification.get_recipients_for_activity('stock_committed', instance)
        if recipients:
            Notification.create_notification(
                recipients=recipients,
                notification_type='stock_committed',
                title=f'Stock Committed: {instance.stock.item_name}',
                message=f'{instance.quantity} units of {instance.stock.item_name} have been committed for order {instance.customer_order_number}.',
                related_object=instance,
                priority='medium'
            )


@receiver(post_save, sender=StockReservation)
def create_stock_reservation_notification(sender, instance, created, **kwargs):
    """Create notification when stock reservation is created"""
    if created:
        recipients = Notification.get_recipients_for_activity('reservation_created', instance)
        if recipients:
            Notification.create_notification(
                recipients=recipients,
                notification_type='reservation_created',
                title=f'Stock Reserved: {instance.stock.item_name}',
                message=f'{instance.quantity} units of {instance.stock.item_name} have been reserved ({instance.get_reservation_type_display()}).',
                related_object=instance,
                priority='medium'
            )


@receiver(post_save, sender=StockAudit)
def create_stock_audit_notification(sender, instance, created, **kwargs):
    """Create notification when stock audit is started or completed"""
    if created:
        recipients = Notification.get_recipients_for_activity('stock_audit_started', instance)
        if recipients:
            Notification.create_notification(
                recipients=recipients,
                notification_type='stock_audit_started',
                title=f'Stock Audit Started: {instance.audit_reference}',
                message=f'Stock audit "{instance.title}" has been started.',
                related_object=instance,
                priority='medium'
            )
    else:
        # Check for status changes
        if hasattr(instance, '_state') and instance._state.adding is False:
            try:
                old_instance = StockAudit.objects.get(pk=instance.pk)
            except StockAudit.DoesNotExist:
                return
            
            # Status changed to completed
            if old_instance.status != 'completed' and instance.status == 'completed':
                recipients = Notification.get_recipients_for_activity('stock_audit_completed', instance)
                if recipients:
                    Notification.create_notification(
                        recipients=recipients,
                        notification_type='stock_audit_completed',
                        title=f'Stock Audit Completed: {instance.audit_reference}',
                        message=f'Stock audit "{instance.title}" has been completed.',
                        related_object=instance,
                        priority='high' if instance.has_variances else 'medium'
                    )


@receiver(post_save, sender=Invoice)
def create_invoice_notification(sender, instance, created, **kwargs):
    """Create notification when invoice is created"""
    if created:
        recipients = Notification.get_recipients_for_activity('invoice_created', instance)
        if recipients:
            Notification.create_notification(
                recipients=recipients,
                notification_type='invoice_created',
                title=f'New Invoice: {instance.invoice_number}',
                message=f'Invoice {instance.invoice_number} for ${instance.invoice_total} has been created for PO {instance.purchase_order.reference_number}.',
                related_object=instance,
                priority='medium'
            )


@receiver(post_save, sender=Payment)
def create_payment_notification(sender, instance, created, **kwargs):
    """Create notification when payment is made"""
    if created:
        recipients = Notification.get_recipients_for_activity('payment_made', instance)
        if recipients:
            Notification.create_notification(
                recipients=recipients,
                notification_type='payment_made',
                title=f'Payment Made: ${instance.payment_amount}',
                message=f'Payment of ${instance.payment_amount} has been made for invoice {instance.invoice.invoice_number}.',
                related_object=instance,
                priority='medium'
            )


@receiver(post_save, sender=PurchaseOrderReceiving)
def create_po_receiving_notification(sender, instance, created, **kwargs):
    """Create notification when PO items are received"""
    if created:
        recipients = Notification.get_recipients_for_activity('po_items_received', instance)
        if recipients:
            Notification.create_notification(
                recipients=recipients,
                notification_type='po_items_received',
                title=f'Items Received: {instance.purchase_order_item.product}',
                message=f'{instance.quantity_received} units of {instance.purchase_order_item.product} have been received for PO {instance.purchase_order_item.purchase_order.reference_number}.',
                related_object=instance.purchase_order_item.purchase_order,
                priority='medium'
            )


@receiver(post_save, sender=Stock)
def check_low_stock_notification(sender, instance, created, **kwargs):
    """Create notification for low stock alerts"""
    if not created and instance.is_low_stock:
        # Check if we already have a recent low stock notification for this item
        from django.utils import timezone
        from datetime import timedelta
        
        recent_notification = Notification.objects.filter(
            notification_type='stock_low',
            related_object_type='stock',
            related_object_id=instance.id,
            created_at__gte=timezone.now() - timedelta(days=1)  # Don't spam - only once per day
        ).first()
        
        if not recent_notification:
            recipients = Notification.get_recipients_for_activity('stock_low', instance)
            if recipients:
                Notification.create_notification(
                    recipients=recipients,
                    notification_type='stock_low',
                    title=f'Low Stock Alert: {instance.item_name}',
                    message=f'{instance.item_name} is running low with only {instance.available_for_sale} units available (reorder level: {instance.re_order}).',
                    related_object=instance,
                    priority='high'
                )