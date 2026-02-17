from rest_framework.views import APIView
from rest_framework import status
from common.responses import ApiResponse
from core.serializers.User.operations_serializer import (
    ReportExportCreateSerializer,
    ReportExportSerializer,
    ProductivityRuleConfigSerializer,
    ProductivityScoreSerializer,
    ClientTrustRuleConfigSerializer,
    ClientTrustScoreSerializer,
    ClientRiskAlertSerializer,
)
from core.services.User.operations_service import (
    AnalysisService,
    ReportingService,
    ProductivityService,
    ClientTrustService,
)


class AnalysisSummaryView(APIView):
    def get(self, request):
        return ApiResponse.success('Analysis summary fetched successfully', AnalysisService.summary())


class AnalysisWebAnalyticsView(APIView):
    def get(self, request):
        days = int(request.query_params.get('days', 14))
        return ApiResponse.success('Web analytics fetched successfully', AnalysisService.web_analytics(period_days=days))


class AnalysisEarningsTrendView(APIView):
    def get(self, request):
        period = request.query_params.get('period', 'monthly')
        return ApiResponse.success('Earnings trend fetched successfully', AnalysisService.earnings_trend(period=period))


class AnalysisTimeAllocationView(APIView):
    def get(self, request):
        return ApiResponse.success('Time allocation fetched successfully', AnalysisService.time_allocation())


class AnalysisTopClientsView(APIView):
    def get(self, request):
        return ApiResponse.success('Top clients fetched successfully', AnalysisService.top_clients())


class AnalysisTaskAccuracyView(APIView):
    def get(self, request):
        return ApiResponse.success('Task accuracy fetched successfully', AnalysisService.task_accuracy())


class AnalysisInvoiceHealthView(APIView):
    def get(self, request):
        return ApiResponse.success('Invoice health fetched successfully', AnalysisService.invoice_health())


class AnalysisExportView(APIView):
    def get(self, request):
        data = ReportingService.monthly_bundle()
        return ApiResponse.success('Analysis export dataset fetched successfully', data)


class ReportEarningsView(APIView):
    def get(self, request):
        return ApiResponse.success('Earnings report fetched successfully', ReportingService.earnings_report())


class ReportTimeAllocationView(APIView):
    def get(self, request):
        return ApiResponse.success('Time allocation report fetched successfully', ReportingService.time_allocation_report())


class ReportProjectPerformanceView(APIView):
    def get(self, request):
        return ApiResponse.success('Project performance report fetched successfully', ReportingService.project_performance())


class ReportClientAnalyticsView(APIView):
    def get(self, request):
        return ApiResponse.success('Client analytics report fetched successfully', ReportingService.client_analytics())


class ReportMonthlyView(APIView):
    def get(self, request):
        return ApiResponse.success('Monthly report fetched successfully', ReportingService.monthly_bundle())


class ReportExportView(APIView):
    def post(self, request):
        serializer = ReportExportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ReportingService.export_report(serializer.validated_data)
        return ApiResponse.success('Report export generated successfully', ReportExportSerializer(report).data, status.HTTP_201_CREATED)


class ProductivitySummaryView(APIView):
    def get(self, request):
        data = ProductivityService.summary()
        if not data:
            return ApiResponse.success('Productivity summary fetched successfully', {})
        return ApiResponse.success('Productivity summary fetched successfully', ProductivityScoreSerializer(data).data)


class ProductivityWeeklyTrendView(APIView):
    def get(self, request):
        data = ProductivityService.weekly_trend()
        return ApiResponse.success('Productivity weekly trend fetched successfully', ProductivityScoreSerializer(data, many=True).data)


class ProductivityTaskVarianceView(APIView):
    def get(self, request):
        data = ProductivityService.task_variance()
        return ApiResponse.success('Productivity task variance fetched successfully', ProductivityScoreSerializer(data, many=True).data)


class ProductivityOnTimeRateView(APIView):
    def get(self, request):
        return ApiResponse.success('Productivity on-time rate fetched successfully', ProductivityService.on_time_rate())


class ProductivityUtilizationView(APIView):
    def get(self, request):
        return ApiResponse.success('Productivity utilization fetched successfully', ProductivityService.utilization())


class ProductivityRulesView(APIView):
    def patch(self, request):
        config = ProductivityService.update_rules(request.data)
        return ApiResponse.success('Productivity rules updated successfully', ProductivityRuleConfigSerializer(config).data)


class ClientTrustSummaryView(APIView):
    def get(self, request):
        return ApiResponse.success('Client trust summary fetched successfully', ClientTrustService.summary())


class ClientTrustClientsView(APIView):
    def get(self, request):
        data = ClientTrustService.clients()
        return ApiResponse.success('Client trust list fetched successfully', ClientTrustScoreSerializer(data, many=True).data)


class ClientTrustHistoryView(APIView):
    def get(self, request, client_id):
        data = ClientTrustService.history(client_id)
        return ApiResponse.success('Client trust history fetched successfully', [
            {
                'id': row.id,
                'event_type': row.event_type,
                'event_date': row.event_date,
                'days_delayed': row.days_delayed,
                'amount': row.amount,
                'score_impact': row.score_impact,
                'notes': row.notes,
            }
            for row in data
        ])


class ClientTrustRecalculateView(APIView):
    def post(self, request):
        data = ClientTrustService.recalculate()
        return ApiResponse.success('Client trust recalculated successfully', ClientTrustScoreSerializer(data, many=True).data)


class ClientTrustRulesView(APIView):
    def patch(self, request):
        config = ClientTrustService.update_rules(request.data)
        return ApiResponse.success('Client trust rules updated successfully', ClientTrustRuleConfigSerializer(config).data)


class ClientTrustAlertsView(APIView):
    def get(self, request):
        data = ClientTrustService.alerts()
        return ApiResponse.success('Client trust alerts fetched successfully', ClientRiskAlertSerializer(data, many=True).data)
