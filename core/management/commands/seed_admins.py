from django.core.management.base import BaseCommand
from core.models import Admin

class Command(BaseCommand):
    help = 'Seeds the database with a Master Admin and a Sub Admin'

    def handle(self, *args, **options):
        # Create Master Admin
        if not Admin.objects.filter(email='admin@workhub.com').exists():
            admin = Admin.objects.create(
                first_name='Master',
                last_name='Admin',
                email='admin@workhub.com',
                role='master_admin'
            )
            admin.set_password('password')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Successfully created Master Admin'))
        else:
            self.stdout.write(self.style.WARNING('Master Admin already exists'))

        # Create Sub Admin
        if not Admin.objects.filter(email='subadmin@workhub.com').exists():
            admin = Admin.objects.create(
                first_name='Sub',
                last_name='Admin',
                email='subadmin@workhub.com',
                role='sub_admin'
            )
            admin.set_password('password')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Successfully created Sub Admin'))
        else:
            self.stdout.write(self.style.WARNING('Sub Admin already exists'))
