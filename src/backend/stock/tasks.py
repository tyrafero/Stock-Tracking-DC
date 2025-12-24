from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_email_async(self, subject, message, html_message, from_email, recipient_list, fail_silently=False):
    """
    Async task to send emails using Django's send_mail function.
    
    Args:
        subject (str): Email subject
        message (str): Plain text message
        html_message (str): HTML message
        from_email (str): Sender email
        recipient_list (list): List of recipient emails
        fail_silently (bool): Whether to fail silently on errors
    
    Returns:
        dict: Result status and message
    """
    try:
        logger.info(f"Sending email to {recipient_list} with subject: {subject}")
        
        result = send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=fail_silently
        )
        
        if result:
            logger.info(f"Email sent successfully to {recipient_list}")
            return {
                'status': 'success',
                'message': f'Email sent successfully to {len(recipient_list)} recipients',
                'recipients': recipient_list
            }
        else:
            logger.warning(f"Email sending failed for {recipient_list}")
            return {
                'status': 'failed',
                'message': 'Email sending failed',
                'recipients': recipient_list
            }
            
    except Exception as exc:
        error_details = {
            'error_type': type(exc).__name__,
            'error_message': str(exc),
            'recipients': recipient_list,
            'subject': subject,
            'attempt': self.request.retries + 1 if hasattr(self, 'request') else 1
        }
        logger.error(f"Email sending error: {error_details}")
        
        # Log specific network/connection errors
        if 'network is not reachable' in str(exc).lower():
            logger.error("Network connectivity issue - check internet connection and firewall settings")
        elif 'authentication' in str(exc).lower():
            logger.error("SMTP authentication failed - check email credentials")
        elif 'timeout' in str(exc).lower():
            logger.error("SMTP connection timeout - check network latency and server availability")
            
        # Re-raise the exception so Celery can handle retries
        raise self.retry(exc=exc)

@shared_task
def send_purchase_order_email(purchase_order_id):
    """
    Send purchase order email asynchronously.
    
    Args:
        purchase_order_id (int): ID of the purchase order
        
    Returns:
        dict: Result status and message
    """
    try:
        from .models import PurchaseOrder
        
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        
        # Render email template
        email_subject = f"Purchase Order #{purchase_order.reference_number}"
        email_body = render_to_string('emails/purchase_order.html', {
            'purchase_order': purchase_order,
        })
        
        # Prepare recipient list
        recipient_emails = [purchase_order.manufacturer.company_email]
        if purchase_order.manufacturer.additional_email:
            recipient_emails.append(purchase_order.manufacturer.additional_email)
        
        # Send email using the async task
        return send_email_async.delay(
            subject=email_subject,
            message='',
            html_message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=recipient_emails,
            fail_silently=False
        )
        
    except Exception as exc:
        logger.error(f"Purchase order email task failed: {str(exc)}")
        return {
            'status': 'error',
            'message': str(exc)
        }