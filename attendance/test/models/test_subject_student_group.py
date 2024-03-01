from django.test import TestCase
from django.contrib.auth.models import User


class SubjectStudentGroupTest(TestCase):
    test_comninations = [
        ("proxy", "proxy", AttendanceStatus.Proxy),
        ("proxy", "verified", AttendanceStatus.Proxy),
        ("proxy", "standby", AttendanceStatus.Proxy),
        ("proxy", "flaggers", AttendanceStatus.Proxy),
        ("present", "proxy", AttendanceStatus.Present),
        ("present", "verified", AttendanceStatus.Present),
        ("present", "standby", AttendanceStatus.Present),
        ("present", "flaggers", AttendanceStatus.Present),
        ("absent", "proxy", AttendanceStatus.Proxy),
        ("absent", "verified", AttendanceStatus.Present),
        ("absent", "standby", AttendanceStatus.Present),
        ("absent", "flaggers", AttendanceStatus.Absent),
    ]

    def setUp(self):
        self.student = Student.objects.create(
            name="Test Student", mail="teststudent@sst.scaler.com"
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
        self.user = User.objects.create(username="admin@admin.com")

    def test_with_geolocation_update(self):

