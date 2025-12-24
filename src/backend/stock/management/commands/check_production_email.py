from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
import logging

class Command(BaseCommand):
    help = 'Test email in production environment with safe fallback'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, help='Test email recipient', default='test@example.com')

    def handle(self, *args, **options):
        self.stdout.write('🧪 Production Email Test\n')
        
        # Log environment info (safe for production)
        self.stdout.write('📋 Environment Check:')
        self.stdout.write(f'  DEBUG: {settings.DEBUG}')
        self.stdout.write(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER[:5]}***@{settings.EMAIL_HOST_USER.split("@")[1] if settings.EMAIL_HOST_USER else "None"}')
        self.stdout.write('')

        # Test email with comprehensive error handling
        try:
            self.stdout.write('📧 Attempting to send test email...')
            
            result = send_mail(
                subject='Production Email Test',
                message='This is a test email from Railway production.',
                html_message='<h2>Production Email Test</h2><p>This is a test email from Railway production.</p>',
                from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                recipient_list=[options['to']],
                fail_silently=False,
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS('✅ Email sent successfully!'))
                self.stdout.write(f'   Sent to: {options["to"]}')
            else:
                self.stdout.write(self.style.WARNING('⚠️  Email function returned 0 (may indicate failure)'))
                
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            self.stdout.write(self.style.ERROR(f'❌ Email failed: {error_type}'))
            self.stdout.write(self.style.ERROR(f'   Message: {error_msg}'))
            
            # Provide specific guidance based on error
            if 'network is not reachable' in error_msg.lower():
                self.stdout.write(self.style.WARNING('\n💡 Network Issue Detected:'))
                self.stdout.write('   - Railway may be blocking SMTP connections')
                self.stdout.write('   - Consider using SendGrid, Mailgun, or AWS SES')
                self.stdout.write('   - Check Railway network policies')
                
            elif 'authentication' in error_msg.lower():
                self.stdout.write(self.style.WARNING('\n💡 Authentication Issue Detected:'))
                self.stdout.write('   - Gmail app password may have expired')
                self.stdout.write('   - Check EMAIL_PASSWORD environment variable')
                self.stdout.write('   - Regenerate Gmail app password')
                
            elif 'timeout' in error_msg.lower():
                self.stdout.write(self.style.WARNING('\n💡 Timeout Issue Detected:'))
                self.stdout.write('   - Railway may have strict network timeouts')
                self.stdout.write('   - Try alternative email service')
                
            self.stdout.write('\n🔧 Recommended Actions:')
            self.stdout.write('   1. Add SENDGRID_API_KEY to Railway environment')
            self.stdout.write('   2. Or use Railway\'s email addon if available')
            self.stdout.write('   3. Or switch to console backend temporarily')