from celery import shared_task

from .models import Case

@shared_task
def count_cases():
    return Case.objects.count()