from django.urls import path
from core.controllers.User.auth_controller import (
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    UserChangePasswordView,
    UserForgotPasswordView,
    UserResetPasswordView
)
from core.controllers.User.client_controller import (
    UserClientListView,
    UserClientDetailView
)
from core.controllers.User.project_controller import (
    UserProjectListView,
    UserProjectDetailView
)
from core.controllers.User.task_controller import (
    UserTaskListView,
    UserTaskDetailView
)
from core.controllers.User.workbench_controller import (
    WorkbenchOverviewView,
    WorkbenchProjectsView,
    WorkbenchProjectTasksView,
    WorkbenchActiveTimerView,
    WorkbenchTimerStartView,
    WorkbenchTimerPauseView,
    WorkbenchTimerResumeView,
    WorkbenchTimerBreakStartView,
    WorkbenchTimerBreakStopView,
    WorkbenchTimerStopView,
    WorkbenchManualEntryView,
    WorkbenchTimeEntryListView,
    WorkbenchTimeEntryDetailView,
    WorkbenchSyncView,
)
from core.controllers.User.operations_controller import (
    AnalysisSummaryView,
    AnalysisWebAnalyticsView,
    AnalysisEarningsTrendView,
    AnalysisTimeAllocationView,
    AnalysisTopClientsView,
    AnalysisTaskAccuracyView,
    AnalysisInvoiceHealthView,
    AnalysisExportView,
    ReportEarningsView,
    ReportTimeAllocationView,
    ReportProjectPerformanceView,
    ReportClientAnalyticsView,
    ReportMonthlyView,
    ReportExportView,
    ProductivitySummaryView,
    ProductivityWeeklyTrendView,
    ProductivityTaskVarianceView,
    ProductivityOnTimeRateView,
    ProductivityUtilizationView,
    ProductivityRulesView,
    ClientTrustSummaryView,
    ClientTrustClientsView,
    ClientTrustHistoryView,
    ClientTrustRecalculateView,
    ClientTrustRulesView,
    ClientTrustAlertsView,
)
from core.controllers.User.invoicing_controller import (
    InvoiceListCreateView,
    InvoiceFromTimeEntriesView,
    InvoiceDetailView,
    InvoiceSubmitView,
    InvoiceSendView,
    InvoiceReminderView,
    InvoiceMarkPaidView,
    InvoicePaymentListCreateView,
    InvoicePDFView,
    InvoiceStatsView,
    InvoiceNumberingConfigView,
    InvoiceNumberPreviewView,
    InvoiceVersionListCreateView,
    InvoiceVersionDetailView,
    InvoiceVersionRestoreView,
)
from core.controllers.User.calendar_kanban_controller import (
    CalendarEventListCreateView,
    CalendarEventDetailView,
    CalendarTaskFeedView,
    CalendarInvoiceFeedView,
    KanbanBoardListCreateView,
    KanbanBoardDetailView,
    KanbanColumnCreateView,
    KanbanColumnDetailView,
    KanbanCardCreateView,
    KanbanCardDetailView,
    KanbanCardMoveView,
)
from core.controllers.User.platform_controller import (
    NotificationListView,
    NotificationReadView,
    FileUploadView,
    FileDetailView,
    WorkspaceSettingsView,
    HealthView,
)
from core.controllers.User.management_alias_controller import ProjectTaskListCreateAliasView
from django.utils.decorators import decorator_from_middleware
from core.middleware.user_auth import UserAuthMiddleware

user_auth_required = decorator_from_middleware(UserAuthMiddleware)

