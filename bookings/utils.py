from rest_framework.response import Response

def api_response(data={}, status=200, message="Success", error=False):
    return Response({
        "data": data,
        "status": status,
        "message": message,
        "error": error
    }, status=status)
