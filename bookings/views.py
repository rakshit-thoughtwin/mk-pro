from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count
from .models import Booking, Person
from .serializers import BookingSerializer
from .utils import api_response
from .services import BookingService
import datetime

class AvailableSlotsView(views.APIView):
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return api_response({}, 400, "Date parameter is required", True)
        
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return api_response({}, 400, "Invalid date format. Use YYYY-MM-DD", True)

        availability = {}
        for segment, _ in Booking.SEGMENT_CHOICES:
            # Count APPROVED persons for this segment
            # Note: We need to filter Person objects by booking__status=APPROVED
            used_count = Person.objects.filter(
                booking__booking_date=date_obj,
                booking__time_segment=segment,
                booking__status=Booking.STATUS_APPROVED
            ).count()
            
            available_slots = max(0, BookingService.MAX_SLOTS - used_count)
            availability[segment] = available_slots

        return api_response(availability, 200, "Slot availability retrieved")

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        # We override create to enforce the response format for success
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # According to requirements, checkout response should return data: {} not serializer.data
        return api_response({}, 201, "Your request has been submitted")

    # Assuming we don't expose list/update/delete generally, but ModelViewSet does.
    # The prompt explicitly asks for "Checkout / Create Booking".
    # I'll modify the list response to be compliant if accessed.
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return api_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(serializer.data)
