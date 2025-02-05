from __future__ import absolute_import, unicode_literals

# ENSURE CELERY IS ALWAYS IMPORTED WHEN DJANGO STARTS
from .celery import app as celery_app

__all__ = ('celery_app',)