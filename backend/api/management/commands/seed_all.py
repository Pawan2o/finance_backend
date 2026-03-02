from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def add_arguments(self, parser):
        parser.add_argument('n', type=int, help='Number of entries to create for each model')

    def handle(self, *args, **kwargs):
        n = kwargs['n']

        # Import and run each seed script
        seed_scripts = [
            'api.management.commands.seed_address',
            'api.management.commands.seed_test',
        ]

        for script in seed_scripts:
            try:
                self.stdout.write(self.style.SUCCESS(f'Starting seeding for {script}...'))
                module = __import__(script, fromlist=['Command'])
                module.Command().handle(n=n)  # Pass the 'n' argument here
                self.stdout.write(self.style.SUCCESS(f'Finished seeding for {script}\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error occurred while seeding {script}: {e}'))
