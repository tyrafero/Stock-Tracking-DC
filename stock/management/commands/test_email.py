from django.core.management.base import BaseCommand
from stock.tasks import send_email_async
from django.conf import settings

class Command(BaseCommand):
    help = 'Test async email functionality'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, help='Email address to send test email to', required=True)

    def handle(self, *args, **options):
        recipient = options['to']
        
        self.stdout.write(f'Sending test email to {recipient}...')
        
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