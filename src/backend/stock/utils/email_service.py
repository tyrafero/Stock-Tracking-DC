"""
Railway-friendly email service with automatic fallback
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail.backends.console import EmailBackend as ConsoleBackend

logger = logging.getLogger(__name__)

class RailwayEmailService:
    """
    Email service that handles Railway's network restrictions gracefully
    """
    
    @staticmethod
    def send_email(subject, message, html_message, from_email, recipient_list, fail_silently=False):
        """
        Send email with automatic fallback for production issues
        """
        try:
            # Try normal email sending first
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
                    'success': True,
                    'message': f'Email sent to {len(recipient_list)} recipients',
                    'method': 'smtp'
                }
            else:
                raise Exception("send_mail returned 0")
                
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Email sending failed: {e}")
            
            # If it's a network issue in production, log instead of crash
            if not settings.DEBUG and ('network' in error_msg or 'timeout' in error_msg or 'reachable' in error_msg):
                # Log essential email details only (not full HTML)
                console_message = f"""
                EMAIL NOTIFICATION LOGGED (Network Restricted):
                To: {', '.join(recipient_list)}
                From: {from_email}
                Subject: {subject}
                Status: Failed to send via SMTP - {str(e)[:100]}...
                Note: Purchase order status updated successfully
                """
                logger.warning(console_message)
                
                return {
                    'success': False,
                    'message': 'Email could not be sent due to network restrictions, but purchase order was updated successfully',
                    'method': 'console_fallback',
                    'logged': True
                }
            else:
                # Re-raise in development or for non-network errors
                raise e

def send_purchase_order_email_safe(purchase_order, recipient_emails, email_subject, email_body):
    """
    Safe wrapper for sending purchase order emails
    """
    service = RailwayEmailService()
    
    try:
        result = service.send_email(
            subject=email_subject,
            message='',
            html_message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=recipient_emails,
            fail_silently=False
        )
        
        if result['success']:
            return f"Purchase Order {purchase_order.reference_number} sent successfully via {result['method']}!"
        else:
            return f"Purchase Order {purchase_order.reference_number} updated. {result['message']}"
            
    except Exception as e:
        logger.error(f"Purchase order email failed: {e}")
        return f"Purchase Order {purchase_order.reference_number} updated, but email failed: {str(e)}"