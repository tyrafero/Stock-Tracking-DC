"""
Django signals for stock app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserRole


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