urlpatterns = [
    # Public routes
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('forgot-password/', UserForgotPasswordView.as_view(), name='user-forgot-password'),
    path('reset-password/', UserResetPasswordView.as_view(), name='user-reset-password'),
    
    # Protected routes
    path('profile/', user_auth_required(UserProfileView.as_view()), name='user-profile'),
    path('change-password/', user_auth_required(UserChangePasswordView.as_view()), name='user-change-password'),

    # Client Management
    path('clients/', user_auth_required(UserClientListView.as_view()), name='user-clients'),
    path('clients/<uuid:client_id>/', user_auth_required(UserClientDetailView.as_view()), name='user-client-detail'),

    # Project Management
    path('projects/', user_auth_required(UserProjectListView.as_view()), name='user-projects'),
    path('projects/<uuid:project_id>/', user_auth_required(UserProjectDetailView.as_view()), name='user-project-detail'),

    # Task Management
    path('tasks/', user_auth_required(UserTaskListView.as_view()), name='user-tasks'),
    path('tasks/<uuid:task_id>/', user_auth_required(UserTaskDetailView.as_view()), name='user-task-detail'),
    path('projects/<uuid:project_id>/tasks/', user_auth_required(ProjectTaskListCreateAliasView.as_view()), name='user-project-tasks'),

    # Workbench
    path('workbench/overview/', user_auth_required(WorkbenchOverviewView.as_view()), name='workbench-overview'),
    path('workbench/projects/', user_auth_required(WorkbenchProjectsView.as_view()), name='workbench-projects'),
    path('workbench/projects/<uuid:project_id>/tasks/', user_auth_required(WorkbenchProjectTasksView.as_view()), name='workbench-project-tasks'),
    path('workbench/timer/active/', user_auth_required(WorkbenchActiveTimerView.as_view()), name='workbench-timer-active'),
    path('workbench/timer/start/', user_auth_required(WorkbenchTimerStartView.as_view()), name='workbench-timer-start'),
    path('workbench/timer/pause/', user_auth_required(WorkbenchTimerPauseView.as_view()), name='workbench-timer-pause'),
    path('workbench/timer/resume/', user_auth_required(WorkbenchTimerResumeView.as_view()), name='workbench-timer-resume'),
    path('workbench/timer/break/start/', user_auth_required(WorkbenchTimerBreakStartView.as_view()), name='workbench-timer-break-start'),
    path('workbench/timer/break/stop/', user_auth_required(WorkbenchTimerBreakStopView.as_view()), name='workbench-timer-break-stop'),
    path('workbench/timer/stop/', user_auth_required(WorkbenchTimerStopView.as_view()), name='workbench-timer-stop'),
    path('workbench/time-entries/manual/', user_auth_required(WorkbenchManualEntryView.as_view()), name='workbench-manual-entry'),
    path('workbench/time-entries/', user_auth_required(WorkbenchTimeEntryListView.as_view()), name='workbench-time-entries'),
    path('workbench/time-entries/<int:entry_id>/', user_auth_required(WorkbenchTimeEntryDetailView.as_view()), name='workbench-time-entry-detail'),
    path('workbench/time-entries/sync/', user_auth_required(WorkbenchSyncView.as_view()), name='workbench-sync'),

    # Analysis
    path('analysis/summary/', user_auth_required(AnalysisSummaryView.as_view()), name='analysis-summary'),
    path('analysis/web-analytics/', user_auth_required(AnalysisWebAnalyticsView.as_view()), name='analysis-web-analytics'),
    path('analysis/earnings-trend/', user_auth_required(AnalysisEarningsTrendView.as_view()), name='analysis-earnings-trend'),
    path('analysis/time-allocation/', user_auth_required(AnalysisTimeAllocationView.as_view()), name='analysis-time-allocation'),
    path('analysis/top-clients/', user_auth_required(AnalysisTopClientsView.as_view()), name='analysis-top-clients'),
    path('analysis/task-accuracy/', user_auth_required(AnalysisTaskAccuracyView.as_view()), name='analysis-task-accuracy'),
    path('analysis/invoice-health/', user_auth_required(AnalysisInvoiceHealthView.as_view()), name='analysis-invoice-health'),
    path('analysis/export/', user_auth_required(AnalysisExportView.as_view()), name='analysis-export'),

    # Invoicing
    path('invoices/stats/', user_auth_required(InvoiceStatsView.as_view()), name='invoices-stats'),
    path('invoices/from-time-entries/', user_auth_required(InvoiceFromTimeEntriesView.as_view()), name='invoices-from-time-entries'),
    path('invoices/', user_auth_required(InvoiceListCreateView.as_view()), name='invoices'),
    path('invoices/<int:invoice_id>/', user_auth_required(InvoiceDetailView.as_view()), name='invoice-detail'),
    path('invoices/<int:invoice_id>/submit/', user_auth_required(InvoiceSubmitView.as_view()), name='invoice-submit'),
    path('invoices/<int:invoice_id>/send/', user_auth_required(InvoiceSendView.as_view()), name='invoice-send'),
    path('invoices/<int:invoice_id>/reminder/', user_auth_required(InvoiceReminderView.as_view()), name='invoice-reminder'),
    path('invoices/<int:invoice_id>/mark-paid/', user_auth_required(InvoiceMarkPaidView.as_view()), name='invoice-mark-paid'),
    path('invoices/<int:invoice_id>/payments/', user_auth_required(InvoicePaymentListCreateView.as_view()), name='invoice-payments'),
    path('invoices/<int:invoice_id>/pdf/', user_auth_required(InvoicePDFView.as_view()), name='invoice-pdf'),
    path('invoices/<int:invoice_id>/versions/', user_auth_required(InvoiceVersionListCreateView.as_view()), name='invoice-versions'),
    path('invoices/<int:invoice_id>/versions/<int:version_id>/', user_auth_required(InvoiceVersionDetailView.as_view()), name='invoice-version-detail'),
    path('invoices/<int:invoice_id>/versions/<int:version_id>/restore/', user_auth_required(InvoiceVersionRestoreView.as_view()), name='invoice-version-restore'),
    path('invoice-numbering/config/', user_auth_required(InvoiceNumberingConfigView.as_view()), name='invoice-numbering-config'),
    path('invoice-numbering/next/', user_auth_required(InvoiceNumberPreviewView.as_view()), name='invoice-numbering-next'),

    # Reports
    path('reports/earnings/', user_auth_required(ReportEarningsView.as_view()), name='reports-earnings'),
    path('reports/time-allocation/', user_auth_required(ReportTimeAllocationView.as_view()), name='reports-time-allocation'),
    path('reports/project-performance/', user_auth_required(ReportProjectPerformanceView.as_view()), name='reports-project-performance'),
    path('reports/client-analytics/', user_auth_required(ReportClientAnalyticsView.as_view()), name='reports-client-analytics'),
    path('reports/monthly/', user_auth_required(ReportMonthlyView.as_view()), name='reports-monthly'),
    path('reports/export/', user_auth_required(ReportExportView.as_view()), name='reports-export'),

    # Productivity
    path('productivity/summary/', user_auth_required(ProductivitySummaryView.as_view()), name='productivity-summary'),
    path('productivity/weekly-trend/', user_auth_required(ProductivityWeeklyTrendView.as_view()), name='productivity-weekly-trend'),
    path('productivity/task-variance/', user_auth_required(ProductivityTaskVarianceView.as_view()), name='productivity-task-variance'),
    path('productivity/on-time-rate/', user_auth_required(ProductivityOnTimeRateView.as_view()), name='productivity-on-time-rate'),
    path('productivity/utilization/', user_auth_required(ProductivityUtilizationView.as_view()), name='productivity-utilization'),
    path('productivity/rules/', user_auth_required(ProductivityRulesView.as_view()), name='productivity-rules'),

    # Client Trust
    path('client-trust/summary/', user_auth_required(ClientTrustSummaryView.as_view()), name='client-trust-summary'),
    path('client-trust/clients/', user_auth_required(ClientTrustClientsView.as_view()), name='client-trust-clients'),
    path('client-trust/clients/<uuid:client_id>/history/', user_auth_required(ClientTrustHistoryView.as_view()), name='client-trust-history'),
    path('client-trust/recalculate/', user_auth_required(ClientTrustRecalculateView.as_view()), name='client-trust-recalculate'),
    path('client-trust/rules/', user_auth_required(ClientTrustRulesView.as_view()), name='client-trust-rules'),
    path('client-trust/alerts/', user_auth_required(ClientTrustAlertsView.as_view()), name='client-trust-alerts'),

    # Calendar
    path('calendar/events/', user_auth_required(CalendarEventListCreateView.as_view()), name='calendar-events'),
    path('calendar/events/<int:event_id>/', user_auth_required(CalendarEventDetailView.as_view()), name='calendar-event-detail'),
    path('calendar/feeds/tasks/', user_auth_required(CalendarTaskFeedView.as_view()), name='calendar-feed-tasks'),
    path('calendar/feeds/invoices/', user_auth_required(CalendarInvoiceFeedView.as_view()), name='calendar-feed-invoices'),

    # Kanban
    path('kanban/boards/', user_auth_required(KanbanBoardListCreateView.as_view()), name='kanban-boards'),
    path('kanban/boards/<int:board_id>/', user_auth_required(KanbanBoardDetailView.as_view()), name='kanban-board-detail'),
    path('kanban/boards/<int:board_id>/columns/', user_auth_required(KanbanColumnCreateView.as_view()), name='kanban-columns-create'),
    path('kanban/columns/<int:column_id>/', user_auth_required(KanbanColumnDetailView.as_view()), name='kanban-column-detail'),
    path('kanban/columns/<int:column_id>/cards/', user_auth_required(KanbanCardCreateView.as_view()), name='kanban-cards-create'),
    path('kanban/cards/<int:card_id>/', user_auth_required(KanbanCardDetailView.as_view()), name='kanban-card-detail'),
    path('kanban/cards/<int:card_id>/move/', user_auth_required(KanbanCardMoveView.as_view()), name='kanban-card-move'),

    # Common Dashboard APIs
    path('notifications/', user_auth_required(NotificationListView.as_view()), name='notifications'),
    path('notifications/<int:id>/read/', user_auth_required(NotificationReadView.as_view()), name='notification-read'),
    path('files/upload/', user_auth_required(FileUploadView.as_view()), name='file-upload'),
    path('files/<uuid:fileId>/', user_auth_required(FileDetailView.as_view()), name='file-detail'),
    path('settings/workspace/', user_auth_required(WorkspaceSettingsView.as_view()), name='workspace-settings'),
    path('health/', HealthView.as_view(), name='api-health'),
]
