from django.contrib import admin
from .models import Booking, Person
from .services import BookingService

class PersonInline(admin.TabularInline):
    model = Person
    extra = 0

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    inlines = [PersonInline]
    list_display = ('booking_representation', 'booking_date', 'time_segment', 'status', 'created_at')
    list_filter = ('status', 'booking_date', 'time_segment')
    actions = ['approve_bookings', 'reject_bookings']

    def booking_representation(self, obj):
        count = obj.persons.count()
        return f"{obj.primary_person_name} -> qty({count})"
    booking_representation.short_description = 'Booking Details'

    @admin.action(description='Approve selected bookings')
    def approve_bookings(self, request, queryset):
        success_count = 0
        failure_count = 0
        
        for booking in queryset:
            success, message = BookingService.approve_booking(booking.id)
            if success:
                success_count += 1
            else:
                failure_count += 1
                self.message_user(request, f"Could not approve {booking}: {message}", level='error')
        
        if success_count:
            self.message_user(request, f"Successfully approved {success_count} bookings.")

    @admin.action(description='Reject selected bookings')
    def reject_bookings(self, request, queryset):
        count = 0
        for booking in queryset:
            BookingService.reject_booking(booking.id)
            count += 1
        self.message_user(request, f"Rejected {count} bookings.")

admin.site.register(Person)
