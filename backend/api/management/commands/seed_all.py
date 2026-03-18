from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed the database with initial data"

    def add_arguments(self, parser):
        parser.add_argument("n", type=int, help="Number of entries to create for each model")

    def handle(self, *args, **kwargs):

        n = kwargs["n"]

        seed_scripts = [
            "api.management.commands.seed_types",
            "api.management.commands.seed_categories",
            "api.management.commands.seed_roles",
            "api.management.commands.seed_permissions",
        ]

        for script in seed_scripts:
            try:
                self.stdout.write(self.style.SUCCESS(f"Starting seeding for {script}..."))

                module = __import__(script, fromlist=["Command"])
                module.Command().handle()

                self.stdout.write(self.style.SUCCESS(f"Finished seeding for {script}\n"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error occurred while seeding {script}: {e}"))