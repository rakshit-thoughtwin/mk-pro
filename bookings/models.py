from django.db import models
from django.core.exceptions import ValidationError

class Booking(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    SEGMENT_MORNING = 'MORNING'
    SEGMENT_NOON = 'NOON'
    SEGMENT_EVENING = 'EVENING'
    SEGMENT_NIGHT = 'NIGHT'

    SEGMENT_CHOICES = [
        (SEGMENT_MORNING, 'Morning'),
        (SEGMENT_NOON, 'Noon'),
        (SEGMENT_EVENING, 'Evening'),
        (SEGMENT_NIGHT, 'Night'),
    ]

    booking_date = models.DateField()
    time_segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    primary_person_name = models.CharField(max_length=255)
    primary_contact = models.CharField(max_length=20)  # For SMS
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.primary_person_name} - {self.booking_date} ({self.time_segment})"

class Person(models.Model):
    booking = models.ForeignKey(Booking, related_name='persons', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    aadhaar = models.CharField(max_length=20) # Adjust length as needed
    aadhaar_file = models.FileField(upload_to='aadhaar_docs/', blank=True, null=True)
    identity_details = models.TextField(blank=True) # Any other details

    def __str__(self):
        return self.name
