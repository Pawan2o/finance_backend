from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Seed default roles"

    def handle(self, *args, **kwargs):

        roles = ["user"]

        for role_name in roles:
            role, created = Group.objects.get_or_create(name=role_name)

            message = (
                self.style.SUCCESS(f"Created Role: {role.name}")
                if created
                else self.style.WARNING(f"Role already exists: {role.name}")
            )

            self.stdout.write(message)

        self.stdout.write(self.style.SUCCESS("Role seeding completed"))