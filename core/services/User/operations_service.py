from datetime import timedelta
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from core.models.workbench import TimeEntry
from core.models.invoicing import Invoice
from core.models.client import Client
from core.models.task import Task
from core.models.project import Project
from core.models.operations import (
    ReportExport,
    ProductivityRuleConfig,
    ProductivityScore,
    ClientTrustRuleConfig,
    ClientTrustScore,
    ClientTrustEvent,
    ClientRiskAlert,
)


class AnalysisService:
    @staticmethod
    def summary():
        now = timezone.now().date()
        month_start = now.replace(day=1)
        total_seconds = TimeEntry.objects.filter(entry_date__gte=month_start, entry_date__lte=now).aggregate(total=Sum('duration_seconds'))['total'] or 0
        billable_seconds = TimeEntry.objects.filter(entry_date__gte=month_start, entry_date__lte=now, is_billable=True).aggregate(total=Sum('duration_seconds'))['total'] or 0
        earnings = TimeEntry.objects.filter(entry_date__gte=month_start, entry_date__lte=now).aggregate(total=Sum('amount_snapshot'))['total'] or 0
        productivity = ProductivityScore.objects.filter(period_type='monthly').order_by('-period_end').first()
        on_time_rate = productivity.on_time_percent if productivity else 0
        utilization = round((billable_seconds / total_seconds) * 100, 2) if total_seconds else 0

        return {
            'billable_hours': round(billable_seconds / 3600, 2),
            'earnings': earnings,
            'utilization': utilization,
            'productivity_score': productivity.productivity_score if productivity else 0,
            'on_time_rate': on_time_rate,
        }

    @staticmethod
    def web_analytics(period_days=14):
        today = timezone.now().date()
        points = []
        for i in range(period_days - 1, -1, -1):
            date = today - timedelta(days=i)
            seconds = TimeEntry.objects.filter(entry_date=date).aggregate(total=Sum('duration_seconds'))['total'] or 0
            points.append({'date': str(date), 'hours': round(seconds / 3600, 2)})
        return points

    @staticmethod
    def earnings_trend(period='monthly'):
        days = 30 if period == 'monthly' else 7
        return AnalysisService.web_analytics(period_days=days)

    @staticmethod
    def time_allocation():
        total = TimeEntry.objects.aggregate(total=Sum('duration_seconds'))['total'] or 0
        billable = TimeEntry.objects.filter(is_billable=True).aggregate(total=Sum('duration_seconds'))['total'] or 0
        non_billable = total - billable
        return {
            'client_work': round(billable / 3600, 2),
            'admin': round(non_billable / 3600, 2),
            'meetings': 0,
            'learning': 0,
        }

    @staticmethod
    def top_clients():
        rows = Client.objects.annotate(revenue=Sum('invoices__paid_amount'), hours=Sum('projects__tasks__time_entries__duration_seconds')).order_by('-revenue')[:10]
        data = []
        for row in rows:
            data.append({
                'client_id': str(row.id),
                'name': row.name,
                'revenue': row.revenue or 0,
                'hours': round((row.hours or 0) / 3600, 2),
                'trust': row.trust_score or 0,
            })
        return data

    @staticmethod
    def task_accuracy():
        tasks = Task.objects.filter(is_active=True)
        data = []
        for task in tasks:
            est = float(task.estimated_hours or 0)
            act = float(task.actual_hours or 0)
            variance = round(act - est, 2)
            data.append({'task_id': str(task.id), 'title': task.title, 'estimated_hours': est, 'actual_hours': act, 'variance_hours': variance})
        return data

    @staticmethod
    def invoice_health():
        return {
            'paid': Invoice.objects.filter(status='paid').count(),
            'pending': Invoice.objects.filter(status__in=['draft', 'submitted', 'sent']).count(),
            'overdue': Invoice.objects.filter(status='overdue').count(),
        }


class ReportingService:
    @staticmethod
    def earnings_report():
        return AnalysisService.earnings_trend(period='monthly')

    @staticmethod
    def time_allocation_report():
        return AnalysisService.time_allocation()

    @staticmethod
    def project_performance():
        rows = Project.objects.annotate(hours=Sum('tasks__time_entries__duration_seconds')).order_by('-hours')
        return [
            {
                'project_id': str(r.id),
                'project_name': r.name,
                'completion': r.progress_percent or 0,
                'tracked_hours': round((r.hours or 0) / 3600, 2),
                'risk': 'high' if (r.progress_percent or 0) < 30 else 'normal',
            }
            for r in rows
        ]

    @staticmethod
    def client_analytics():
        return AnalysisService.top_clients()

    @staticmethod
    def monthly_bundle():
        return {
            'summary': AnalysisService.summary(),
            'earnings': AnalysisService.earnings_trend(),
            'allocation': AnalysisService.time_allocation(),
            'invoice_health': AnalysisService.invoice_health(),
        }

    @staticmethod
    def export_report(data):
        report = ReportExport.objects.create(
            report_type=data['report_type'],
            period_type=data['period_type'],
            filters_json=data.get('filters_json', {}),
            file_format=data['file_format'],
            file_id='',
            export_status='completed',
            requested_at=timezone.now(),
            completed_at=timezone.now(),
        )
        return report


