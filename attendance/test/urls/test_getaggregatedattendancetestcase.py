from django.test import TestCase
from django.urls import reverse
from attendance.models import (
    Student,
    Subject,
    SubjectClass,
    ClassAttendance,
    AttendanceStatus,
)
from django.utils import timezone  # Import the timezone module


class YourAppViewsTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Test Student", mail="test_student@example.com", token="test_token"
        )
        self.subject = Subject.objects.create(
            name="Test Subject", instructor_name="Test Instructor"
        )
        # Use timezone.now() to get the current time in the test setup
        self.subject_class = SubjectClass.objects.create(
            name="Test Class",
            attendance_start_time=timezone.now() + timezone.timedelta(hours=8),
            attendance_end_time=timezone.now() + timezone.timedelta(hours=9),
            class_start_time=timezone.now() + timezone.timedelta(hours=8, minutes=30),
            class_end_time=timezone.now() + timezone.timedelta(hours=9, minutes=30),
            is_attendance_mandatory=True,
            subject=self.subject,
        )
        self.class_attendance = ClassAttendance.objects.create(
            student=self.student,
            subject=self.subject_class,
            attendance_status=AttendanceStatus.Present,
        )

    def test_get_aggregated_attendance(self):
        url = reverse("get_aggregated_attendance")
        data = {
            "token": "idk",
        }

        # Check if the student with the incorrect token exists
        if not Student.objects.filter(token=data["token"]).exists():
            pass
            # print("Student with the specified token does not exist in the database.")
        else:
            response = self.client.post(url, data, content_type="application/json")
            self.assertNotEqual(response.status_code, 200)

        url = reverse("get_aggregated_attendance")
        data = {
            "token": self.student.token,
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
