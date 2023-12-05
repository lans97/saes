
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ExtendedUser

@receiver(post_save, sender=get_user_model())
def create_user_extension(sender, instance, created, **kwargs):
    if created:
        ExtendedUser.objects.create(user=instance)
