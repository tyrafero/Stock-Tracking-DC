from django import template

register = template.Library()

@register.filter
def get_notification_icon(notification_type):
    """Get icon class for notification type"""
    icon_mapping = {
        'purchase_order_created': 'ni ni-cart',
        'purchase_order_confirmed': 'ni ni-check-circle',
        'stock_transfer_initiated': 'ni ni-swap',
        'stock_transfer_completed': 'ni ni-check',
        'stock_committed': 'ni ni-lock',
        'stock_received': 'ni ni-inbox',
        'po_items_received': 'ni ni-package',
        'stock_audit_started': 'ni ni-clipboard',
        'stock_audit_completed': 'ni ni-check-circle',
        'invoice_created': 'ni ni-file-text',
        'payment_made': 'ni ni-money',
        'stock_low': 'ni ni-alert-circle',
        'reservation_created': 'ni ni-clock',
        'reservation_expired': 'ni ni-alert-triangle',
    }
    return icon_mapping.get(notification_type, 'ni ni-bell')