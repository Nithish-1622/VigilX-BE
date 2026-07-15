import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.views import exception_handler
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.http import Http404

logger = logging.getLogger("django.request")

def custom_exception_handler(exc, context):
    """
    Standardizes DRF exception response structure.
    """
    # Call DRF's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize the payload structure
        original_data = response.data
        detail_msg = "An error occurred."
        
        # If it's a dictionary and has 'detail', use it as the main message
        if isinstance(original_data, dict):
            if 'detail' in original_data:
                detail_msg = original_data.pop('detail')
            elif len(original_data) == 1:
                # If there's only one key, try to use it as detail
                key, value = list(original_data.items())[0]
                if isinstance(value, list) and len(value) > 0:
                    detail_msg = f"{key}: {value[0]}"
                else:
                    detail_msg = f"{key}: {value}"
            else:
                detail_msg = "Validation failed."
        elif isinstance(original_data, list) and len(original_data) > 0:
            detail_msg = original_data[0]

        # Determine error codes based on status code
        error_code = "API_ERROR"
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            error_code = "AUTHENTICATION_FAILED"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_code = "PERMISSION_DENIED"
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "NOT_FOUND"
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            error_code = "VALIDATION_ERROR"

        response.data = {
            "status": "error",
            "error_code": error_code,
            "message": detail_msg,
            "errors": original_data if isinstance(original_data, dict) else {"details": original_data}
        }
    else:
        # Django native exception conversions for Rest Framework views
        if isinstance(exc, Http404):
            return JsonResponse({
                "status": "error",
                "error_code": "NOT_FOUND",
                "message": "The requested resource was not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if isinstance(exc, PermissionDenied):
            return JsonResponse({
                "status": "error",
                "error_code": "PERMISSION_DENIED",
                "message": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

    return response


class ExceptionHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to catch raw Django/Python exceptions, log them,
    and return an enterprise-grade error structure with HTTP 500.
    """
    def process_exception(self, request, exception):
        # Log the exception stack trace internally
        logger.exception(f"Unhandled exception caught during request {request.path}: {str(exception)}")
        
        response_data = {
            "status": "error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please contact system support."
        }
        
        # In DEBUG mode, we can optionally attach details, but to respect the contract
        # we will keep the standard envelope.
        return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
