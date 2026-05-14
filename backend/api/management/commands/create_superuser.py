from django.core.management.base import BaseCommand
from api.User.model import CustomUser
import os


class Command(BaseCommand):
    help = 'Create superuser if not exists'

    def handle(self, *args, **kwargs):
        username = os.getenv('SUPERUSER_NAME', 'admin')
        email = os.getenv('SUPERUSER_EMAIL', 'admin@example.com')
        password = os.getenv('SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.ERROR('SUPERUSER_PASSWORD env var not set'))
            return

        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))
            return

        CustomUser.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created'))
