from django.core.management.base import BaseCommand
from core.models import Permission
from core.constants.permissions import PERMISSIONS

class Command(BaseCommand):
    help = 'Syncs the permissions from constants file to the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Syncing permissions..."))
        
        created_count = 0
        updated_count = 0
        
        for group in PERMISSIONS:
            group_name = group['group_name']
            for perm in group['permissions']:
                obj, created = Permission.objects.update_or_create(
                    code=perm['code'],
                    defaults={
                        'name': perm['name'],
                        'group_name': group_name
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
        self.stdout.write(self.style.SUCCESS(f"Successfully synced permissions! Created: {created_count}, Updated: {updated_count}"))
