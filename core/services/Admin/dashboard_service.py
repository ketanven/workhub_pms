from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncMonth, ExtractMonth
from django.utils import timezone
from datetime import timedelta

from core.models import Invoice, Task, Project, User
from core.models.invoicing import InvoiceStatusHistory, InvoicePayment
from core.models.workbench import TimeEntry


class DashboardService:

    @staticmethod
    def get_stats():
        total_users = User.objects.filter(is_active=True).count()

        invoices = Invoice.objects.all()
        revenue_collected = invoices.aggregate(total=Sum('paid_amount'))['total'] or 0
        open_pipeline = invoices.exclude(status='paid').aggregate(total=Sum('balance_amount'))['total'] or 0
        overdue_invoices = invoices.filter(status='overdue').count() + invoices.filter(
            due_date__lt=timezone.now().date(),
            status__in=['sent', 'draft', 'partially_paid']
        ).count()

        active_users = User.objects.filter(
            is_active=True,
            projects__status='in_progress'
        ).distinct().count()

        return {
            "revenue_collected": float(revenue_collected),
            "open_pipeline": float(open_pipeline),
            "active_freelancers": active_users,
            "total_freelancers": total_users,
            "overdue_invoices": overdue_invoices,
        }

    @staticmethod
    def get_revenue_chart(year):
        months_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Invoiced amounts per month
        invoiced_qs = (
            Invoice.objects
            .filter(issue_date__year=year)
            .annotate(month=ExtractMonth('issue_date'))
            .values('month')
            .annotate(total=Sum('total_amount'))
            .order_by('month')
        )
        invoiced_map = {row['month']: float(row['total']) for row in invoiced_qs}

        # Received (paid) amounts per month
        received_qs = (
            InvoicePayment.objects
            .filter(payment_date__year=year)
            .annotate(month=ExtractMonth('payment_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        received_map = {row['month']: float(row['total']) for row in received_qs}

        invoiced = [invoiced_map.get(m, 0) for m in range(1, 13)]
        received = [received_map.get(m, 0) for m in range(1, 13)]

        return {
            "months": months_labels,
            "invoiced": invoiced,
            "received": received,
        }

    @staticmethod
    def get_task_stats():
        qs = Task.objects.values('status').annotate(count=Count('id'))
        stats = {row['status']: row['count'] for row in qs}
        return {
            "completed": stats.get('completed', 0),
            "in_progress": stats.get('in_progress', 0),
            "pending": stats.get('todo', 0),
        }

    @staticmethod
    def get_activity_feed(limit=10):
        entries = (
            InvoiceStatusHistory.objects
            .select_related('invoice', 'invoice__client')
            .order_by('-changed_at')[:limit]
        )
        feed = []
        for entry in entries:
            inv = entry.invoice
            client_name = inv.client.name if inv.client else 'Unknown'
            title = f"Invoice #{inv.invoice_number} marked as {entry.to_status.title()}"
            detail = f"₹{inv.total_amount} from {client_name}"

            diff = timezone.now() - entry.changed_at
            if diff.total_seconds() < 3600:
                time_str = f"{int(diff.total_seconds() // 60)}m ago"
            elif diff.total_seconds() < 86400:
                time_str = f"{int(diff.total_seconds() // 3600)}h ago"
            else:
                time_str = f"{diff.days}d ago"

            feed.append({
                "title": title,
                "detail": detail,
                "time": time_str
            })

        # If no history entries, return from recent invoices
        if not feed:
            recent_invoices = Invoice.objects.select_related('client').order_by('-created_at')[:limit]
            for inv in recent_invoices:
                client_name = inv.client.name if inv.client else 'Unknown'
                diff = timezone.now() - inv.created_at
                if diff.total_seconds() < 3600:
                    time_str = f"{int(diff.total_seconds() // 60)}m ago"
                elif diff.total_seconds() < 86400:
                    time_str = f"{int(diff.total_seconds() // 3600)}h ago"
                else:
                    time_str = f"{diff.days}d ago"

                feed.append({
                    "title": f"Invoice #{inv.invoice_number} created ({inv.status.title()})",
                    "detail": f"₹{inv.total_amount} from {client_name}",
                    "time": time_str
                })

        return feed

    @staticmethod
    def get_analysis(period='week'):
        now = timezone.now()
        if period == 'day':
            start = now - timedelta(days=1)
        elif period == 'month':
            start = now - timedelta(days=30)
        else:
            start = now - timedelta(days=7)

        prev_start = start - (now - start)

        # Current period stats
        current_revenue = Invoice.objects.filter(
            paid_at__gte=start, paid_at__lte=now
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        prev_revenue = Invoice.objects.filter(
            paid_at__gte=prev_start, paid_at__lt=start
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        revenue_trend = 0
        if prev_revenue > 0:
            revenue_trend = round(((float(current_revenue) - float(prev_revenue)) / float(prev_revenue)) * 100, 1)

        # Hours logged
        current_hours_seconds = TimeEntry.objects.filter(
            entry_date__gte=start.date(), entry_date__lte=now.date()
        ).aggregate(total=Sum('duration_seconds'))['total'] or 0
        current_hours = round(current_hours_seconds / 3600, 1)

        prev_hours_seconds = TimeEntry.objects.filter(
            entry_date__gte=prev_start.date(), entry_date__lt=start.date()
        ).aggregate(total=Sum('duration_seconds'))['total'] or 0
        prev_hours = round(prev_hours_seconds / 3600, 1)

        hours_trend = 0
        if prev_hours > 0:
            hours_trend = round(((current_hours - prev_hours) / prev_hours) * 100, 1)

        # Active projects
        active_projects = Project.objects.filter(status='in_progress').count()
        prev_active = Project.objects.filter(
            status='in_progress',
            created_at__lt=start
        ).count()
        projects_trend = 0
        if prev_active > 0:
            projects_trend = round(((active_projects - prev_active) / prev_active) * 100, 1)

        # Freelancers billed
        freelancers_billed = Invoice.objects.filter(
            issue_date__gte=start.date()
        ).values('client__user').distinct().count()

        # Productivity chart - daily breakdown
        if period == 'day':
            categories = [f"{h}:00" for h in range(0, 24, 3)]
        elif period == 'month':
            categories = [f"Week {i}" for i in range(1, 6)]
        else:
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            categories = day_names

        hours_data = [0] * len(categories)
        tasks_data = [0] * len(categories)

        # Allocation by project
        allocations = (
            TimeEntry.objects
            .filter(entry_date__gte=start.date(), entry_date__lte=now.date())
            .values('project__name')
            .annotate(total_seconds=Sum('duration_seconds'))
            .order_by('-total_seconds')[:6]
        )
        total_allocation_seconds = sum(a['total_seconds'] for a in allocations) or 1
        allocation_list = []
        for a in allocations:
            allocation_list.append({
                "name": a['project__name'],
                "value": round((a['total_seconds'] / total_allocation_seconds) * 100)
            })

        return {
            "revenue_collected": float(current_revenue),
            "revenue_trend": revenue_trend,
            "hours_logged": current_hours,
            "hours_trend": hours_trend,
            "active_projects": active_projects,
            "projects_trend": projects_trend,
            "freelancers_billed": freelancers_billed,
            "freelancers_trend": 0,
            "productivity_chart": {
                "categories": categories,
                "hours": hours_data,
                "tasks": tasks_data,
            },
            "allocation": allocation_list,
        }
