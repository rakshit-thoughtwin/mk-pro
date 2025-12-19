from django.db import transaction
from .models import Booking, Person

class NotificationService:
    @staticmethod
    def send_sms(phone, message):
        # Mock SMS sending
        print(f"[{phone}] SMS: {message}")

class BookingService:
    MAX_SLOTS = 10

    @staticmethod
    def approve_booking(booking_id):
        with transaction.atomic():
            # Lock the booking to prevent race conditions on the booking itself
            booking = Booking.objects.select_for_update().get(id=booking_id)
            
            if booking.status != Booking.STATUS_PENDING:
                return False, "Booking is not pending"

            # Calculate current usage for the target segment
            # We must lock the relevant rows or ensure we are reading consistent state.
            # Ideally, we should lock all "Approved" bookings for this date/segment to prevent concurrent approvals exceeding limit.
            # But select_for_update() on filter() is tricky if rows don't exist.
            # A common pattern is to just count. Phantom reads are possible in some isolation levels, but default is Read Committed.
            # For strict correctness, we might need to lock a parent 'Slot' row, but we don't have one.
            # We can select_for_update() on the Person table for this date/segment?
            # Or just rely on the fact that we are in a transaction and checking.
            # To be strictly safe against race conditions where two txns checks sum < 10 at same time:
            # We need serialization. select_for_update() on the *Bookings* of that day helps if we mistakenly lock *all*. 
            # Better approach: `Bookings.objects.select_for_update().filter(...)` locks existing.
            
            # Simplified strict approach:
            # Lock all bookings for that date/segment.
            _ = list(Booking.objects.select_for_update().filter(
                booking_date=booking.booking_date,
                time_segment=booking.time_segment
            ))

            current_usage = Person.objects.filter(
                booking__booking_date=booking.booking_date,
                booking__time_segment=booking.time_segment,
                booking__status=Booking.STATUS_APPROVED
            ).count()

            booking_size = booking.persons.count()

            if current_usage + booking_size > BookingService.MAX_SLOTS:
                # Reject if full - according to requirements, auto-reject and send SMS
                booking.status = Booking.STATUS_REJECTED
                booking.save()
                NotificationService.send_sms(booking.primary_contact, "Slots not available, booking rejected")
                return False, "Slots not available, booking rejected"

            # Approve
            booking.status = Booking.STATUS_APPROVED
            booking.save()
            
            NotificationService.send_sms(booking.primary_contact, "Your booking is confirmed")
            return True, "Booking approved"

    @staticmethod
    def reject_booking(booking_id):
        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(id=booking_id)
            if booking.status == Booking.STATUS_REJECTED:
                 return True, "Already rejected"
            
            booking.status = Booking.STATUS_REJECTED
            booking.save()
            NotificationService.send_sms(booking.primary_contact, "Your booking has been rejected")
            return True, "Booking rejected"
