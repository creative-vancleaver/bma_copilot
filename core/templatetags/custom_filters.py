from django import template
import os
from django.conf import settings

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.filter
def file_exists(image_url):
    if not image_url:
        return False
    file_path = os.path.join(settings.MEDIA_ROOT, image_url.lstrip("/"))
    return os.path.exists(file_path)

@register.filter
def replace(value, args):
    
    if not isinstance(value, str) or not args or " " not in args:
        return value
    
    old_char = args[0]
    new_char = args[1:]

    return value.replace(old_char, new_char)

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class}) 

@register.filter
def abbreviate_cell_type(value):
    abbreviations = {
        'blasts_and_blast_equivalents': 'Blasts',
        'erythroid_precursors': 'Erythroids',
    }

    return abbreviations.get(value, value.replace('_', ' ').title())