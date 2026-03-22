from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.authentication import AdminJWTAuthentication
from core.services.Admin.dashboard_service import DashboardService
from common.responses import ApiResponse


class DashboardStatsView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = DashboardService.get_stats()
        return ApiResponse.success("Dashboard stats fetched successfully", data=data)


class RevenueChartView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year', None)
        if not year:
            from django.utils import timezone
            year = timezone.now().year
        data = DashboardService.get_revenue_chart(int(year))
        return ApiResponse.success("Revenue chart fetched successfully", data=data)


class TaskStatsView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = DashboardService.get_task_stats()
        return ApiResponse.success("Task stats fetched successfully", data=data)


class ActivityFeedView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = DashboardService.get_activity_feed()
        return ApiResponse.success("Activity feed fetched successfully", data=data)


class AnalysisView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'week')
        data = DashboardService.get_analysis(period)
        return ApiResponse.success("Analysis data fetched successfully", data=data)
