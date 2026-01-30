from rest_framework.response import Response
from django.http import JsonResponse

class ApiResponse:

    @staticmethod
    def success(message, data=None, status=200):
        return Response({
            "status": status,
            "message": message,
            "data": data
        }, status=status)

    @staticmethod
    def error(message, status=400):
        return Response({
            "status": status,
            "message": message
        }, status=status)

    @staticmethod
    def json_error(message, status=400):
        return JsonResponse({
            "status": status,
            "message": message
        }, status=status)
