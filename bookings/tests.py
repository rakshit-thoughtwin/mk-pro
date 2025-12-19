from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Booking, Person
from .services import BookingService
import datetime

class BookingSystemTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.date = datetime.date.today() + datetime.timedelta(days=1)
        self.date_str = self.date.strftime('%Y-%m-%d')
        self.segment = Booking.SEGMENT_MORNING

    def test_strict_api_format_success(self):
        payload = {
             "booking_date": self.date_str,
             "time_segment": self.segment,
             "primary_person_name": "John Doe",
             "primary_contact": "1234567890",
             "persons": [
                 {"name": "John", "aadhaar": "123", "identity_details": "x"},
                 {"name": "Jane", "aadhaar": "456", "identity_details": "y"}
             ]
        }
        response = self.client.post(reverse('booking-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertIn('error', data)
        self.assertEqual(data['status'], 201)
        self.assertFalse(data['error'])

    def test_booking_flow_and_capacity(self):
        # 1. Check availability initial
        res = self.client.get(reverse('slots'), {'date': self.date_str})
        self.assertEqual(res.data['data'][self.segment], 10)

        # 2. Create Booking A (4 people)
        b1_persons = [{"name": f"P{i}", "aadhaar": str(i), "identity_details": ""} for i in range(4)]
        payload1 = {
             "booking_date": self.date_str,
             "time_segment": self.segment,
             "primary_person_name": "User 1",
             "primary_contact": "111",
             "persons": b1_persons
        }
        res1 = self.client.post(reverse('booking-list'), payload1, format='json')
        self.assertEqual(res1.status_code, 201)
        b1_id = res1.json()['data']['id']
        
        # Verify status PENDING
        b1 = Booking.objects.get(id=b1_id)
        self.assertEqual(b1.status, Booking.STATUS_PENDING)

        # Availability should still be 10 (only APPROVED counts)
        res = self.client.get(reverse('slots'), {'date': self.date_str})
        self.assertEqual(res.data['data'][self.segment], 10)

        # 3. Approve Booking A
        success, msg = BookingService.approve_booking(b1_id)
        self.assertTrue(success)
        
        # Availability should be 6
        res = self.client.get(reverse('slots'), {'date': self.date_str})
        self.assertEqual(res.data['data'][self.segment], 6)

        # 4. Create Booking B (7 people) -> Should fail approval
        b2_persons = [{"name": f"Q{i}", "aadhaar": str(i), "identity_details": ""} for i in range(7)]
        payload2 = {
             "booking_date": self.date_str,
             "time_segment": self.segment,
             "primary_person_name": "User 2",
             "primary_contact": "222",
             "persons": b2_persons
        }
        res2 = self.client.post(reverse('booking-list'), payload2, format='json')
        b2_id = res2.json()['data']['id']

        success, msg = BookingService.approve_booking(b2_id)
        self.assertFalse(success)
        self.assertIn("Slots not available", msg)
        
        # 5. Create Booking C (6 people) -> Should succeed approval (Wait, 6+4=10)
        b3_persons = [{"name": f"R{i}", "aadhaar": str(i), "identity_details": ""} for i in range(6)]
        payload3 = {
             "booking_date": self.date_str,
             "time_segment": self.segment,
             "primary_person_name": "User 3",
             "primary_contact": "333",
             "persons": b3_persons
        }
        res3 = self.client.post(reverse('booking-list'), payload3, format='json')
        b3_id = res3.json()['data']['id']

        success, msg = BookingService.approve_booking(b3_id)
        self.assertTrue(success)

        # Availability should be 0
        res = self.client.get(reverse('slots'), {'date': self.date_str})
        self.assertEqual(res.data['data'][self.segment], 0)

    def test_validation_error_format(self):
        # Missing required field
        payload = {}
        response = self.client.post(reverse('booking-list'), payload, format='json')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertTrue(data['error'])
        # data['data'] should contain field errors

    def test_aadhaar_file_upload(self):
        # Create a dummy file
        file_content = b"dummy pdf content"
        uploaded_file = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")

        # Note: Nested Multipart upload in DRF with JSON + Files is tricky.
        # Usually, one sends multipart/form-data.
        # But our structure is:
        # { ... "persons": [ { ... "aadhaar_file": <FILE> } ] }
        # DRF's default JSONParser doesn't handle files. MultiPartParser handles flattened data.
        # Nested list of objects with files in multipart/form-data is complex to serialize for standard HTML forms/DRF.
        # However, DRF can handle it if we format keys like "persons[0]aadhaar_file".
        
        # Strategies:
        # 1. Base64 encode file in JSON (Easiest for JSON APIs).
        # 2. Separate endpoint for file upload.
        # 3. Multipart with specific naming convention.
        
        # Given the "Strict API" requirement and likely usage:
        # If we use Multipart, we need to adjust the test client.
        
        # Let's try sending as multipart/form-data with key indexing.
        
        payload = {
             "booking_date": self.date_str,
             "time_segment": self.segment,
             "primary_person_name": "File User",
             "primary_contact": "999",
             "persons[0]name": "File Person",
             "persons[0]aadhaar": "9999",
             "persons[0]aadhaar_file": uploaded_file
        }
        # We need to change the ModelViewSet to generally support MultiPartParser if we want this?
        # Default DRF parsers include JSONParser, FormParser, MultiPartParser.
        # But BookingSerializer expects a list of dicts for `persons`. 
        # Form/MultiPart data is a QueryDict. DRF's ModelSerializer w/ "many=True" nested writes usually fails with flat form data unless we use a custom parser or structure.
        
        # Actually, for this specific request, the user likely wants standard file handling.
        # DRF nested writable fields don't support file uploads well out-of-the-box with multipart.
        # Since I'm in "Backend-only" mode, I should probably stick to what works best or define the expectation.
        # If I strictly used JSON, I can't upload raw files (only Base64).
        
        # Let's try standard DRF test client multipart behavior which might just work if I format it right, 
        # OR I might fail and realize I need a better approach (like a separate upload endpoint).
        # But let's assume the client knows how to send `persons[0][name]` etc.
        
        # Update: DRF doesn't parse `persons[0][name]` automatically into nested lists for ModelSerializers by default.
        # It's a known pain point.
        # However, I didn't change the Parser classes, so it supports JSON and Multipart.
        # If I send JSON, I can't send the file.
        
        # Workaround for the TEST:
        # We'll skip the complexity of nested multipart test for now and just verify the MODEL supports it,
        # OR we assume the frontend sends separate requests? "Checkout" implies one go.
        # Let's assume the user accepts Base64 or standard multipart.
        
        # Let's actually implement a robust test that assumes JSON for metadata and Base64? 
        # No, FileField expects a file. 
        # Let's try to see if we can make it work with `format='multipart'` and the bracket syntax.
        # If not, I'll document the limitation or switching to Base64Field (drf-extra-fields).
        
        # For now, let's keep it simple. If this test fails on "nested data with multipart", 
        # I will know I need to fix the Serializer handling or install `drf-writable-nested` or similar.
        
        # Actually, simpler: Test that the FIELD exists and works on the model directly first?
        # No, integrated test is better.
        
        response = self.client.post(
            reverse('booking-list'), 
            payload, 
            format='multipart' # APIClient handles this
        )
        
        # Ideally verification:
        if response.status_code != 201:
             # Debugging fallback if nested multipart fails
             print(response.data)
             
        self.assertEqual(response.status_code, 201)
        booking_id = response.json()['data']['id']
        person = Person.objects.get(booking_id=booking_id)
        self.assertTrue(bool(person.aadhaar_file))
        self.assertTrue(person.aadhaar_file.name.endswith('.pdf'))
