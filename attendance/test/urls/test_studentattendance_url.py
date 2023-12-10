from django.test import TestCase
from django.urls import reverse
from attendance.models import Student


class getAttendance(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Test Student", mail="test@sst.scaler.com"
        )

    def test_studentAttendance_url(self):
        response = self.client.get(reverse("studentAttendance", args=["test"]))
        self.assertEqual(response.status_code, 200)
