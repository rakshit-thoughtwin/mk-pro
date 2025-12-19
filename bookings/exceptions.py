from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Extract a more specific error message if available
        message = "An error occurred"
        if isinstance(response.data, dict):
            # Try to get a meaningful error message from validation errors
            if 'detail' in response.data:
                message = str(response.data['detail'])
            elif 'non_field_errors' in response.data:
                message = str(response.data['non_field_errors'][0]) if response.data['non_field_errors'] else message
        
        return Response({
            "data": response.data,
            "status": response.status_code,
            "message": message,
            "error": True
        }, status=response.status_code)

    return response
