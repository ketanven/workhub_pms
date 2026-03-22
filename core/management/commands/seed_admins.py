from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import Admin, Role, Permission

class Command(BaseCommand):
    help = 'Seeds the database with roles, permissions, a Master Admin and a Sub Admin'

    def handle(self, *args, **options):
        # 1. Sync permissions
        call_command('sync_permissions')
        self.stdout.write(self.style.SUCCESS('Permissions synced.'))

        # 2. Create Master Admin Role and attach all permissions
        master_role, _ = Role.objects.get_or_create(name='Master Admin')
        all_perms = Permission.objects.all()
        master_role.permissions.set(all_perms)
        self.stdout.write(self.style.SUCCESS('Master Admin role created and permissions assigned.'))

        # 3. Create Sub Admin Role and attach some permissions
        sub_role, _ = Role.objects.get_or_create(name='Operations Admin')
        dashboard_perms = Permission.objects.filter(code__in=['dashboard_read', 'user_read'])
        sub_role.permissions.set(dashboard_perms)
        self.stdout.write(self.style.SUCCESS('Operations Admin role created.'))

        # 4. Create or update Master Admin
        admin, created = Admin.objects.get_or_create(
            email='admin@workhub.com',
            defaults={
                'first_name': 'Master',
                'last_name': 'Admin',
                'role': master_role
            }
        )
        if created:
            admin.set_password('password')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Successfully created Master Admin'))
        else:
            admin.role = master_role
            admin.save()
            self.stdout.write(self.style.WARNING('Master Admin checked and role applied.'))

        # 5. Create or update Sub Admin
        subadmin, s_created = Admin.objects.get_or_create(
            email='subadmin@workhub.com',
            defaults={
                'first_name': 'Sub',
                'last_name': 'Admin',
                'role': sub_role
            }
        )
        if s_created:
            subadmin.set_password('password')
            subadmin.save()
            self.stdout.write(self.style.SUCCESS('Successfully created Sub Admin'))
        else:
            subadmin.role = sub_role
            subadmin.save()
            self.stdout.write(self.style.WARNING('Sub Admin checked and role applied.'))

        self.stdout.write(self.style.SUCCESS('Admin seeding complete!'))
