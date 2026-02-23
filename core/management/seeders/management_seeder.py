from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Client, Project, Task


User = get_user_model()


@dataclass
class ManagementSeedContext:
    user: User
    clients: list[Client]
    projects: list[Project]
    tasks: list[Task]


class ManagementSeeder:
    def __init__(self, stdout=None):
        self.stdout = stdout

    def log(self, msg: str):
        if self.stdout:
            self.stdout.write(msg)

    def seed_user(self) -> User:
        user, created = User.objects.get_or_create(
            email='demo@workhub.com',
            defaults={
                'username': 'demo',
                'first_name': 'Demo',
                'last_name': 'Freelancer',
                'is_active': True,
            },
        )
        if created:
            user.set_password('password123')
            user.save(update_fields=['password'])
            self.log('Created demo user: demo@workhub.com / password123')
        return user

    def seed_clients(self, user: User) -> list[Client]:
        clients = []
        specs = [
            ('Demo Acme Labs', 'Acme Labs', 'contact1@example.com', Decimal('70.00')),
            ('Demo Northwind Co', 'Northwind Co', 'contact2@example.com', Decimal('80.00')),
            ('Demo BlueOrbit', 'BlueOrbit', 'contact3@example.com', Decimal('90.00')),
        ]
        for idx, (name, company, email, rate) in enumerate(specs, start=1):
            client, _ = Client.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'company_name': company,
                    'email': email,
                    'phone': f'+1-555-20{idx}',
                    'currency': 'USD',
                    'hourly_rate': rate,
                    'payment_terms_days': 14,
                    'trust_score': Decimal('75.00'),
                    'is_active': True,
                },
            )
            clients.append(client)
        self.log('Seeded clients module')
        return clients

    def seed_projects(self, user: User, clients: list[Client]) -> list[Project]:
        if not clients:
            clients = self.seed_clients(user)

        projects = []
        now = timezone.now().date()
        specs = [
            (clients[0], 'Demo Website Revamp', Project.STATUS_IN_PROGRESS, Project.PRIORITY_HIGH, Decimal('85.00')),
            (clients[0], 'Demo Mobile App API', Project.STATUS_PLANNED, Project.PRIORITY_MEDIUM, Decimal('95.00')),
            (clients[1], 'Demo CRM Automation', Project.STATUS_IN_PROGRESS, Project.PRIORITY_URGENT, Decimal('105.00')),
            (clients[2], 'Demo Analytics Dashboard', Project.STATUS_ON_HOLD, Project.PRIORITY_LOW, Decimal('75.00')),
        ]

        for client, name, status, priority, rate in specs:
            project, _ = Project.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'client': client,
                    'description': f'{name} seeded for demo',
                    'status': status,
                    'priority': priority,
                    'billing_type': Project.BILLING_HOURLY,
                    'hourly_rate': rate,
                    'currency': 'USD',
                    'estimated_hours': Decimal('120.00'),
                    'progress_percent': Decimal('35.00'),
                    'start_date': now - timedelta(days=20),
                    'due_date': now + timedelta(days=30),
                    'is_active': True,
                },
            )
            if project.client_id != client.id:
                project.client = client
                project.save(update_fields=['client'])
            projects.append(project)
        self.log('Seeded projects module')
        return projects

    def seed_tasks(self, user: User, projects: list[Project]) -> list[Task]:
        if not projects:
            projects = self.seed_projects(user, self.seed_clients(user))

        tasks = []
        now = timezone.now().date()
        for project in projects:
            specs = [
                ('Planning & Scope', Task.STATUS_COMPLETED, Task.PRIORITY_MEDIUM, Decimal('12.00'), Decimal('11.50')),
                ('Implementation', Task.STATUS_IN_PROGRESS, Task.PRIORITY_HIGH, Decimal('45.00'), Decimal('22.00')),
                ('Testing & QA', Task.STATUS_TODO, Task.PRIORITY_HIGH, Decimal('20.00'), Decimal('0.00')),
            ]
            for title, status, priority, est, actual in specs:
                task, _ = Task.objects.get_or_create(
                    user=user,
                    project=project,
                    title=f'{project.name} - {title}',
                    defaults={
                        'description': f'{title} task seeded for demo',
                        'status': status,
                        'priority': priority,
                        'estimated_hours': est,
                        'actual_hours': actual,
                        'progress_percent': Decimal('40.00'),
                        'start_date': now - timedelta(days=14),
                        'due_date': now + timedelta(days=14),
                        'billable': True,
                        'hourly_rate': project.hourly_rate,
                        'is_active': True,
                    },
                )
                tasks.append(task)
        self.log('Seeded tasks module')
        return tasks

    def seed_module(self, module: str) -> ManagementSeedContext:
        user = self.seed_user()
        clients: list[Client] = []
        projects: list[Project] = []
        tasks: list[Task] = []

        if module in ('all', 'clients'):
            clients = self.seed_clients(user)

        if module in ('all', 'projects'):
            if not clients:
                clients = self.seed_clients(user)
            projects = self.seed_projects(user, clients)

        if module in ('all', 'tasks'):
            if not clients:
                clients = self.seed_clients(user)
            if not projects:
                projects = self.seed_projects(user, clients)
            tasks = self.seed_tasks(user, projects)

        return ManagementSeedContext(user=user, clients=clients, projects=projects, tasks=tasks)
