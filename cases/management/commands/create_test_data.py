from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

from users.models import User
from cases.models import Case, Video

class Command(BaseCommand):
    help = 'Creates test data for development'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create test user if doesn't exist
        user, created = User.objects.get_or_create(
            id=str(uuid.uuid4()),  # Generate UUID string for id
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f'Created test user: {user.email}')
        
        # Create some test cases
        for i in range(3):
            case = Case.objects.create(
                id=str(uuid.uuid4()),  # Generate UUID string for id
                name=f'Test Case {i+1}',
                description=f'Description for test case {i+1}',
                date=timezone.now().date(),
                time=timezone.now().time(),
                status='pending',
                user=user
            )
            
            # Create a video for each case
            video = Video.objects.create(
                id=str(uuid.uuid4()),  # Generate UUID string for id
                case=case,
                video_file_path=f'/fake/path/to/video_{i+1}.webm',
                azure_url=f'https://fake-azure.com/video_{i+1}.webm'
            )
            
            self.stdout.write(f'Created case {case.name} with video')

        self.stdout.write(self.style.SUCCESS('Successfully created test data')) 