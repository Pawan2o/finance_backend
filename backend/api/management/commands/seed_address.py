from django.core.management.base import BaseCommand
from api.Address.model import Address
import uuid
from faker import Faker

class Command(BaseCommand):
    help = 'Seed the Address model with n records'

    def add_arguments(self, parser):
        parser.add_argument('n', type=int, help='Number of records to create')

    def handle(self, *args, **kwargs):
        n = kwargs['n']
        faker = Faker()

        for _ in range(n):
            Address.objects.create(
                id=uuid.uuid4(),
                address=faker.street_address(),
                city=faker.city(),
                state=faker.state(),
                pincode=faker.postcode(),
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {n} records into Address model'))
