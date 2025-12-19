from rest_framework import serializers
from .models import Booking, Person
from django.db import transaction

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['name', 'aadhaar', 'aadhaar_file', 'identity_details']

class BookingSerializer(serializers.ModelSerializer):
    persons = PersonSerializer(many=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_date', 'time_segment', 'status',
            'primary_person_name', 'primary_contact',
            'persons', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate_persons(self, value):
        if not value:
            raise serializers.ValidationError("At least one person is required.")
        return value

    def create(self, validated_data):
        persons_data = validated_data.pop('persons')
        with transaction.atomic():
            booking = Booking.objects.create(**validated_data)
            for person_data in persons_data:
                Person.objects.create(booking=booking, **person_data)
        return booking
