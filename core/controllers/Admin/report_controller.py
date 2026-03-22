from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.authentication import AdminJWTAuthentication
from core.services.Admin.report_service import ReportService
from common.responses import ApiResponse


class ReportTemplateListView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = ReportService.get_templates()
        return ApiResponse.success("Report templates fetched successfully", data=data)


class ReportGenerateView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        template_id = request.data.get('template_id')
        file_format = request.data.get('format', 'PDF')
        time_range = request.data.get('time_range', {})

        if not template_id:
            return ApiResponse.error("template_id is required", status=status.HTTP_400_BAD_REQUEST)

        data = ReportService.generate_report(template_id, file_format, time_range)
        return ApiResponse.success("Report generated successfully", data=data, status=status.HTTP_201_CREATED)


class ReportRunListView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = ReportService.get_runs()
        return ApiResponse.success("Report runs fetched successfully", data=data)
