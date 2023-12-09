from django.test import TestCase
from attendance.models import (
    ClassAttendanceWithGeoLocation,
    ClassAttendance,
    Student,
    SubjectClass,
    AttendanceStatus,
)
from django.utils import timezone


class ClassAttendanceWithGeoLocationTest(TestCase):
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

    def test_create_with_method(self):
        lat, lon, accuracy = 12.9715987, 77.5945627, 10.0
        class_attendance = ClassAttendanceWithGeoLocation.create_with(
            self.student, self.subject, lat, lon, accuracy
        )
        self.assertEqual(self.student, class_attendance.student)
        self.assertEqual(self.subject, class_attendance.subject)

        c = ClassAttendance.objects.get(student=self.student, subject=self.subject)
        attendance_with_geo = ClassAttendanceWithGeoLocation.objects.get(
            class_attendance=c
        )
        self.assertIsNotNone(attendance_with_geo)
        self.assertAlmostEqual(float(attendance_with_geo.lat), lat)
        self.assertAlmostEqual(float(attendance_with_geo.lon), lon)
        self.assertAlmostEqual(float(attendance_with_geo.accuracy), accuracy)
        self.assertEqual(attendance_with_geo.status, "standby")

    def test_get_attendance_status_method(self):
        class_attendance = ClassAttendanceWithGeoLocation.create_with(
            self.student, self.subject, 12.9715987, 77.5945627, 10.0
        )
        class_attendance.status = "verified"
        class_attendance.save()
        attendance_with_geo = ClassAttendanceWithGeoLocation.objects.get(
            class_attendance=class_attendance
        )
        self.assertEqual(
            attendance_with_geo.get_attendance_status(), AttendanceStatus.Present
        )
