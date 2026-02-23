from django.core.management.base import BaseCommand, CommandError

from core.management.seeders.dashboard_seeder import DashboardSeeder


class Command(BaseCommand):
    help = 'Seeds dashboard demo data module-wise or full system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            type=str,
            default='all',
            choices=[
                'all',
                'workbench',
                'invoicing',
                'analysis',
                'reports',
                'productivity',
                'trust',
                'calendar',
                'kanban',
                'platform',
            ],
            help='Select which module to seed',
        )

    def handle(self, *args, **options):
        module = options['module']

        try:
            seeder = DashboardSeeder(stdout=self.stdout)
            ctx = seeder.seed_module(module)
            self.stdout.write(self.style.SUCCESS(f'Seed completed for module: {module}'))
            self.stdout.write(
                self.style.SUCCESS(
                    f'Demo credentials: email={ctx.user.email} password=password123'
                )
            )
        except Exception as exc:
            raise CommandError(f'Seeding failed: {exc}')
