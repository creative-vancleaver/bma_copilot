from django.core.management.base import BaseCommand
from cells.models import CellClassification
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Slugify existing ai_class and user_class fields in CellClassification"

    def handle(self, *args, **kwargs):
        updated_count = 0

        for obj in CellClassification.objects.all():
            updated = False

            if obj.ai_class:
                new_ai_class = slugify(obj.ai_class)
                if obj.ai_class != new_ai_class:
                    obj.ai_class = new_ai_class
                    updated = True

            if hasattr(obj, 'user_class') and obj.user_class:
                new_user_class = slugify(obj.user_class)
                if obj.user_class != new_user_class:
                    obj.user_class = new_user_class
                    updated = True

            if updated:
                obj.save()
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} records."))