class ProductivityService:
    @staticmethod
    def summary():
        latest = ProductivityScore.objects.order_by('-period_end').first()
        return latest

    @staticmethod
    def weekly_trend():
        return ProductivityScore.objects.filter(period_type='weekly').order_by('-period_start')[:12]

    @staticmethod
    def task_variance():
        return ProductivityScore.objects.filter(task_id__isnull=False).order_by('-period_end')[:100]

    @staticmethod
    def on_time_rate():
        score = ProductivityService.summary()
        return {'on_time_rate': score.on_time_percent if score else 0}

    @staticmethod
    def utilization():
        score = ProductivityService.summary()
        return {'utilization': score.utilization_percent if score else 0}

    @staticmethod
    def update_rules(payload):
        config = ProductivityRuleConfig.objects.filter(is_active=True).order_by('-id').first()
        if not config:
            config = ProductivityRuleConfig.objects.create(rule_name='default')
        for key, value in payload.items():
            setattr(config, key, value)
        config.save()
        return config


class ClientTrustService:
    @staticmethod
    def summary():
        rows = ClientTrustScore.objects.values('trust_level').annotate(count=Count('id')).order_by('trust_level')
        avg = ClientTrustScore.objects.aggregate(avg=Avg('trust_score'))['avg'] or 0
        return {'distribution': list(rows), 'average_score': avg}

    @staticmethod
    def clients():
        return ClientTrustScore.objects.select_related('client').order_by('-period_end')

    @staticmethod
    def history(client_id):
        return ClientTrustEvent.objects.filter(client_id=client_id).order_by('-event_date')

    @staticmethod
    def recalculate():
        rule = ClientTrustRuleConfig.objects.filter(is_active=True).order_by('-id').first()
        if not rule:
            rule = ClientTrustRuleConfig.objects.create(rule_name='default')

        results = []
        for client in Client.objects.all():
            invoices = Invoice.objects.filter(client=client)
            total = invoices.count() or 1
            paid_on_time = invoices.filter(status='paid').count()
            overdue = invoices.filter(status='overdue').count()
            delayed = max(total - paid_on_time - overdue, 0)

            score = (paid_on_time / total) * float(rule.on_time_weight)
            score -= (delayed / total) * float(rule.delay_penalty_weight)
            score -= (overdue / total) * float(rule.overdue_penalty_weight)
            score = max(min(round(score, 2), 100), 0)

            if score >= float(rule.trusted_min_score):
                level = 'trusted'
            elif score >= float(rule.moderate_min_score):
                level = 'moderate'
            elif score >= float(rule.watch_min_score):
                level = 'watch'
            else:
                level = 'risky'

            trust = ClientTrustScore.objects.create(
                client=client,
                period_type='rolling',
                period_start=timezone.now().date() - timedelta(days=90),
                period_end=timezone.now().date(),
                on_time_payment_percent=round((paid_on_time / total) * 100, 2),
                delayed_invoice_count=delayed,
                overdue_invoice_count=overdue,
                avg_days_to_pay=0,
                trust_score=score,
                trust_level=level,
                flags_json={'overdue_invoices': overdue},
            )
            results.append(trust)

            if level == 'risky':
                ClientRiskAlert.objects.create(
                    client=client,
                    alert_type='payment_behavior',
                    severity='high',
                    title=f'High risk payment pattern: {client.name}',
                    message='Client has risky trust score based on overdue and delayed payments.',
                    triggered_at=timezone.now(),
                    status='open',
                    context_json={'trust_score': score},
                )
        return results

    @staticmethod
    def update_rules(payload):
        config = ClientTrustRuleConfig.objects.filter(is_active=True).order_by('-id').first()
        if not config:
            config = ClientTrustRuleConfig.objects.create(rule_name='default')
        for key, value in payload.items():
            setattr(config, key, value)
        config.save()
        return config

    @staticmethod
    def alerts():
        return ClientRiskAlert.objects.filter(status='open').order_by('-triggered_at')
