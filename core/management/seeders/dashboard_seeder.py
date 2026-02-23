from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import (
    Client,
    Project,
    Task,
    TimeEntry,
    TimerSession,
    TimerBreak,
    OfflineSyncBatch,
    Invoice,
    InvoiceLineItem,
    InvoicePayment,
    InvoiceStatusHistory,
    InvoiceVersion,
    InvoiceNumberingConfig,
    InvoiceSequence,
    InvoiceReminder,
    InvoiceAttachment,
    ReportingSnapshot,
    ReportExport,
    ProductivityRuleConfig,
    ProductivityScore,
    ClientTrustRuleConfig,
    ClientTrustScore,
    ClientTrustEvent,
    ClientRiskAlert,
    CalendarEvent,
    CalendarEventLink,
    KanbanBoard,
    KanbanColumn,
    KanbanCard,
    KanbanCardActivity,
    KanbanLabel,
    KanbanCardLabel,
    Notification,
    File,
    WorkspaceSetting,
)


User = get_user_model()


@dataclass
class SeedContext:
    user: User
    clients: list[Client]
    projects: list[Project]
    tasks: list[Task]


class DashboardSeeder:
    """Seeds all dashboard modules with linked demo data.

    Data is idempotent by unique naming/keys and safe to run multiple times.
    """

    def __init__(self, stdout=None):
        self.stdout = stdout

    def log(self, message: str):
        if self.stdout:
            self.stdout.write(message)

    def seed_core_entities(self) -> SeedContext:
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

        clients: list[Client] = []
        for idx, name in enumerate(['Acme Labs', 'Northwind Co', 'BlueOrbit'], start=1):
            client, _ = Client.objects.get_or_create(
                user=user,
                name=f'Demo {name}',
                defaults={
                    'company_name': name,
                    'email': f'contact{idx}@example.com',
                    'phone': f'+1-555-100{idx}',
                    'currency': 'USD',
                    'hourly_rate': Decimal('65.00') + Decimal(str(idx * 5)),
                    'payment_terms_days': 14,
                    'trust_score': Decimal('80.00') - Decimal(str(idx * 5)),
                    'is_active': True,
                },
            )
            clients.append(client)

        projects: list[Project] = []
        project_specs = [
            ('Demo Website Revamp', clients[0], Project.STATUS_IN_PROGRESS, Project.PRIORITY_HIGH, Decimal('85.00')),
            ('Demo Mobile App API', clients[0], Project.STATUS_PLANNED, Project.PRIORITY_MEDIUM, Decimal('95.00')),
            ('Demo CRM Automation', clients[1], Project.STATUS_IN_PROGRESS, Project.PRIORITY_URGENT, Decimal('105.00')),
            ('Demo Analytics Dashboard', clients[2], Project.STATUS_ON_HOLD, Project.PRIORITY_LOW, Decimal('75.00')),
        ]
        for name, client, status, priority, rate in project_specs:
            project, _ = Project.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'client': client,
                    'description': f'{name} project for frontend demo and workflows',
                    'status': status,
                    'priority': priority,
                    'billing_type': Project.BILLING_HOURLY,
                    'hourly_rate': rate,
                    'currency': 'USD',
                    'estimated_hours': Decimal('120.00'),
                    'progress_percent': Decimal(str(random.randint(15, 75))),
                    'start_date': timezone.now().date() - timedelta(days=30),
                    'due_date': timezone.now().date() + timedelta(days=30),
                    'is_active': True,
                },
            )
            if project.client_id != client.id:
                project.client = client
                project.save(update_fields=['client'])
            projects.append(project)

        tasks: list[Task] = []
        for project in projects:
            for title, status, priority, estimate, actual in [
                ('Planning & Scope', Task.STATUS_COMPLETED, Task.PRIORITY_MEDIUM, Decimal('10.00'), Decimal('11.00')),
                ('Implementation', Task.STATUS_IN_PROGRESS, Task.PRIORITY_HIGH, Decimal('40.00'), Decimal('24.50')),
                ('Testing & QA', Task.STATUS_TODO, Task.PRIORITY_HIGH, Decimal('20.00'), Decimal('0.00')),
            ]:
                task, _ = Task.objects.get_or_create(
                    user=user,
                    project=project,
                    title=f'{project.name} - {title}',
                    defaults={
                        'description': f'{title} for {project.name}',
                        'status': status,
                        'priority': priority,
                        'estimated_hours': estimate,
                        'actual_hours': actual,
                        'progress_percent': Decimal(str(random.randint(0, 100))),
                        'start_date': timezone.now().date() - timedelta(days=20),
                        'due_date': timezone.now().date() + timedelta(days=10),
                        'billable': True,
                        'hourly_rate': project.hourly_rate,
                        'is_active': True,
                    },
                )
                tasks.append(task)

        return SeedContext(user=user, clients=clients, projects=projects, tasks=tasks)

    def seed_workbench(self, ctx: SeedContext):
        now = timezone.now()

        for day in range(1, 22):
            entry_date = (now - timedelta(days=day)).date()
            task = random.choice(ctx.tasks)
            project = task.project
            start = timezone.make_aware(timezone.datetime.combine(entry_date, timezone.datetime.min.time())) + timedelta(hours=9)
            duration = random.randint(1800, 14400)
            end = start + timedelta(seconds=duration)
            local_uuid = f'demo-entry-{entry_date.isoformat()}-{task.id}'
            TimeEntry.objects.get_or_create(
                local_entry_uuid=local_uuid,
                defaults={
                    'project': project,
                    'task': task,
                    'entry_date': entry_date,
                    'start_time': start,
                    'end_time': end,
                    'duration_seconds': duration,
                    'is_manual': day % 6 == 0,
                    'source': 'manual' if day % 6 == 0 else 'timer',
                    'note': f'Demo tracked work for {task.title}',
                    'is_billable': task.billable,
                    'hourly_rate_snapshot': task.hourly_rate,
                    'amount_snapshot': (Decimal(duration) / Decimal(3600)) * (task.hourly_rate or Decimal('0.00')),
                    'sync_status': 'synced',
                    'synced_at': now,
                },
            )

        run_task = ctx.tasks[1]
        running_session, _ = TimerSession.objects.get_or_create(
            local_session_uuid='demo-running-session',
            defaults={
                'project': run_task.project,
                'task': run_task,
                'started_at': now - timedelta(minutes=40),
                'status': TimerSession.STATUS_RUNNING,
                'started_from': 'web',
                'offline_mode': False,
            },
        )
        if running_session.status != TimerSession.STATUS_RUNNING:
            running_session.status = TimerSession.STATUS_RUNNING
            running_session.started_at = now - timedelta(minutes=40)
            running_session.resumed_at = None
            running_session.paused_at = None
            running_session.stopped_at = None
            running_session.total_elapsed_seconds = 0
            running_session.save()

        break_session, _ = TimerSession.objects.get_or_create(
            local_session_uuid='demo-break-session',
            defaults={
                'project': run_task.project,
                'task': run_task,
                'started_at': now - timedelta(hours=3),
                'paused_at': now - timedelta(hours=2, minutes=30),
                'status': TimerSession.STATUS_BREAK,
                'total_elapsed_seconds': 1200,
                'started_from': 'web',
                'offline_mode': False,
            },
        )
        TimerBreak.objects.get_or_create(
            timer_session=break_session,
            break_started_at=now - timedelta(hours=2, minutes=30),
            defaults={
                'reason': 'Coffee break',
                'break_ended_at': None,
                'break_duration_seconds': 0,
            },
        )

        OfflineSyncBatch.objects.get_or_create(
            batch_uuid='demo-sync-batch-001',
            defaults={
                'payload_json': {'source': 'mobile', 'entries': 3},
                'item_count': 3,
                'sync_status': 'completed',
                'attempted_at': now - timedelta(days=1),
                'completed_at': now - timedelta(days=1),
            },
        )
        self.log('Seeded workbench module')

    def seed_invoicing(self, ctx: SeedContext):
        now = timezone.now()
        cfg = (
            InvoiceNumberingConfig.objects.filter(scope_type='workspace', scope_id='')
            .order_by('id')
            .first()
        )
        if not cfg:
            cfg = InvoiceNumberingConfig.objects.create(
                scope_type='workspace',
                scope_id='',
                prefix='INV',
                separator='-',
                include_year=True,
                include_month=True,
                sequence_padding=4,
                reset_rule='yearly',
                is_active=True,
            )

        sequence, _ = InvoiceSequence.objects.get_or_create(
            config=cfg,
            period_key=str(now.year),
            defaults={'last_sequence': 4},
        )
        if sequence.last_sequence < 4:
            sequence.last_sequence = 4
            sequence.save(update_fields=['last_sequence'])

        invoice_specs = [
            ('INV-2026-0001', ctx.clients[0], ctx.projects[0], 'paid', Decimal('1500.00')),
            ('INV-2026-0002', ctx.clients[1], ctx.projects[2], 'sent', Decimal('980.00')),
            ('INV-2026-0003', ctx.clients[2], ctx.projects[3], 'overdue', Decimal('450.00')),
            ('INV-2026-0004', ctx.clients[0], ctx.projects[1], 'draft', Decimal('700.00')),
        ]

        seeded_invoices = []
        for number, client, project, status, total in invoice_specs:
            invoice, _ = Invoice.objects.get_or_create(
                invoice_number=number,
                defaults={
                    'client': client,
                    'project': project,
                    'issue_date': now.date() - timedelta(days=20),
                    'due_date': now.date() - timedelta(days=5) if status == 'overdue' else now.date() + timedelta(days=10),
                    'currency': 'USD',
                    'invoice_type': 'hourly',
                    'status': status,
                    'subtotal': total,
                    'discount_total': Decimal('0.00'),
                    'tax_total': Decimal('0.00'),
                    'total_amount': total,
                    'paid_amount': total if status == 'paid' else Decimal('0.00'),
                    'balance_amount': Decimal('0.00') if status == 'paid' else total,
                    'notes': 'Demo invoice for dashboard testing',
                    'terms': 'Net 14',
                    'submitted_at': now - timedelta(days=15),
                    'sent_at': now - timedelta(days=14) if status in ['paid', 'sent', 'overdue'] else None,
                    'paid_at': now - timedelta(days=7) if status == 'paid' else None,
                },
            )
            seeded_invoices.append(invoice)

            if not invoice.line_items.exists():
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    item_type='service',
                    title=f'{project.name} Development',
                    description='Milestone billing',
                    quantity=Decimal('10.00'),
                    unit='hour',
                    unit_price=total / Decimal('10.00'),
                    line_total=total,
                    sort_order=0,
                    task=ctx.tasks[0],
                    time_entry=TimeEntry.objects.first(),
                )

            InvoiceStatusHistory.objects.get_or_create(
                invoice=invoice,
                to_status=invoice.status,
                changed_at=invoice.created_at,
                defaults={
                    'from_status': '',
                    'reason': 'Seeded demo state',
                },
            )

            InvoiceVersion.objects.get_or_create(
                invoice=invoice,
                version_no=1,
                defaults={
                    'version_label': 'v1',
                    'snapshot_json': {'invoice_number': invoice.invoice_number, 'status': invoice.status},
                    'change_summary': 'Initial version',
                    'edited_at': invoice.created_at,
                },
            )

            InvoiceReminder.objects.get_or_create(
                invoice=invoice,
                reminder_type='payment_due',
                channel='email',
                scheduled_at=now - timedelta(days=2),
                defaults={
                    'sent_at': now - timedelta(days=2),
                    'status': 'sent',
                    'message_template': 'Gentle reminder',
                },
            )

            InvoiceAttachment.objects.get_or_create(
                invoice=invoice,
                file_id='demo-file-attachment',
                defaults={'attachment_type': 'supporting_document'},
            )

        paid_invoice = next((inv for inv in seeded_invoices if inv.status == 'paid'), None)
        if paid_invoice:
            InvoicePayment.objects.get_or_create(
                invoice=paid_invoice,
                payment_date=now.date() - timedelta(days=7),
                amount=paid_invoice.total_amount,
                defaults={
                    'currency': 'USD',
                    'payment_method': 'bank_transfer',
                    'transaction_reference': 'DEMO-TXN-1001',
                    'payment_note': 'Seed full payment',
                    'status': 'completed',
                },
            )

        self.log('Seeded invoicing module')

    def seed_reports_and_productivity(self, ctx: SeedContext):
        now = timezone.now()
        ReportingSnapshot.objects.get_or_create(
            snapshot_type='monthly_bundle',
            period_type='monthly',
            period_start=now.date().replace(day=1),
            period_end=now.date(),
            defaults={
                'filters_json': {'scope': 'all'},
                'data_json': {'note': 'Demo snapshot'},
                'generated_at': now,
            },
        )

        ReportExport.objects.get_or_create(
            report_type='earnings',
            period_type='monthly',
            file_format='csv',
            requested_at=now - timedelta(days=1),
            defaults={
                'filters_json': {'scope': 'all'},
                'file_id': 'demo-export-1',
                'export_status': 'completed',
                'completed_at': now - timedelta(days=1),
            },
        )

        rules = ProductivityRuleConfig.objects.filter(rule_name='default').order_by('id').first()
        if not rules:
            rules = ProductivityRuleConfig.objects.create(
                rule_name='default',
                weight_on_time=Decimal('40.00'),
                weight_estimate_accuracy=Decimal('35.00'),
                weight_utilization=Decimal('25.00'),
                target_utilization_percent=Decimal('80.00'),
                overrun_penalty_factor=Decimal('1.20'),
                is_active=True,
            )
        if not rules.is_active:
            rules.is_active = True
            rules.save(update_fields=['is_active'])

        for i in range(8):
            start = (now - timedelta(days=(i + 1) * 7)).date()
            end = start + timedelta(days=6)
            task = random.choice(ctx.tasks)
            ProductivityScore.objects.get_or_create(
                period_type='weekly',
                period_start=start,
                period_end=end,
                task=task,
                defaults={
                    'project': task.project,
                    'estimated_hours': Decimal('20.00'),
                    'actual_hours': Decimal(str(random.randint(14, 28))),
                    'utilization_percent': Decimal(str(random.randint(60, 95))),
                    'on_time_percent': Decimal(str(random.randint(55, 100))),
                    'variance_percent': Decimal(str(random.randint(0, 35))),
                    'productivity_score': Decimal(str(random.randint(58, 95))),
                    'breakdown_json': {'seed': 'demo'},
                },
            )

        self.log('Seeded reports/productivity module')

    def seed_client_trust(self, ctx: SeedContext):
        now = timezone.now()
        trust_rules = ClientTrustRuleConfig.objects.filter(rule_name='default').order_by('id').first()
        if not trust_rules:
            trust_rules = ClientTrustRuleConfig.objects.create(
                rule_name='default',
                on_time_weight=Decimal('50.00'),
                delay_penalty_weight=Decimal('25.00'),
                overdue_penalty_weight=Decimal('25.00'),
                severe_overdue_threshold_days=30,
                trusted_min_score=Decimal('80.00'),
                moderate_min_score=Decimal('60.00'),
                watch_min_score=Decimal('40.00'),
                is_active=True,
            )
        if not trust_rules.is_active:
            trust_rules.is_active = True
            trust_rules.save(update_fields=['is_active'])

        levels = ['trusted', 'moderate', 'watch']
        for idx, client in enumerate(ctx.clients):
            score_val = Decimal(str(88 - (idx * 18)))
            trust = ClientTrustScore.objects.get_or_create(
                client=client,
                period_type='rolling',
                period_start=now.date() - timedelta(days=90),
                period_end=now.date(),
                defaults={
                    'on_time_payment_percent': Decimal(str(95 - idx * 20)),
                    'delayed_invoice_count': idx,
                    'overdue_invoice_count': 1 if idx == 2 else 0,
                    'avg_days_to_pay': Decimal(str(6 + idx * 3)),
                    'trust_score': score_val,
                    'trust_level': levels[min(idx, len(levels) - 1)],
                    'flags_json': {'seed': 'demo'},
                },
            )[0]

            ClientTrustEvent.objects.get_or_create(
                client=client,
                invoice=Invoice.objects.filter(client=client).first(),
                event_type='payment_observed',
                event_date=now.date() - timedelta(days=idx * 10),
                defaults={
                    'days_delayed': idx * 2,
                    'amount': Decimal('250.00') + Decimal(str(idx * 150)),
                    'score_impact': Decimal(str(-idx * 2)),
                    'notes': 'Demo trust event',
                },
            )

            if trust.trust_level == 'watch':
                ClientRiskAlert.objects.get_or_create(
                    client=client,
                    alert_type='payment_behavior',
                    severity='medium',
                    title=f'Demo alert for {client.name}',
                    message='Overdue pattern detected in recent invoices.',
                    triggered_at=now - timedelta(days=2),
                    defaults={
                        'status': 'open',
                        'context_json': {'seed': 'demo'},
                    },
                )

        self.log('Seeded client trust module')

    def seed_calendar(self, ctx: SeedContext):
        now = timezone.now()
        for i in range(1, 7):
            start = now + timedelta(days=i, hours=2)
            end = start + timedelta(hours=1)
            event, _ = CalendarEvent.objects.get_or_create(
                title=f'Demo Event {i}',
                start_at=start,
                end_at=end,
                defaults={
                    'description': 'Demo calendar event',
                    'event_type': 'meeting' if i % 2 else 'reminder',
                    'all_day': False,
                    'timezone': 'UTC',
                    'location': 'Virtual',
                    'color': '#22c55e' if i % 2 else '#3b82f6',
                    'source_type': 'custom',
                    'source_id': '',
                    'reminder_minutes_before': 30,
                    'recurrence_rule': '',
                    'status': 'scheduled',
                },
            )
            CalendarEventLink.objects.get_or_create(
                calendar_event=event,
                entity_type='project',
                entity_id=str(ctx.projects[i % len(ctx.projects)].id),
            )

        self.log('Seeded calendar module')

    def seed_kanban(self, ctx: SeedContext):
        board, _ = KanbanBoard.objects.get_or_create(
            name='Demo Delivery Board',
            defaults={
                'description': 'Seeded kanban board',
                'color': '#0ea5e9',
                'icon': 'board',
                'visibility': 'private',
                'sort_order': 1,
                'is_archived': False,
            },
        )

        todo, _ = KanbanColumn.objects.get_or_create(board=board, name='To Do', defaults={'sort_order': 1})
        in_progress, _ = KanbanColumn.objects.get_or_create(board=board, name='In Progress', defaults={'sort_order': 2})
        done, _ = KanbanColumn.objects.get_or_create(board=board, name='Done', defaults={'sort_order': 3, 'is_done_column': True})

        card_map = [
            (todo, 'Define API contracts', 'high', 'todo'),
            (in_progress, 'Implement invoice endpoints', 'urgent', 'in_progress'),
            (done, 'Create auth flow', 'medium', 'done'),
        ]

        seeded_cards = []
        for idx, (col, title, priority, status) in enumerate(card_map, start=1):
            card, _ = KanbanCard.objects.get_or_create(
                board=board,
                column=col,
                title=f'Demo {title}',
                defaults={
                    'description': f'{title} for seeded workflow',
                    'project': ctx.projects[idx % len(ctx.projects)],
                    'task': ctx.tasks[idx % len(ctx.tasks)],
                    'priority': priority,
                    'due_date': timezone.now().date() + timedelta(days=idx * 2),
                    'estimate_hours': Decimal('6.00') + Decimal(str(idx)),
                    'actual_hours': Decimal('1.50') * idx,
                    'status': status,
                    'sort_order': idx,
                    'is_archived': False,
                },
            )
            seeded_cards.append(card)

        label_urgent, _ = KanbanLabel.objects.get_or_create(board=board, name='Urgent', defaults={'color': '#ef4444'})
        label_backend, _ = KanbanLabel.objects.get_or_create(board=board, name='Backend', defaults={'color': '#6366f1'})

        if seeded_cards:
            KanbanCardLabel.objects.get_or_create(card=seeded_cards[0], label=label_backend)
            KanbanCardLabel.objects.get_or_create(card=seeded_cards[1], label=label_urgent)
            KanbanCardActivity.objects.get_or_create(
                card=seeded_cards[1],
                action_type='move',
                from_value=str(todo.id),
                to_value=str(in_progress.id),
                defaults={'action_note': 'Seeded movement activity'},
            )

        self.log('Seeded kanban module')

    def seed_platform(self):
        now = timezone.now()
        settings = WorkspaceSetting.objects.order_by('id').first()
        if not settings:
            WorkspaceSetting.objects.create(
                currency='USD',
                timezone='UTC',
                week_start_day='monday',
                default_hourly_rate=Decimal('80.00'),
                invoice_due_days_default=14,
                invoice_tax_default=Decimal('0.00'),
                invoice_prefix_default='INV',
                date_format='YYYY-MM-DD',
                time_format='24h',
            )

        for i in range(1, 7):
            Notification.objects.get_or_create(
                notification_type='system' if i % 2 else 'invoice',
                title=f'Demo Notification {i}',
                message='Seeded notification for dashboard testing',
                entity_type='invoice' if i % 2 == 0 else 'task',
                entity_id=str(i),
                defaults={
                    'severity': 'info' if i <= 4 else 'warning',
                    'is_read': i % 3 == 0,
                    'read_at': now - timedelta(days=i) if i % 3 == 0 else None,
                    'action_url': '/dashboard',
                    'metadata_json': {'seed': 'demo'},
                },
            )

        File.objects.get_or_create(
            path='uploads/demo/invoice-sample.pdf',
            original_name='invoice-sample.pdf',
            defaults={
                'storage_disk': 'local',
                'mime_type': 'application/pdf',
                'extension': 'pdf',
                'size_bytes': 20480,
                'checksum': 'demo-checksum',
                'visibility': 'private',
                'status': 'uploaded',
                'metadata_json': {'seed': 'demo'},
                'uploaded_at': now,
            },
        )

        self.log('Seeded platform module')

    def seed_module(self, module: str):
        ctx = self.seed_core_entities()

        if module in ('all', 'workbench'):
            self.seed_workbench(ctx)

        if module in ('all', 'invoicing'):
            self.seed_invoicing(ctx)

        if module in ('all', 'reports', 'analysis', 'productivity'):
            self.seed_reports_and_productivity(ctx)

        if module in ('all', 'trust'):
            self.seed_client_trust(ctx)

        if module in ('all', 'calendar'):
            self.seed_calendar(ctx)

        if module in ('all', 'kanban'):
            self.seed_kanban(ctx)

        if module in ('all', 'platform'):
            self.seed_platform()

        return ctx
