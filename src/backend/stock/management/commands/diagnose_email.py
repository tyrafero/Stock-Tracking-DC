from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import socket
import smtplib
from email.mime.text import MIMEText

class Command(BaseCommand):
    help = 'Diagnose email connectivity issues'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Email Connectivity Diagnostics\n')
        
        # 1. Check basic settings
        self.stdout.write('📋 Email Settings:')
        self.stdout.write(f'  EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'  EMAIL_TIMEOUT: {getattr(settings, "EMAIL_TIMEOUT", "Not set")}')
        self.stdout.write('')
        
        # 2. Test network connectivity
        self.stdout.write('🌐 Network Connectivity Tests:')
        self._test_network_connectivity()
        self.stdout.write('')
        
        # 3. Test SMTP connection
        self.stdout.write('📧 SMTP Connection Test:')
        self._test_smtp_connection()
        self.stdout.write('')
        
        # 4. Test Django email sending
        self.stdout.write('🚀 Django Email Test:')
        self._test_django_email()

    def _test_network_connectivity(self):
        """Test basic network connectivity to Gmail"""
        try:
            # Test DNS resolution
            self.stdout.write('  Testing DNS resolution for smtp.gmail.com...')
            socket.gethostbyname('smtp.gmail.com')
            self.stdout.write(self.style.SUCCESS('  ✅ DNS resolution: OK'))
            
            # Test port connectivity
            self.stdout.write('  Testing port 587 connectivity...')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex(('smtp.gmail.com', 587))
            sock.close()
            
            if result == 0:
                self.stdout.write(self.style.SUCCESS('  ✅ Port 587: OK'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ Port 587: Connection failed (error code: {result})'))
                
        except socket.gaierror as e:
            self.stdout.write(self.style.ERROR(f'  ❌ DNS resolution failed: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Network test failed: {e}'))

    def _test_smtp_connection(self):
        """Test raw SMTP connection"""
        try:
            self.stdout.write('  Attempting SMTP connection...')
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=30)
            
            self.stdout.write('  Starting TLS...')
            server.starttls()
            
            self.stdout.write('  Attempting login...')
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            
            self.stdout.write(self.style.SUCCESS('  ✅ SMTP connection: OK'))
            server.quit()
            
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Authentication failed: {e}'))
        except smtplib.SMTPConnectError as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Connection failed: {e}'))
        except smtplib.SMTPServerDisconnected as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Server disconnected: {e}'))
        except socket.timeout as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Connection timeout: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ SMTP error: {e}'))

    def _test_django_email(self):
        """Test Django email sending"""
        try:
            self.stdout.write('  Testing Django send_mail...')
            
            # Don't actually send, just test the connection
            from django.core.mail import get_connection
            connection = get_connection()
            connection.open()
            self.stdout.write(self.style.SUCCESS('  ✅ Django email connection: OK'))
            connection.close()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Django email failed: {e}'))