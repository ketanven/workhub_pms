from rest_framework.response import Response

class ApiResponse:

    @staticmethod
    def success(message, data=None, status=200):
        return Response({
            "status": True,
            "message": message,
            "data": data
        }, status=status)

    @staticmethod
    def error(message, status=400):
        return Response({
            "status": False,
            "message": message
        }, status=status)
