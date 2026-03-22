from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.authentication import AdminJWTAuthentication
from core.services.Admin.invoice_service import InvoiceService
from common.responses import ApiResponse


class AdminInvoiceListView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status = request.query_params.get('status', 'all')
        freelancer_id = request.query_params.get('freelancer_id', 'all')
        search = request.query_params.get('search', None)
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        data = InvoiceService.get_invoices(
            status=status,
            freelancer_id=freelancer_id,
            search=search,
            page=page,
            page_size=page_size
        )
        return ApiResponse.success("Invoices fetched successfully", data=data)


class AdminFreelancerListView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = InvoiceService.get_freelancers()
        return ApiResponse.success("Freelancers fetched successfully", data=data)
