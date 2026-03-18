from django.core.management.base import BaseCommand
from api.Category.model import Category
from api.Type.model import Type


class Command(BaseCommand):
    help = "Seed default categories"

    def handle(self, *args, **kwargs):

        categories = [
            {"name": "Food", "type": "expense", "material_icon": "restaurant"},
            {"name": "Transport", "type": "expense", "material_icon": "directions_car"},
            {"name": "Shopping", "type": "expense", "material_icon": "shopping_cart"},
            {"name": "Bills", "type": "expense", "material_icon": "receipt_long"},
            {"name": "Health", "type": "expense", "material_icon": "health_and_safety"},
            {"name": "Entertainment", "type": "expense", "material_icon": "movie"},
            {"name": "Education", "type": "expense", "material_icon": "school"},
            {"name": "Travel", "type": "expense", "material_icon": "flight"},
            {"name": "Salary", "type": "income", "material_icon": "payments"},
            {"name": "Freelance", "type": "income", "material_icon": "laptop_mac"},
            {"name": "Business", "type": "income", "material_icon": "business_center"},
            {"name": "Investment", "type": "income", "material_icon": "trending_up"},
            {"name": "Bonus", "type": "income", "material_icon": "card_giftcard"},
        ]

        for category in categories:

            type_obj = Type.objects.filter(name=category["type"]).first()

            if not type_obj:
                self.stdout.write(self.style.ERROR(f"Type '{category['type']}' not found"))
                continue

            obj, created = Category.objects.get_or_create(
                name=category["name"],
                type=type_obj,
                defaults={"material_icon": category["material_icon"]},
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {obj.name}"))

        self.stdout.write(self.style.SUCCESS("Category seeding completed"))