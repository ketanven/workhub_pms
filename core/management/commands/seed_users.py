from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with 10 fake users'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding 10 users...')
        
        for _ in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.unique.email()
            username = email.split('@')[0]
            
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = f"{email.split('@')[0]}{random.randint(1, 9999)}"

            user = User.objects.create_user(
                username=username,
                email=email,
                password='password',
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.email}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded users'))
