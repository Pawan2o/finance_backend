from django.core.management.base import BaseCommand
from api.TestAPI.model import Test
import uuid
from faker import Faker
import random
from api.Address.model import Address

class Command(BaseCommand):
    help = 'Seed the Test model with n records'

    def add_arguments(self, parser):
        parser.add_argument('n', type=int, help='Number of records to create')

    def handle(self, *args, **kwargs):
        n = kwargs['n']
        faker = Faker()

        addresses = list(Address.objects.all())

        if not addresses:
            self.stdout.write(self.style.ERROR('No Address instances available.'))
            return

        for _ in range(n):
            address = random.choice(addresses)
            
            Test.objects.create(
                id=uuid.uuid4(),
                name=faker.name(),
                description=faker.text(max_nb_chars=200),
                address=address,
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {n} records into Test model'))
