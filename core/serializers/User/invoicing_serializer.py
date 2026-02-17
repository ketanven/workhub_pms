from rest_framework import serializers
from core.models.invoicing import (
    Invoice,
    InvoiceLineItem,
    InvoicePayment,
    InvoiceVersion,
    InvoiceNumberingConfig,
)
from core.models.client import Client
from core.models.project import Project
from core.models.task import Task
from core.models.workbench import TimeEntry


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = '__all__'


class InvoicePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoicePayment
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    payments = InvoicePaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'


class InvoiceLineItemInputSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=False, allow_null=True)
    time_entry = serializers.PrimaryKeyRelatedField(queryset=TimeEntry.objects.all(), required=False, allow_null=True)

    class Meta:
        model = InvoiceLineItem
        fields = [
            'item_type', 'title', 'description', 'quantity', 'unit',
            'unit_price', 'tax_percent', 'discount_percent', 'line_total',
            'sort_order', 'task', 'time_entry'
        ]


class InvoiceCreateSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False, allow_null=True)
    line_items = InvoiceLineItemInputSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'client', 'project', 'issue_date', 'due_date',
            'currency', 'invoice_type', 'status', 'subtotal', 'discount_total',
            'tax_total', 'total_amount', 'paid_amount', 'balance_amount', 'notes',
            'terms', 'metadata_json', 'line_items'
        ]


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemInputSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'client', 'project', 'issue_date', 'due_date',
            'currency', 'invoice_type', 'status', 'subtotal', 'discount_total',
            'tax_total', 'total_amount', 'paid_amount', 'balance_amount', 'notes',
            'terms', 'metadata_json', 'line_items'
        ]


class InvoiceFromTimeEntriesSerializer(serializers.Serializer):
    client_id = serializers.UUIDField()
    project_id = serializers.UUIDField(required=False, allow_null=True)
    time_entry_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    issue_date = serializers.DateField(required=False)
    due_date = serializers.DateField(required=False)
    currency = serializers.CharField(required=False, default='USD')


class InvoicePaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoicePayment
        fields = [
            'payment_date', 'amount', 'currency', 'payment_method',
            'transaction_reference', 'payment_note', 'status'
        ]


class MarkPaidSerializer(serializers.Serializer):
    payment_date = serializers.DateField(required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    payment_method = serializers.CharField(required=False, allow_blank=True)
    transaction_reference = serializers.CharField(required=False, allow_blank=True)


class InvoiceVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceVersion
        fields = '__all__'


class InvoiceVersionCreateSerializer(serializers.Serializer):
    version_label = serializers.CharField(required=False, allow_blank=True, default='')
    change_summary = serializers.CharField(required=False, allow_blank=True, default='')


class InvoiceNumberingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceNumberingConfig
        fields = '__all__'
