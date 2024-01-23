from django.test import TestCase
from django.urls import reverse
from attendance.models import (
    Student,
    SubjectClass,
    ClassAttendance,
    AttendanceStatus,
    ProjectConfiguration,
)
from django.contrib.auth.models import User
from django.utils import timezone  # Import the timezone module


class ClassAttendanceBtUrlBSMTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Test Student", mail="teststudent@sst.scaler.com"
        )
        self.attendance_marker_user = User.objects.create_user(
            username="staff", email="staff@mail.com", password=None, is_superuser=True
        )

        start_time = timezone.datetime(year=2023, month=12, day=8, hour=9, minute=0)
        end_time = timezone.datetime(year=2023, month=12, day=8, hour=12, minute=0)
        attendance_start_time = timezone.datetime(
            year=2023, month=12, day=8, hour=8, minute=50
        )
        attendance_end_time = timezone.datetime(
            year=2023, month=12, day=8, hour=9, minute=30
        )

        self.subject = SubjectClass.objects.create(
            name="Test Subject",
            attendance_start_time=timezone.make_aware(attendance_start_time),
            attendance_end_time=timezone.make_aware(attendance_end_time),
            class_start_time=timezone.make_aware(start_time),
            class_end_time=timezone.make_aware(end_time),
        )
        self.project_config = ProjectConfiguration.get_config()

    def test_get_aggregated_attendance_present(self):
        url = reverse("mark_attendance_subject", args=[self.subject.pk])
        data = {"mail": self.student.mail, "status": "present"}

        self.client.force_login(self.attendance_marker_user)
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        class_attendance = ClassAttendance.objects.get(
            subject=self.subject, student=self.student
        )
        self.assertEqual(class_attendance.attendance_status, AttendanceStatus.Present)

        data["status"] = "absent"
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)

        class_attendance = ClassAttendance.objects.get(
            subject=self.subject, student=self.student
        )
        self.assertEqual(class_attendance.attendance_status, AttendanceStatus.Absent)

    def test_get_aggregated_attendance_absent(self):
        self.project_config.INJEST_ATTENDANCE_IN_REAL_TIME = True
        self.project_config.save()
        url = reverse("mark_attendance_subject", args=[self.subject.pk])
        data = {"mail": self.student.mail, "status": "absent"}

        self.client.force_login(self.attendance_marker_user)
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        class_attendance = ClassAttendance.objects.get(
            subject=self.subject, student=self.student
        )
        self.assertEqual(class_attendance.attendance_status, AttendanceStatus.Absent)

        data["status"] = "present"
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)

        class_attendance = ClassAttendance.objects.get(
            subject=self.subject, student=self.student
        )
        self.assertEqual(class_attendance.attendance_status, AttendanceStatus.Present)
