import os
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
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
from core.models.platform import WorkspaceSetting
from core.models.project import Project
from core.models.task import Task
from core.models.workbench import TimeEntry


class InvoicingService:
    @staticmethod
    def _to_decimal(value, default='0'):
        if value is None or value == '':
            return Decimal(default)
        return Decimal(str(value))

    @staticmethod
    def _format_money(value, currency='USD'):
        return f"{InvoicingService._to_decimal(value):,.2f} {currency}"

    @staticmethod
    def _get_branding_assets():
        try:
            from reportlab.lib.utils import ImageReader
        except Exception:
            ImageReader = None

        brand_title = os.getenv('INVOICE_BRAND_TITLE', 'FWTS')
        brand_subtitle = os.getenv('INVOICE_BRAND_SUBTITLE', 'Freelancer Work Tracking System')
        brand_address = os.getenv('INVOICE_BRAND_ADDRESS', 'FWTS Systems, India')
        brand_contact = os.getenv('INVOICE_BRAND_CONTACT', 'billing@fwts.in')
        logo_path_setting = os.getenv('INVOICE_LOGO_PATH', '').strip()
        candidate_paths = []

        if logo_path_setting:
            candidate_paths.append(Path(logo_path_setting))
        candidate_paths.extend([
            Path(settings.BASE_DIR) / 'assets' / 'invoice-logo.png',
            Path(settings.BASE_DIR) / 'assets' / 'invoice-logo.jpg',
            Path(settings.BASE_DIR) / 'assets' / 'invoice-logo.jpeg',
            Path(settings.BASE_DIR) / 'assets' / 'logo.png',
            Path(settings.BASE_DIR) / 'assets' / 'logo.jpg',
            Path(settings.BASE_DIR) / 'assets' / 'logo.jpeg',
            Path(settings.BASE_DIR) / 'static' / 'logo.png',
            Path(settings.BASE_DIR) / 'static' / 'logo.jpg',
            Path(settings.BASE_DIR) / 'static' / 'logo.jpeg',
            Path(settings.BASE_DIR) / 'logo.png',
            Path(settings.BASE_DIR) / 'logo.jpg',
            Path(settings.BASE_DIR) / 'logo.jpeg',
        ])

        logo_path = None
        logo_reader = None
        for candidate in candidate_paths:
            if candidate.exists() and candidate.is_file():
                logo_path = candidate
                try:
                    if not ImageReader:
                        break
                    logo_reader = ImageReader(str(candidate))
                    break
                except Exception:
                    logo_path = None
                    logo_reader = None

        return {
            'title': brand_title,
            'subtitle': brand_subtitle,
            'address': brand_address,
            'contact': brand_contact,
            'logo_path': str(logo_path) if logo_path else '',
            'logo_reader': logo_reader,
        }

    @staticmethod
    def _build_invoice_pdf_document(payload):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except Exception:
            raise ValidationError('PDF generation dependency is missing. Please install reportlab.')

        buffer = BytesIO()
        styles = getSampleStyleSheet()
        normal = styles['Normal']
        heading = styles['Heading2']
        heading.fontName = 'Helvetica-Bold'
        heading.fontSize = 14
        heading.textColor = colors.HexColor('#0F172A')
        section_label = ParagraphStyle(
            name='SectionLabel',
            parent=styles['Heading4'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=4,
            spaceBefore=8,
        )
        normal.fontSize = 9
        normal.leading = 12
        small = ParagraphStyle(
            name='Small',
            parent=normal,
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#475569'),
        )

        branding = payload['branding']
        top_margin = 38 * mm
        left_margin = 14 * mm
        right_margin = 14 * mm
        bottom_margin = 16 * mm

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=top_margin,
            leftMargin=left_margin,
            rightMargin=right_margin,
            bottomMargin=bottom_margin,
        )

        def draw_header_footer(canvas_obj, document):
            page_width, page_height = A4
            fwts_green = colors.HexColor('#22C55E')
            fwts_green_dark = colors.HexColor('#15803D')
            fwts_mint = colors.HexColor('#DCFCE7')
            white = colors.white
            invoice_title = payload.get('pdf_title') or f"Invoice {payload.get('invoice', {}).get('invoice_number', '')}".strip()

            # PDF metadata (used by browser tab labels in many viewers).
            canvas_obj.setTitle(invoice_title)
            canvas_obj.setAuthor(branding.get('title', 'FWTS'))
            canvas_obj.setSubject('Freelancer Invoice')

            canvas_obj.saveState()
            # Professional layered header: clean base + smooth accents.
            canvas_obj.setFillColor(fwts_green_dark)
            canvas_obj.rect(0, page_height - 34 * mm, page_width, 34 * mm, stroke=0, fill=1)

            # Top lighter gradient-like sweep
            canvas_obj.setFillColor(fwts_green)
            p2 = canvas_obj.beginPath()
            p2.moveTo(0, page_height)
            p2.lineTo(page_width, page_height)
            p2.lineTo(page_width, page_height - 10 * mm)
            p2.curveTo(page_width * 0.80, page_height - 18 * mm, page_width * 0.55, page_height - 8 * mm, page_width * 0.36, page_height - 12 * mm)
            p2.curveTo(page_width * 0.20, page_height - 15 * mm, page_width * 0.08, page_height - 14 * mm, 0, page_height - 16 * mm)
            p2.close()
            canvas_obj.drawPath(p2, fill=1, stroke=0)

            # Single smooth white wave cut (no notch near logo)
            canvas_obj.setFillColor(colors.white)
            p = canvas_obj.beginPath()
            p.moveTo(0, page_height - 24 * mm)
            p.curveTo(page_width * 0.18, page_height - 32 * mm, page_width * 0.37, page_height - 20 * mm, page_width * 0.55, page_height - 24 * mm)
            p.curveTo(page_width * 0.73, page_height - 28 * mm, page_width * 0.88, page_height - 30 * mm, page_width, page_height - 23 * mm)
            p.lineTo(page_width, page_height - 34 * mm)
            p.lineTo(0, page_height - 34 * mm)
            p.close()
            canvas_obj.drawPath(p, fill=1, stroke=0)

            # Curved bottom theme
            canvas_obj.setFillColor(fwts_mint)
            p3 = canvas_obj.beginPath()
            p3.moveTo(0, 0)
            p3.lineTo(page_width, 0)
            p3.lineTo(page_width, 9 * mm)
            p3.curveTo(page_width - 40 * mm, 15 * mm, page_width - 95 * mm, 3 * mm, page_width - 135 * mm, 7 * mm)
            p3.curveTo(page_width - 175 * mm, 11 * mm, 50 * mm, 13 * mm, 0, 8 * mm)
            p3.close()
            canvas_obj.drawPath(p3, fill=1, stroke=0)

            canvas_obj.setStrokeColor(colors.HexColor('#BBF7D0'))
            canvas_obj.setLineWidth(0.9)
            canvas_obj.line(left_margin, 12 * mm, page_width - right_margin, 12 * mm)
            canvas_obj.restoreState()

            logo_reader = branding.get('logo_reader')
            if logo_reader:
                try:
                    # White badge behind logo so transparent/colored logos stay visible
                    logo_box_x = left_margin
                    logo_box_y = page_height - 33.5 * mm
                    logo_box_w = 26 * mm
                    logo_box_h = 24 * mm
                    canvas_obj.setFillColor(colors.white)
                    canvas_obj.roundRect(logo_box_x, logo_box_y, logo_box_w, logo_box_h, 2.8 * mm, stroke=0, fill=1)
                    canvas_obj.setStrokeColor(colors.HexColor('#BBF7D0'))
                    canvas_obj.setLineWidth(0.6)
                    canvas_obj.roundRect(logo_box_x, logo_box_y, logo_box_w, logo_box_h, 2.8 * mm, stroke=1, fill=0)

                    canvas_obj.drawImage(
                        logo_reader,
                        logo_box_x + 1.5 * mm,
                        logo_box_y + 1.0 * mm,
                        width=23 * mm,
                        height=22 * mm,
                        preserveAspectRatio=True,
                        mask='auto',
                    )
                except Exception:
                    pass
            else:
                # Logo fallback box when image is not configured.
                canvas_obj.setFillColor(colors.HexColor('#DCFCE7'))
                canvas_obj.roundRect(left_margin, page_height - 33.5 * mm, 26 * mm, 24 * mm, 2.8 * mm, stroke=0, fill=1)
                canvas_obj.setFillColor(colors.HexColor('#166534'))
                canvas_obj.setFont('Helvetica-Bold', 16)
                canvas_obj.drawCentredString(left_margin + 13 * mm, page_height - 20.2 * mm, 'F')

            canvas_obj.setFillColor(white)
            canvas_obj.setFont('Helvetica-Bold', 14)
            canvas_obj.drawString(left_margin + 30 * mm, page_height - 11.8 * mm, branding.get('title', 'FWTS'))
            canvas_obj.setFont('Helvetica', 8)
            canvas_obj.drawString(left_margin + 30 * mm, page_height - 16.4 * mm, branding.get('subtitle', 'Freelancer Work Tracking System'))
            canvas_obj.setFont('Helvetica', 7.5)
            canvas_obj.drawString(left_margin + 30 * mm, page_height - 20.8 * mm, f"{branding.get('address', 'FWTS Systems, India')} | {branding.get('contact', 'billing@fwts.in')}")

            canvas_obj.setFillColor(colors.HexColor('#166534'))
            canvas_obj.setFont('Helvetica-Bold', 8)
            canvas_obj.drawString(left_margin, 6.3 * mm, f"{branding.get('title', 'FWTS')} Invoice System")
            canvas_obj.setFont('Helvetica', 7.5)
            canvas_obj.drawString(left_margin + 42 * mm, 6.3 * mm, branding.get('address', 'FWTS Systems, India'))
            canvas_obj.drawRightString(page_width - right_margin, 6.3 * mm, f"Page {document.page}")

        story = []
        story.append(Paragraph('INVOICE', heading))
        story.append(Spacer(1, 1 * mm))

        invoice_info = payload['invoice']
        project_info = payload['project']
        client_info = payload['client']
        freelancer_info = payload['freelancer']

        info_table_data = [
            [
                Paragraph('<b>Invoice Number:</b>', normal),
                Paragraph(invoice_info['invoice_number'], normal),
                Paragraph('<b>Issue Date:</b>', normal),
                Paragraph(invoice_info['issue_date'], normal),
            ],
            [
                Paragraph('<b>Project:</b>', normal),
                Paragraph(project_info['name'], normal),
                Paragraph('<b>Due Date:</b>', normal),
                Paragraph(invoice_info['due_date'], normal),
            ],
            [
                Paragraph('<b>Currency:</b>', normal),
                Paragraph(invoice_info['currency'], normal),
                Paragraph('<b>Status:</b>', normal),
                Paragraph(invoice_info['status'], normal),
            ],
        ]
        info_table = Table(info_table_data, colWidths=[30 * mm, 70 * mm, 28 * mm, 52 * mm])
        info_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 4 * mm))

        parties_table = Table([
            [
                Paragraph('<b>From (Freelancer)</b>', section_label),
                Paragraph('<b>Bill To (Client)</b>', section_label),
            ],
            [
                Paragraph(
                    (
                        f"{freelancer_info['name']}<br/>"
                        f"{freelancer_info['email']}<br/>"
                        f"Address: {freelancer_info['address']}"
                    ),
                    normal,
                ),
                Paragraph(
                    (
                        f"{client_info['name']}<br/>"
                        f"{client_info['company']}<br/>"
                        f"{client_info['email']}<br/>"
                        f"Phone: {client_info['phone']}<br/>"
                        f"Address: {client_info['address']}"
                    ),
                    normal,
                ),
            ],
        ], colWidths=[90 * mm, 90 * mm])
        parties_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(parties_table)
        story.append(Spacer(1, 4 * mm))

        story.append(Paragraph('Task Line Items', section_label))
        task_rows = [[
            Paragraph('<b>#</b>', small),
            Paragraph('<b>Task</b>', small),
            Paragraph('<b>Status</b>', small),
            Paragraph('<b>Priority</b>', small),
            Paragraph('<b>Est Hrs</b>', small),
            Paragraph('<b>Act Hrs</b>', small),
            Paragraph('<b>Rate</b>', small),
            Paragraph('<b>Amount</b>', small),
        ]]

        for idx, item in enumerate(payload['task_items'], start=1):
            task_rows.append([
                Paragraph(str(idx), small),
                Paragraph(item['title'], small),
                Paragraph(item['status'], small),
                Paragraph(item['priority'], small),
                Paragraph(item['estimated_hours'], small),
                Paragraph(item['actual_hours'], small),
                Paragraph(item['rate'], small),
                Paragraph(item['amount'], small),
            ])

        if len(task_rows) == 1:
            task_rows.append([
                Paragraph('1', small),
                Paragraph('No tasks found for this project', small),
                Paragraph('-', small),
                Paragraph('-', small),
                Paragraph('0.00', small),
                Paragraph('0.00', small),
                Paragraph(f"0.00 {invoice_info['currency']}", small),
                Paragraph(f"0.00 {invoice_info['currency']}", small),
            ])

        task_table = Table(
            task_rows,
            colWidths=[8 * mm, 55 * mm, 20 * mm, 20 * mm, 18 * mm, 18 * mm, 23 * mm, 28 * mm],
            repeatRows=1,
        )
        task_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#CBD5E1')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(task_table)
        story.append(Spacer(1, 4 * mm))

        totals = payload['totals']
        totals_table = Table([
            [Paragraph('<b>Subtotal</b>', normal), Paragraph(totals['subtotal'], normal)],
            [Paragraph('<b>Tax</b>', normal), Paragraph(totals['tax'], normal)],
            [Paragraph('<b>Discount</b>', normal), Paragraph(totals['discount'], normal)],
            [Paragraph('<b>Total</b>', normal), Paragraph(totals['total'], normal)],
            [Paragraph('<b>Amount Due</b>', normal), Paragraph(totals['amount_due'], normal)],
        ], colWidths=[35 * mm, 40 * mm], hAlign='RIGHT')
        totals_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#CBD5E1')),
            ('BACKGROUND', (0, 3), (-1, 4), colors.HexColor('#F8FAFC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 4 * mm))

        story.append(Paragraph('Notes', section_label))
        story.append(Paragraph(payload['notes'], normal))
        story.append(Spacer(1, 1 * mm))
        story.append(Paragraph('Payment Terms', section_label))
        story.append(Paragraph(payload['payment_terms'], normal))
        story.append(Spacer(1, 1 * mm))
        story.append(Paragraph('Bank / Payout Details', section_label))
        payout = payload.get('payout_details', {})
        payout_value = ParagraphStyle(
            name='PayoutValue',
            parent=small,
            fontSize=9,
            leading=10,
            textColor=colors.HexColor('#0F172A'),
        )
        payout_table = Table([
            [Paragraph('<b>PAYMENT DETAILS (Use These For Transfer)</b>', ParagraphStyle(name='PayoutHeader', parent=small, fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)), Paragraph('', small)],
            [Paragraph('<b>Bank Name</b>', small), Paragraph(payout.get('bank_name', '__________'), payout_value)],
            [Paragraph('<b>Account Name</b>', small), Paragraph(payout.get('account_name', '__________'), payout_value)],
            [Paragraph('<b>Account Number</b>', small), Paragraph(payout.get('account_number', '__________'), payout_value)],
            [Paragraph('<b>SWIFT / IFSC</b>', small), Paragraph(payout.get('swift_ifsc', '__________'), payout_value)],
        ], colWidths=[44 * mm, 136 * mm])
        payout_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#86EFAC')),
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#15803D')),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F0FDF4')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(payout_table)

        doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
        return buffer.getvalue()

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
    def generate_project_invoice_pdf(user, client_id, project_id, payout_details=None):
        client = Client.objects.filter(id=client_id, user=user, is_active=True).first()
        if not client:
            raise ValidationError('Client not found')

        project = Project.objects.filter(id=project_id, user=user, client=client, is_active=True).first()
        if not project:
            raise ValidationError('Project not found for the selected client')

        tasks = Task.objects.filter(project=project, user=user, is_active=True).order_by('created_at')
        workspace = WorkspaceSetting.objects.order_by('-id').first()

        default_rate = InvoicingService._to_decimal(
            getattr(workspace, 'default_hourly_rate', None) or client.hourly_rate or project.hourly_rate or 0
        )
        tax_percent = InvoicingService._to_decimal(getattr(workspace, 'invoice_tax_default', 0) or 0)
        due_days = getattr(workspace, 'invoice_due_days_default', None) or client.payment_terms_days or 7
        due_days = int(due_days or 7)
        currency = project.currency or client.currency or getattr(workspace, 'currency', '') or 'USD'

        subtotal = Decimal('0.00')
        task_items = []
        for task in tasks:
            estimated_hours = InvoicingService._to_decimal(task.estimated_hours)
            actual_hours = InvoicingService._to_decimal(task.actual_hours)
            used_hours = actual_hours if actual_hours > 0 else estimated_hours
            rate = InvoicingService._to_decimal(task.hourly_rate or project.hourly_rate or client.hourly_rate or default_rate)
            line_amount = (used_hours * rate).quantize(Decimal('0.01'))
            subtotal += line_amount

            task_items.append({
                'title': task.title,
                'status': task.status.replace('_', ' ').title(),
                'priority': task.priority.title(),
                'estimated_hours': f'{estimated_hours:.2f}',
                'actual_hours': f'{actual_hours:.2f}',
                'rate': InvoicingService._format_money(rate, currency),
                'amount': InvoicingService._format_money(line_amount, currency),
            })

        tax_total = (subtotal * tax_percent / Decimal('100')).quantize(Decimal('0.01'))
        discount_total = Decimal('0.00')
        total_amount = (subtotal + tax_total - discount_total).quantize(Decimal('0.01'))

        issue_date = timezone.now().date()
        due_date = issue_date + timedelta(days=due_days)
        invoice_number = InvoicingService.generate_next_invoice_number()
        branding = InvoicingService._get_branding_assets()

        freelancer_address_parts = [
            user.first_name or '',
            user.last_name or '',
        ]
        freelancer_address = ' '.join([p for p in freelancer_address_parts if p]).strip() or 'Address not set'
        client_address = ', '.join([
            part for part in [
                client.address_line1,
                client.address_line2,
                client.city,
                client.state,
                client.postal_code,
                client.country,
            ] if part
        ]) or 'Address not set'

        payout_payload = {
            'bank_name': (payout_details or {}).get('bank_name') or '__________',
            'account_name': (payout_details or {}).get('account_name') or '__________',
            'account_number': (payout_details or {}).get('account_number') or '__________',
            'swift_ifsc': (payout_details or {}).get('swift_ifsc') or '__________',
        }

        payload = {
            'branding': branding,
            'pdf_title': f"Invoice {invoice_number}",
            'invoice': {
                'invoice_number': invoice_number,
                'issue_date': str(issue_date),
                'due_date': str(due_date),
                'currency': currency,
                'status': 'Draft',
            },
            'project': {
                'name': project.name,
            },
            'client': {
                'name': client.name,
                'company': client.company_name or '-',
                'email': client.email or '-',
                'phone': client.phone or '-',
                'address': client_address,
            },
            'freelancer': {
                'name': f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip() or user.email,
                'email': user.email,
                'address': freelancer_address,
            },
            'task_items': task_items,
            'totals': {
                'subtotal': InvoicingService._format_money(subtotal, currency),
                'tax': f"{InvoicingService._format_money(tax_total, currency)} ({tax_percent:.2f}%)",
                'discount': InvoicingService._format_money(discount_total, currency),
                'total': InvoicingService._format_money(total_amount, currency),
                'amount_due': InvoicingService._format_money(total_amount, currency),
            },
            'notes': project.notes or 'Work completed as per scope. Additional notes can be updated later.',
            'payment_terms': (
                f"Please process payment within {due_days} days from issue date. "
                "Late payment terms can be added later."
            ),
            'payment_details': (
                "Bank Name: {bank_name} | Account Name: {account_name} | "
                "Account Number: {account_number} | SWIFT/IFSC: {swift_ifsc}"
            ).format(**payout_payload),
            'payout_details': payout_payload,
        }

        pdf_bytes = InvoicingService._build_invoice_pdf_document(payload)
        file_name = f"invoice-{invoice_number}.pdf"
        storage_path = f"invoices/generated/{timezone.now().strftime('%Y/%m/%d')}/{file_name}"
        saved_path = default_storage.save(storage_path, ContentFile(pdf_bytes))
        file_url = default_storage.url(saved_path) if saved_path else ''

        return {
            'pdf_bytes': pdf_bytes,
            'file_name': file_name,
            'file_path': saved_path,
            'file_url': file_url,
            'pdf_url': file_url,
            'url': file_url,
            'invoice_number': invoice_number,
            'subtotal': str(subtotal),
            'tax_total': str(tax_total),
            'total_amount': str(total_amount),
            'currency': currency,
            'logo_path': branding.get('logo_path', ''),
        }

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
