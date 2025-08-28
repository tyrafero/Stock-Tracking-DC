from django.core.management.base import BaseCommand
from stock.tasks import send_email_async
from django.conf import settings
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Test async email functionality'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, help='Email address to send test email to', required=True)

    def handle(self, *args, **options):
        recipient = options['to']
        
        self.stdout.write(f'Sending test email to {recipient}...')
        
        # Check if Celery is available
        if getattr(settings, 'CELERY_AVAILABLE', False):
            try:
                # Send test email asynchronously
                task = send_email_async.delay(
                    subject='Test Email from Stock Management System',
                    message='This is a test email to verify async email functionality.',
                    html_message='<h2>Test Email</h2><p>This is a test email to verify async email functionality.</p>',
                    from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                    recipient_list=[recipient],
                    fail_silently=False,
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Email queued successfully! Task ID: {task.id}')
                )
                self.stdout.write(
                    'Check your Celery worker logs to see the email processing status.'
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Async email failed: {e}. Falling back to synchronous email.')
                )
                # Fall back to synchronous email
                send_mail(
                    subject='Test Email from Stock Management System',
                    message='This is a test email to verify email functionality.',
                    html_message='<h2>Test Email</h2><p>This is a test email to verify email functionality.</p>',
                    from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                    recipient_list=[recipient],
                    fail_silently=False,
                )
                self.stdout.write(
                    self.style.SUCCESS('Email sent synchronously!')
                )
        else:
            # Send email synchronously if Celery is not available
            self.stdout.write('Celery/Redis not available. Sending email synchronously...')
            send_mail(
                subject='Test Email from Stock Management System',
                message='This is a test email to verify email functionality.',
                html_message='<h2>Test Email</h2><p>This is a test email to verify email functionality.</p>',
                from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS('Email sent synchronously!')
            )