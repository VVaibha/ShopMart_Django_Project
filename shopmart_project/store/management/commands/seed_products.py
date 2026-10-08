from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product


class Command(BaseCommand):
    help = "Seed the database with demo categories and products."

    def handle(self, *args, **options):
        data = {
            'Electronics': [
                ('Wireless Headphones', 2499, 15),
                ('Smart Watch', 3999, 10),
                ('Bluetooth Speaker', 1799, 20),
            ],
            'Fashion': [
                ('Cotton T-Shirt', 599, 40),
                ('Denim Jacket', 2199, 12),
                ('Running Shoes', 2999, 18),
            ],
            'Home & Kitchen': [
                ('Non-Stick Pan Set', 1299, 25),
                ('LED Desk Lamp', 899, 30),
                ('Ceramic Coffee Mug (Set of 4)', 649, 50),
            ],
        }

        for cat_name, products in data.items():
            category, _ = Category.objects.get_or_create(
                name=cat_name, defaults={'slug': slugify(cat_name)}
            )
            for name, price, stock in products:
                Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'slug': slugify(name),
                        'description': f'High quality {name.lower()} at an unbeatable price.',
                        'price': price,
                        'stock': stock,
                    },
                )

        self.stdout.write(self.style.SUCCESS('Demo products seeded successfully!'))
