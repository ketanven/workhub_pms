from datetime import timedelta
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.models.client import Client
from core.models.invoicing import (
    Invoice,
    InvoiceLineItem,
    InvoicePayment,
    InvoiceStatusHistory,
    InvoiceVersion,
    InvoiceNumberingConfig,
    InvoiceSequence,
    InvoiceReminder,
)
from core.models.workbench import TimeEntry


class InvoicingService:
    @staticmethod
    def _calc_line_total(item):
        qty = float(item.get('quantity', 1) or 1)
        price = float(item.get('unit_price', 0) or 0)
        base = qty * price
        discount = base * (float(item.get('discount_percent', 0) or 0) / 100)
        taxable = base - discount
        tax = taxable * (float(item.get('tax_percent', 0) or 0) / 100)
        return round(taxable + tax, 2)

    @staticmethod
    def _recalculate_totals(invoice):
        subtotal = invoice.line_items.aggregate(total=Sum('line_total'))['total'] or 0
        invoice.subtotal = subtotal
        invoice.total_amount = subtotal - (invoice.discount_total or 0) + (invoice.tax_total or 0)
        invoice.balance_amount = (invoice.total_amount or 0) - (invoice.paid_amount or 0)
        invoice.save()
        return invoice

    @staticmethod
    def _record_status(invoice, from_status, to_status, reason=''):
        InvoiceStatusHistory.objects.create(
            invoice=invoice,
            from_status=from_status or '',
            to_status=to_status,
            changed_at=timezone.now(),
            reason=reason,
        )

    @staticmethod
    @transaction.atomic
    def create_invoice(data):
        line_items = data.pop('line_items', [])
        invoice = Invoice.objects.create(**data)
        for idx, item in enumerate(line_items):
            payload = dict(item)
            payload['sort_order'] = payload.get('sort_order', idx)
            payload['line_total'] = payload.get('line_total') or InvoicingService._calc_line_total(payload)
            InvoiceLineItem.objects.create(invoice=invoice, **payload)

        InvoicingService._recalculate_totals(invoice)
        InvoicingService._record_status(invoice, '', invoice.status, 'Invoice created')
        return invoice

    @staticmethod
    @transaction.atomic
    def update_invoice(invoice, data):
        line_items = data.pop('line_items', None)
        old_status = invoice.status

        for key, value in data.items():
            setattr(invoice, key, value)
        invoice.save()

        if line_items is not None:
            invoice.line_items.all().delete()
            for idx, item in enumerate(line_items):
                payload = dict(item)
                payload['sort_order'] = payload.get('sort_order', idx)
                payload['line_total'] = payload.get('line_total') or InvoicingService._calc_line_total(payload)
                InvoiceLineItem.objects.create(invoice=invoice, **payload)

        InvoicingService._recalculate_totals(invoice)
        if old_status != invoice.status:
            InvoicingService._record_status(invoice, old_status, invoice.status, 'Invoice updated')
        return invoice

    @staticmethod
    @transaction.atomic
    def submit_invoice(invoice):
        old = invoice.status
        invoice.status = 'submitted'
        invoice.submitted_at = timezone.now()
        invoice.save()
        InvoicingService._record_status(invoice, old, invoice.status, 'Invoice submitted')
        return invoice

    @staticmethod
    @transaction.atomic
    def send_invoice(invoice):
        old = invoice.status
        if invoice.status == 'draft':
            invoice.status = 'sent'
        invoice.sent_at = timezone.now()
        invoice.save()
        InvoicingService._record_status(invoice, old, invoice.status, 'Invoice sent')
        return invoice

    @staticmethod
    def send_reminder(invoice):
        reminder = InvoiceReminder.objects.create(
            invoice=invoice,
            reminder_type='payment_due',
            channel='email',
            scheduled_at=timezone.now(),
            sent_at=timezone.now(),
            status='sent',
            message_template='Payment reminder sent',
        )
        return reminder

    @staticmethod
    @transaction.atomic
    def add_payment(invoice, data):
        payment = InvoicePayment.objects.create(invoice=invoice, **data)
        paid = invoice.payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
        old_status = invoice.status
        invoice.paid_amount = paid
        invoice.balance_amount = (invoice.total_amount or 0) - paid
        if invoice.balance_amount <= 0:
            invoice.status = 'paid'
            invoice.paid_at = timezone.now()
        invoice.save()
        if old_status != invoice.status:
            InvoicingService._record_status(invoice, old_status, invoice.status, 'Payment recorded')
        return payment, invoice

    @staticmethod
    def mark_paid(invoice, payload):
        amount = payload.get('amount') or invoice.balance_amount or invoice.total_amount
        payment_data = {
            'payment_date': payload.get('payment_date') or timezone.now().date(),
            'amount': amount,
            'currency': invoice.currency,
            'payment_method': payload.get('payment_method', ''),
            'transaction_reference': payload.get('transaction_reference', ''),
            'payment_note': 'Marked as paid',
            'status': 'completed',
        }
        return InvoicingService.add_payment(invoice, payment_data)

    @staticmethod
    def invoice_stats():
        qs = Invoice.objects.all()
        return {
            'collected': qs.filter(status='paid').aggregate(total=Sum('paid_amount'))['total'] or 0,
            'outstanding': qs.exclude(status='paid').aggregate(total=Sum('balance_amount'))['total'] or 0,
            'overdue_count': qs.filter(status='overdue').count(),
            'total_count': qs.count(),
        }

    @staticmethod
    @transaction.atomic
    def create_from_time_entries(client_id, project_id=None, time_entry_ids=None, issue_date=None, due_date=None, currency='USD'):
        client = Client.objects.filter(id=client_id).first()
        if not client:
            raise ValidationError('Client not found')

        entries = TimeEntry.objects.filter(is_billable=True)
        if project_id:
            entries = entries.filter(project_id=project_id)
        if time_entry_ids:
            entries = entries.filter(id__in=time_entry_ids)

        config = InvoicingService.get_or_create_default_numbering()
        invoice_number = InvoicingService.generate_next_invoice_number(config)

        issue = issue_date or timezone.now().date()
        due = due_date or (issue + timedelta(days=7))

        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            client_id=client_id,
            project_id=project_id,
            issue_date=issue,
            due_date=due,
            currency=currency,
            invoice_type='hourly',
            status='draft',
        )

        for idx, entry in enumerate(entries):
            hours = round(entry.duration_seconds / 3600, 2)
            rate = float(entry.hourly_rate_snapshot or 0)
            line_total = round(hours * rate, 2)
            InvoiceLineItem.objects.create(
                invoice=invoice,
                item_type='time_entry',
                title=f'Time Entry #{entry.id}',
                description=entry.note,
                quantity=hours,
                unit='hour',
                unit_price=rate,
                line_total=line_total,
                sort_order=idx,
                task=entry.task,
                time_entry=entry,
            )

        InvoicingService._recalculate_totals(invoice)
        InvoicingService._record_status(invoice, '', invoice.status, 'Invoice created from time entries')
        return invoice

    @staticmethod
    def get_or_create_default_numbering():
        config = InvoiceNumberingConfig.objects.filter(is_active=True).order_by('-id').first()
        if config:
            return config
        return InvoiceNumberingConfig.objects.create(
            scope_type='workspace',
            prefix='INV',
            separator='-',
            include_year=True,
            include_month=False,
            sequence_padding=4,
            reset_rule='yearly',
            format_template='',
            is_active=True,
        )

    @staticmethod
    @transaction.atomic
    def generate_next_invoice_number(config=None):
        config = config or InvoicingService.get_or_create_default_numbering()
        now = timezone.now()
        period_key = f"{now.year}" if config.reset_rule == 'yearly' else f"{now.year}{now.month:02d}"
        sequence, _ = InvoiceSequence.objects.get_or_create(config=config, period_key=period_key, defaults={'last_sequence': 0})
        sequence.last_sequence += 1
        sequence.save()

        parts = [config.prefix] if config.prefix else []
        if config.include_year:
            parts.append(str(now.year))
        if config.include_month:
            parts.append(f"{now.month:02d}")
        parts.append(str(sequence.last_sequence).zfill(config.sequence_padding))
        return config.separator.join(parts)

    @staticmethod
    @transaction.atomic
    def create_version(invoice, version_label='', change_summary=''):
        latest = invoice.versions.order_by('-version_no').first()
        version_no = (latest.version_no + 1) if latest else 1
        snapshot = {
            'invoice': {
                'invoice_number': invoice.invoice_number,
                'client_id': str(invoice.client_id),
                'project_id': str(invoice.project_id) if invoice.project_id else None,
                'issue_date': str(invoice.issue_date),
                'due_date': str(invoice.due_date),
                'currency': invoice.currency,
                'invoice_type': invoice.invoice_type,
                'status': invoice.status,
                'subtotal': str(invoice.subtotal),
                'discount_total': str(invoice.discount_total),
                'tax_total': str(invoice.tax_total),
                'total_amount': str(invoice.total_amount),
                'paid_amount': str(invoice.paid_amount),
                'balance_amount': str(invoice.balance_amount),
                'notes': invoice.notes,
                'terms': invoice.terms,
            },
            'line_items': list(invoice.line_items.values()),
        }
        return InvoiceVersion.objects.create(
            invoice=invoice,
            version_no=version_no,
            version_label=version_label or f'v{version_no}',
            snapshot_json=snapshot,
            change_summary=change_summary,
            edited_at=timezone.now(),
        )

    @staticmethod
    @transaction.atomic
    def restore_version(invoice, version):
        data = version.snapshot_json.get('invoice', {})
        old_status = invoice.status
        for field in [
            'invoice_number', 'issue_date', 'due_date', 'currency', 'invoice_type',
            'status', 'subtotal', 'discount_total', 'tax_total', 'total_amount',
            'paid_amount', 'balance_amount', 'notes', 'terms'
        ]:
            if field in data:
                setattr(invoice, field, data[field])

        invoice.client_id = data.get('client_id', invoice.client_id)
        invoice.project_id = data.get('project_id', invoice.project_id)
        invoice.save()

        invoice.line_items.all().delete()
        for item in version.snapshot_json.get('line_items', []):
            item.pop('id', None)
            item.pop('invoice_id', None)
            item.pop('created_at', None)
            item.pop('updated_at', None)
            InvoiceLineItem.objects.create(invoice=invoice, **item)

        version.is_restored = True
        version.save()
        InvoicingService._record_status(invoice, old_status, invoice.status, f'Restored from version {version.version_no}')
        return invoice
