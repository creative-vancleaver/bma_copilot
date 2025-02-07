from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import CellClassification

@receiver(pre_save, sender=CellClassification)
def slugify_class_fields(sender, instance, **kwargs):
    if instance.ai_class:
        instance.ai_class = slugify(instance.ai_class)
    if instance.user_class:
        instance.user_class = slugify(instance.user_class)