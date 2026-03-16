from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Seed default permissions and assign them to roles"

    def handle(self, *args, **kwargs):

        # Example: Assign all permissions to user role
        try:
            user_group = Group.objects.get(name="user")
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR("User role not found"))
            return

        permissions = Permission.objects.all()

        user_group.permissions.set(permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f"Assigned {permissions.count()} permissions to 'user' role"
            )
        )

        self.stdout.write(self.style.SUCCESS("Permission seeding completed"))