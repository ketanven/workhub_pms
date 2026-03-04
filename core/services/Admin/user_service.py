from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.db.models import Q, Count, Sum
from core.models.client import Client
from core.models.project import Project
from core.models.task import Task
from core.models.invoicing import Invoice

User = get_user_model()

class AdminUserService:
    @staticmethod
    def list_users(search=None, status=None):
        queryset = User.objects.all().order_by('-date_joined')
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) | 
                Q(email__icontains=search)
            )
        
        if status is not None:
             # Normalize status to boolean
            is_active = str(status).lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        return queryset

    @staticmethod
    def create_user(data):
        if User.objects.filter(email=data['email']).exists():
            raise ValidationError("User with this email already exists.")
        
        username = data['email'].split('@')[0]
        # Handle potential username conflict
        if User.objects.filter(username=username).exists():
             import random
             username = f"{username}{random.randint(1, 9999)}"

        user = User.objects.create_user(
            username=username,
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        return user

    @staticmethod
    def update_user(user, data):
        if 'email' in data and User.objects.filter(email=data['email']).exclude(id=user.id).exists():
             raise ValidationError("User with this email already exists.")
             
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        return user

    @staticmethod
    def delete_user(user):
        # Soft delete
        user.is_active = False
        user.save()
        return user

    @staticmethod
    def workspace_data(user):
        clients_qs = Client.objects.filter(user=user).annotate(
            active_projects=Count('projects', filter=Q(projects__is_active=True), distinct=True),
            total_earnings=Sum('invoices__paid_amount'),
        ).order_by('-created_at')
        projects_qs = Project.objects.filter(user=user).annotate(
            task_count=Count('tasks', distinct=True),
            completed_task_count=Count('tasks', filter=Q(tasks__status='completed'), distinct=True),
            total_invoiced=Sum('invoices__total_amount'),
        ).order_by('-created_at')
        tasks_qs = Task.objects.filter(user=user).select_related('project', 'project__client').order_by('-created_at')
        invoices_qs = Invoice.objects.filter(client__user=user).select_related('client', 'project').order_by('-created_at')

        summary = {
            'clients': clients_qs.count(),
            'projects': projects_qs.count(),
            'tasks': tasks_qs.count(),
            'invoices': invoices_qs.count(),
        }

        clients = []
        for c in clients_qs:
            clients.append({
                'id': str(c.id),
                'name': c.name,
                'company_name': c.company_name,
                'email': c.email,
                'active_projects': c.active_projects or 0,
                'total_earnings': c.total_earnings or 0,
                'currency': c.currency or '',
                'is_active': c.is_active,
                'created_at': c.created_at,
            })

        projects = []
        for p in projects_qs:
            projects.append({
                'id': str(p.id),
                'name': p.name,
                'client_id': str(p.client_id),
                'client_name': p.client.name if p.client else '',
                'status': p.status,
                'priority': p.priority,
                'billing_type': p.billing_type,
                'hourly_rate': p.hourly_rate,
                'fixed_price': p.fixed_price,
                'currency': p.currency,
                'due_date': p.due_date,
                'task_count': p.task_count or 0,
                'completed_task_count': p.completed_task_count or 0,
                'total_invoiced': p.total_invoiced or 0,
                'is_active': p.is_active,
                'created_at': p.created_at,
            })

        tasks = []
        for t in tasks_qs:
            tasks.append({
                'id': str(t.id),
                'title': t.title,
                'project_id': str(t.project_id),
                'project_name': t.project.name if t.project else '',
                'client_name': t.project.client.name if t.project and t.project.client else '',
                'status': t.status,
                'priority': t.priority,
                'billable': t.billable,
                'estimated_hours': t.estimated_hours,
                'actual_hours': t.actual_hours,
                'hourly_rate': t.hourly_rate,
                'due_date': t.due_date,
                'is_active': t.is_active,
                'created_at': t.created_at,
            })

        invoices = []
        for i in invoices_qs:
            invoices.append({
                'id': i.id,
                'invoice_number': i.invoice_number,
                'client_id': str(i.client_id),
                'client_name': i.client.name if i.client else '',
                'project_id': str(i.project_id) if i.project_id else None,
                'project_name': i.project.name if i.project else '',
                'status': i.status,
                'issue_date': i.issue_date,
                'due_date': i.due_date,
                'currency': i.currency,
                'total_amount': i.total_amount,
                'paid_amount': i.paid_amount,
                'balance_amount': i.balance_amount,
                'created_at': i.created_at,
            })

        return {
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_active': user.is_active,
            },
            'summary': summary,
            'clients': clients,
            'projects': projects,
            'tasks': tasks,
            'invoices': invoices,
        }
