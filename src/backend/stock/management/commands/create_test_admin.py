from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from stock.models import UserRole

class Command(BaseCommand):
    help = 'Create a test admin user'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin123'
        
        # Create or get the admin user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created new admin user: {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Admin user already exists: {username}')
            )
        
        # Create or get the user role
        role, role_created = UserRole.objects.get_or_create(
            user=user,
            defaults={
                'role': 'admin',
                'created_by': user,
            }
        )
        
        if role_created:
            self.stdout.write(
                self.style.SUCCESS(f'Created admin role for user: {username}')
            )
        else:
            # Update role if it exists
            if role.role != 'admin':
                role.role = 'admin'
                role.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated role to admin for user: {username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Admin role already exists for user: {username}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Admin user ready: {username} / {password}')
        )