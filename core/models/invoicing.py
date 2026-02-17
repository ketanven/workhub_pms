from django.db import models
from core.models.client import Client
from core.models.project import Project
from core.models.task import Task
from core.models.workbench import TimeEntry


class Invoice(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice_number = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    issue_date = models.DateField()
    due_date = models.DateField()
    currency = models.CharField(max_length=10, default='USD')
    invoice_type = models.CharField(max_length=20, default='hourly')
    status = models.CharField(max_length=20, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    metadata_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']


class InvoiceLineItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    item_type = models.CharField(max_length=30, default='service')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=30, default='hour')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sort_order = models.PositiveIntegerField(default=0)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_line_items')
    time_entry = models.ForeignKey(TimeEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_line_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_line_items'
        ordering = ['sort_order', 'id']


class InvoicePayment(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_reference = models.CharField(max_length=200, blank=True)
    payment_note = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_payments'
        ordering = ['-payment_date', '-created_at']


class InvoiceStatusHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='status_histories')
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    metadata_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_status_histories'
        ordering = ['-changed_at']


class InvoiceVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='versions')
    version_no = models.PositiveIntegerField()
    version_label = models.CharField(max_length=100, blank=True)
    snapshot_json = models.JSONField(default=dict)
    change_summary = models.TextField(blank=True)
    edited_at = models.DateTimeField()
    is_restored = models.BooleanField(default=False)
    restored_from_version_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_versions'
        ordering = ['-version_no']
        unique_together = ('invoice', 'version_no')


class InvoiceNumberingConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    scope_type = models.CharField(max_length=30, default='workspace')
    scope_id = models.CharField(max_length=100, blank=True)
    prefix = models.CharField(max_length=30, default='INV')
    separator = models.CharField(max_length=10, default='-')
    include_year = models.BooleanField(default=True)
    include_month = models.BooleanField(default=False)
    client_code_pattern = models.CharField(max_length=100, blank=True)
    sequence_padding = models.PositiveIntegerField(default=4)
    reset_rule = models.CharField(max_length=20, default='yearly')
    format_template = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_numbering_configs'


class InvoiceSequence(models.Model):
    id = models.BigAutoField(primary_key=True)
    config = models.ForeignKey(InvoiceNumberingConfig, on_delete=models.CASCADE, related_name='sequences')
    period_key = models.CharField(max_length=50)
    last_sequence = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_sequences'
        unique_together = ('config', 'period_key')


class InvoiceReminder(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=30)
    channel = models.CharField(max_length=30, default='email')
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='scheduled')
    message_template = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_reminders'


class InvoiceAttachment(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='attachments')
    file_id = models.CharField(max_length=100)
    attachment_type = models.CharField(max_length=50, default='supporting_document')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_attachments'
