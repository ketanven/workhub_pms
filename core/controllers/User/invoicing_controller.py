from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from common.responses import ApiResponse
from core.models.invoicing import Invoice, InvoicePayment, InvoiceVersion
from core.serializers.User.invoicing_serializer import (
    InvoiceSerializer,
    InvoiceCreateSerializer,
    InvoiceUpdateSerializer,
    InvoiceFromTimeEntriesSerializer,
    InvoicePaymentSerializer,
    InvoicePaymentCreateSerializer,
    MarkPaidSerializer,
    InvoiceVersionSerializer,
    InvoiceVersionCreateSerializer,
    InvoiceNumberingConfigSerializer,
)
from core.services.User.invoicing_service import InvoicingService


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


def _error_message(e):
    if hasattr(e, 'detail'):
        detail = e.detail
        if isinstance(detail, list) and detail:
            return str(detail[0])
        return str(detail)
    return str(e)


class InvoiceListCreateView(APIView):
    def get(self, request):
        queryset = Invoice.objects.all().order_by('-created_at')
        status_filter = request.query_params.get('status')
        client_id = request.query_params.get('client_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if date_from:
            queryset = queryset.filter(issue_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(issue_date__lte=date_to)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = InvoiceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = InvoiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invoice = InvoicingService.create_invoice(serializer.validated_data)
            return ApiResponse.success('Invoice created successfully', InvoiceSerializer(invoice).data, status.HTTP_201_CREATED)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class InvoiceFromTimeEntriesView(APIView):
    def post(self, request):
        serializer = InvoiceFromTimeEntriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invoice = InvoicingService.create_from_time_entries(**serializer.validated_data)
            return ApiResponse.success('Invoice draft created from time entries', InvoiceSerializer(invoice).data, status.HTTP_201_CREATED)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class InvoiceDetailView(APIView):
    def get_object(self, invoice_id):
        return Invoice.objects.filter(id=invoice_id).first()

    def get(self, request, invoice_id):
        invoice = self.get_object(invoice_id)
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)
        return ApiResponse.success('Invoice details fetched successfully', InvoiceSerializer(invoice).data)

    def patch(self, request, invoice_id):
        invoice = self.get_object(invoice_id)
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)

        serializer = InvoiceUpdateSerializer(invoice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            invoice = InvoicingService.update_invoice(invoice, serializer.validated_data)
            return ApiResponse.success('Invoice updated successfully', InvoiceSerializer(invoice).data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class InvoiceSubmitView(APIView):
    def post(self, request, invoice_id):
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)
        invoice = InvoicingService.submit_invoice(invoice)
        return ApiResponse.success('Invoice submitted successfully', InvoiceSerializer(invoice).data)


class InvoiceSendView(APIView):
    def post(self, request, invoice_id):
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)
        invoice = InvoicingService.send_invoice(invoice)
        return ApiResponse.success('Invoice sent successfully', InvoiceSerializer(invoice).data)


class InvoiceReminderView(APIView):
    def post(self, request, invoice_id):
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)
        reminder = InvoicingService.send_reminder(invoice)
        return ApiResponse.success('Invoice reminder sent successfully', {'reminder_id': reminder.id})


class InvoiceMarkPaidView(APIView):
    def post(self, request, invoice_id):
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)

        serializer = MarkPaidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        _, invoice = InvoicingService.mark_paid(invoice, serializer.validated_data)
        return ApiResponse.success('Invoice marked as paid successfully', InvoiceSerializer(invoice).data)


class InvoicePaymentListCreateView(APIView):
    def get(self, request, invoice_id):
        payments = InvoicePayment.objects.filter(invoice_id=invoice_id).order_by('-payment_date', '-created_at')
        return ApiResponse.success('Invoice payment history fetched successfully', InvoicePaymentSerializer(payments, many=True).data)

    def post(self, request, invoice_id):
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)

        serializer = InvoicePaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment, invoice = InvoicingService.add_payment(invoice, serializer.validated_data)
            return ApiResponse.success(
                'Payment added successfully',
                {'payment': InvoicePaymentSerializer(payment).data, 'invoice': InvoiceSerializer(invoice).data},
                status.HTTP_201_CREATED,
            )
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class InvoicePDFView(APIView):
    def get(self, request, invoice_id):
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)

        content = f"Invoice: {invoice.invoice_number}\nClient: {invoice.client.name}\nTotal: {invoice.total_amount} {invoice.currency}\nStatus: {invoice.status}"
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice-{invoice.invoice_number}.pdf"'
        return response


class InvoiceStatsView(APIView):
    def get(self, request):
        data = InvoicingService.invoice_stats()
        return ApiResponse.success('Invoice stats fetched successfully', data)


class InvoiceNumberingConfigView(APIView):
    def get(self, request):
        config = InvoicingService.get_or_create_default_numbering()
        return ApiResponse.success('Invoice numbering config fetched successfully', InvoiceNumberingConfigSerializer(config).data)

    def patch(self, request):
        config = InvoicingService.get_or_create_default_numbering()
        serializer = InvoiceNumberingConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.success('Invoice numbering config updated successfully', serializer.data)


class InvoiceNumberPreviewView(APIView):
    def get(self, request):
        number = InvoicingService.generate_next_invoice_number()
        return ApiResponse.success('Next invoice number generated successfully', {'invoice_number': number})


class InvoiceVersionListCreateView(APIView):
    def get(self, request, invoice_id):
        versions = InvoiceVersion.objects.filter(invoice_id=invoice_id).order_by('-version_no')
        return ApiResponse.success('Invoice versions fetched successfully', InvoiceVersionSerializer(versions, many=True).data)

    def post(self, request, invoice_id):
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)

        serializer = InvoiceVersionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        version = InvoicingService.create_version(invoice, **serializer.validated_data)
        return ApiResponse.success('Invoice version created successfully', InvoiceVersionSerializer(version).data, status.HTTP_201_CREATED)


class InvoiceVersionDetailView(APIView):
    def get(self, request, invoice_id, version_id):
        version = InvoiceVersion.objects.filter(invoice_id=invoice_id, id=version_id).first()
        if not version:
            return ApiResponse.error('Invoice version not found', status.HTTP_404_NOT_FOUND)
        return ApiResponse.success('Invoice version fetched successfully', InvoiceVersionSerializer(version).data)


class InvoiceVersionRestoreView(APIView):
    def post(self, request, invoice_id, version_id):
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return ApiResponse.error('Invoice not found', status.HTTP_404_NOT_FOUND)
        version = InvoiceVersion.objects.filter(invoice_id=invoice_id, id=version_id).first()
        if not version:
            return ApiResponse.error('Invoice version not found', status.HTTP_404_NOT_FOUND)

        invoice = InvoicingService.restore_version(invoice, version)
        return ApiResponse.success('Invoice version restored successfully', InvoiceSerializer(invoice).data)
