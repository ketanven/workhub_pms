from django.core.management.base import BaseCommand, CommandError

from core.management.seeders.management_seeder import ManagementSeeder


class Command(BaseCommand):
    help = 'Seeds management data module-wise: clients, projects, tasks, or all'

    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            type=str,
            default='all',
            choices=['all', 'clients', 'projects', 'tasks'],
            help='Select module to seed',
        )

    def handle(self, *args, **options):
        module = options['module']
        try:
            seeder = ManagementSeeder(stdout=self.stdout)
            ctx = seeder.seed_module(module)
            self.stdout.write(self.style.SUCCESS(f'Seed completed for module: {module}'))
            self.stdout.write(self.style.SUCCESS(f'Demo user: {ctx.user.email} / password123'))
            if ctx.clients:
                self.stdout.write(self.style.SUCCESS(f'Clients seeded: {len(ctx.clients)}'))
            if ctx.projects:
                self.stdout.write(self.style.SUCCESS(f'Projects seeded: {len(ctx.projects)}'))
            if ctx.tasks:
                self.stdout.write(self.style.SUCCESS(f'Tasks seeded: {len(ctx.tasks)}'))
        except Exception as exc:
            raise CommandError(f'Seeding failed: {exc}')
