from django.test import TestCase
from django.urls import reverse
from attendance.models import ClassAttendanceByBSM
from attendance.models import Student, Subject, SubjectClass
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone


class DownloadCsvTest(TestCase):
    def setUp(self):
        self.students = [
            Student.objects.create(
                name="Test Student 1", mail="test_student1@sst.scaler.com"
            ),
            Student.objects.create(
                name="Test Student 2",
                mail="test_student2@sst.scaler.com",
            ),
            Student.objects.create(
                name="Test Student 3",
                mail="test_student3@sst.scaler.com",
            ),
        ]
        self.attendance_marker_user = User.objects.create_user(
            username="staff", email="staff@mail.com", password=None
        )

        self.subject = Subject.objects.create(
            name="Test Subject", instructor_name="Test Instructor"
        )
        # Use timezone.now() to get the current time in the test setup
        date_time = datetime.strptime("18/02/2024", "%d/%m/%Y")
        default_timezone = timezone.get_default_timezone()
        date_time = timezone.make_aware(date_time, default_timezone)

        self.subject_class = SubjectClass.objects.create(
            name="Test Class",
            attendance_start_time=date_time + timezone.timedelta(hours=8),
            attendance_end_time=date_time + timezone.timedelta(hours=9),
            class_start_time=date_time + timezone.timedelta(hours=8, minutes=30),
            class_end_time=date_time + timezone.timedelta(hours=9, minutes=30),
            is_attendance_mandatory=True,
            subject=self.subject,
        )
        self.class_attendances = []

        for student, status in zip(
            self.students, [a for (a, b) in ClassAttendanceByBSM.STATUS_CHOICES]
        ):
            class_attendance = ClassAttendanceByBSM.create_with(
                student,
                self.subject_class,
                status,
                marked_by=self.attendance_marker_user,
            )
            self.class_attendances.append(class_attendance)

    def test_generate_csv(self):
        expected_csv_content = (
            ",Test Subject 18/02/2024 => Test Class\r\n"
            "test_student1@sst.scaler.com,Proxy\r\n"
            "test_student2@sst.scaler.com,Present\r\n"
            "test_student3@sst.scaler.com,Absent\r\n"
        )

        # Reverse the URL to get the absolute path
        url = reverse("downloadAttendance", args=[self.subject_class.pk])

        # Make a GET request to the view
        response = self.client.get(url)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the content type is CSV
        self.assertEqual(response["Content-Type"], "text/csv")

        # Check if the CSV content matches the expected content
        self.assertEqual(
            response.content.decode("utf-8"),
            expected_csv_content,
            "Download attendance csv not working",
        )
