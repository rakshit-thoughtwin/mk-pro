from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, AvailableSlotsView

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('slots/', AvailableSlotsView.as_view(), name='slots'),
]
