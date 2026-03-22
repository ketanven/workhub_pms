from django.utils import timezone
from core.models.operations import ReportExport


REPORT_TEMPLATES = [
    {
        "id": "time-report",
        "name": "Time Report",
        "description": "Tracked hours by date range, grouped by project and task.",
        "export_formats": ["PDF", "CSV"]
    },
    {
        "id": "invoice-report",
        "name": "Invoice Report",
        "description": "All invoices with status, amounts, and payment history.",
        "export_formats": ["PDF", "CSV", "Excel"]
    },
    {
        "id": "revenue-report",
        "name": "Revenue Report",
        "description": "Revenue collected and outstanding across all clients.",
        "export_formats": ["PDF", "CSV"]
    },
    {
        "id": "project-report",
        "name": "Project Report",
        "description": "Project progress, hours logged, and budget utilization.",
        "export_formats": ["PDF", "CSV"]
    },
    {
        "id": "freelancer-report",
        "name": "Freelancer Performance Report",
        "description": "Freelancer productivity, hours worked, and billing summary.",
        "export_formats": ["PDF", "CSV"]
    },
]


class ReportService:

    @staticmethod
    def get_templates():
        return REPORT_TEMPLATES

    @staticmethod
    def generate_report(template_id, file_format, time_range):
        # Find template name
        template_name = template_id
        for t in REPORT_TEMPLATES:
            if t['id'] == template_id:
                template_name = t['name']
                break

        export = ReportExport.objects.create(
            report_type=template_name,
            period_type='custom',
            filters_json={
                "template_id": template_id,
                "time_range": time_range
            },
            file_format=file_format.upper(),
            export_status='generated',
            requested_at=timezone.now(),
            completed_at=timezone.now(),
        )
        return {
            "id": export.id,
            "report_type": export.report_type,
            "format": export.file_format,
            "status": "Generated",
            "created_at": export.created_at.strftime("%Y-%m-%d %H:%M"),
        }

    @staticmethod
    def get_runs(limit=20):
        runs = ReportExport.objects.order_by('-created_at')[:limit]
        results = []
        for run in runs:
            time_range_str = ""
            if run.filters_json and 'time_range' in run.filters_json:
                tr = run.filters_json['time_range']
                time_range_str = f"{tr.get('start', '')} - {tr.get('end', '')}"

            results.append({
                "id": run.id,
                "report_type": run.report_type,
                "requested_by": "Admin",
                "time_range": time_range_str,
                "format": run.file_format,
                "status": run.export_status.title(),
                "created_at": run.created_at.strftime("%Y-%m-%d %H:%M"),
                "download_url": f"/api/admin/reports/runs/{run.id}/download/"
            })
        return results
