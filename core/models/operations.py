from django.db import models
from core.models.project import Project
from core.models.task import Task
from core.models.client import Client
from core.models.invoicing import Invoice


class ReportingSnapshot(models.Model):
    id = models.BigAutoField(primary_key=True)
    snapshot_type = models.CharField(max_length=50)
    period_type = models.CharField(max_length=20)
    period_start = models.DateField()
    period_end = models.DateField()
    filters_json = models.JSONField(default=dict, blank=True)
    data_json = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reporting_snapshots'


class ReportExport(models.Model):
    id = models.BigAutoField(primary_key=True)
    report_type = models.CharField(max_length=50)
    period_type = models.CharField(max_length=20)
    filters_json = models.JSONField(default=dict, blank=True)
    file_format = models.CharField(max_length=20)
    file_id = models.CharField(max_length=100, blank=True)
    export_status = models.CharField(max_length=20, default='queued')
    requested_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'report_exports'


class ProductivityRuleConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    rule_name = models.CharField(max_length=100)
    weight_on_time = models.DecimalField(max_digits=6, decimal_places=2, default=33.33)
    weight_estimate_accuracy = models.DecimalField(max_digits=6, decimal_places=2, default=33.33)
    weight_utilization = models.DecimalField(max_digits=6, decimal_places=2, default=33.34)
    target_utilization_percent = models.DecimalField(max_digits=6, decimal_places=2, default=80)
    overrun_penalty_factor = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'productivity_rule_configs'


class ProductivityScore(models.Model):
    id = models.BigAutoField(primary_key=True)
    period_type = models.CharField(max_length=20)
    period_start = models.DateField()
    period_end = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='productivity_scores')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='productivity_scores')
    estimated_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    utilization_percent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    on_time_percent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    variance_percent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    productivity_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    breakdown_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'productivity_scores'


class ClientTrustRuleConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    rule_name = models.CharField(max_length=100)
    on_time_weight = models.DecimalField(max_digits=6, decimal_places=2, default=50)
    delay_penalty_weight = models.DecimalField(max_digits=6, decimal_places=2, default=25)
    overdue_penalty_weight = models.DecimalField(max_digits=6, decimal_places=2, default=25)
    severe_overdue_threshold_days = models.PositiveIntegerField(default=30)
    trusted_min_score = models.DecimalField(max_digits=6, decimal_places=2, default=80)
    moderate_min_score = models.DecimalField(max_digits=6, decimal_places=2, default=60)
    watch_min_score = models.DecimalField(max_digits=6, decimal_places=2, default=40)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client_trust_rule_configs'


class ClientTrustScore(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='trust_scores')
    period_type = models.CharField(max_length=20)
    period_start = models.DateField()
    period_end = models.DateField()
    on_time_payment_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    delayed_invoice_count = models.PositiveIntegerField(default=0)
    overdue_invoice_count = models.PositiveIntegerField(default=0)
    avg_days_to_pay = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    trust_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    trust_level = models.CharField(max_length=20, default='watch')
    flags_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client_trust_scores'


class ClientTrustEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='trust_events')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='trust_events')
    event_type = models.CharField(max_length=50)
    event_date = models.DateField()
    days_delayed = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    score_impact = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'client_trust_events'


class ClientRiskAlert(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='risk_alerts')
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    message = models.TextField()
    triggered_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='open')
    context_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client_risk_alerts'
