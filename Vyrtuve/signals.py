from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profilis, User

"""
create_profile klausosi User modelio post_save signalo
"""
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profilis.objects.create(profilis=instance)