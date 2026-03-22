from django.db.models import Q
from core.models import Invoice, User


class InvoiceService:

    @staticmethod
    def get_invoices(status=None, freelancer_id=None, search=None, page=1, page_size=10):
        qs = Invoice.objects.select_related('client', 'project').all()

        if status and status != 'all':
            qs = qs.filter(status=status)

        if freelancer_id and freelancer_id != 'all':
            qs = qs.filter(client__user_id=freelancer_id)

        if search:
            qs = qs.filter(
                Q(invoice_number__icontains=search) |
                Q(client__name__icontains=search) |
                Q(project__name__icontains=search)
            )

        total_count = qs.count()
        offset = (int(page) - 1) * int(page_size)
        invoices = qs[offset:offset + int(page_size)]

        results = []
        for inv in invoices:
            results.append({
                "id": inv.invoice_number,
                "client_name": inv.client.name if inv.client else "Unknown",
                "project_name": inv.project.name if inv.project else "N/A",
                "freelancer_id": str(inv.client.user_id) if inv.client else None,
                "status": inv.status.title(),
                "issued_date": str(inv.issue_date),
                "due_date": str(inv.due_date),
                "amount": float(inv.total_amount),
                "paid_amount": float(inv.paid_amount),
            })

        return {
            "count": total_count,
            "results": results
        }

    @staticmethod
    def get_freelancers():
        users = User.objects.filter(is_active=True).values('id', 'first_name', 'last_name')
        result = []
        for u in users:
            name = f"{u['first_name']} {u['last_name']}".strip() or "Unnamed"
            result.append({
                "id": str(u['id']),
                "name": name
            })
        return result
