from django.core.management.base import BaseCommand
from api.Type.model import Type


class Command(BaseCommand):
    help = "Seed default transaction types"

    def handle(self, *args, **kwargs):

        types = [
            "income",
            "expense"
        ]

        for type_name in types:

            obj, created = Type.objects.get_or_create(
                name=type_name
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Type: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {obj.name}"))

        self.stdout.write(self.style.SUCCESS("Type seeding completed"))