import json, traceback

# Test Dashboard Service
from core.services.Admin.dashboard_service import DashboardService
from core.services.Admin.invoice_service import InvoiceService
from core.services.Admin.report_service import ReportService

tests = [
    ("Dashboard Stats", lambda: DashboardService.get_stats()),
    ("Revenue Chart", lambda: DashboardService.get_revenue_chart(2026)),
    ("Task Stats", lambda: DashboardService.get_task_stats()),
    ("Activity Feed", lambda: DashboardService.get_activity_feed()),
    ("Analysis (week)", lambda: DashboardService.get_analysis('week')),
    ("Invoices", lambda: InvoiceService.get_invoices()),
    ("Freelancers", lambda: InvoiceService.get_freelancers()),
    ("Report Templates", lambda: ReportService.get_templates()),
    ("Report Runs", lambda: ReportService.get_runs()),
    ("Generate Report", lambda: ReportService.generate_report("time-report", "PDF", {"start": "2026-01-01", "end": "2026-01-31"})),
]

for name, fn in tests:
    try:
        result = fn()
        print(f"[OK] {name}: {json.dumps(result, default=str)[:200]}")
    except Exception as e:
        print(f"[FAIL] {name}")
        traceback.print_exc()
