# Standardized API Response Formatter
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """
    Standardized API Response Format
    """

    @staticmethod
    def success(message="Success", data=None, status_code=status.HTTP_200_OK):
        """Success response format"""
        response_data = {
            "status": "success",
            "message": message,
            "data": data if data is not None else {}
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def error(message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Error response format"""
        response_data = {
            "status": "error",
            "message": message,
            "errors": errors if errors is not None else {}
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def created(message="Resource created successfully", data=None):
        """Created response format"""
        return APIResponse.success(message, data, status.HTTP_201_CREATED)

    @staticmethod
    def deleted(message="Resource deleted successfully"):
        """Deleted response format"""
        return APIResponse.success(message, {}, status.HTTP_200_OK)
