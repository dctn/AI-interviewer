from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from payment.models import Wallet


@receiver(post_save,sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance,resume_credits=1,interview_credits=1)