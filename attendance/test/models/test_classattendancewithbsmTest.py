from django.test import TestCase
from attendance.models import (
    ClassAttendanceByBSM,
    ClassAttendance,
    Student,
    SubjectClass,
    AttendanceStatus,
)
from django.contrib.auth.models import User
from django.utils import timezone


class ClassAttendanceWithBSMTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Test Student", mail="teststudent@sst.scaler.com"
        )
        self.attendance_marker_user = User.objects.create_user(
            username='staff', email='staff@mail.com', password=None
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

    def test_create_with_method_present(self):
        bsm_attendance = ClassAttendanceByBSM.create_with(
            self.student, self.subject, 'present', self.attendance_marker_user
        )
        class_attendance = bsm_attendance.class_attendance
        self.assertEqual(self.student, class_attendance.student)
        self.assertEqual(self.subject, class_attendance.subject)

        c = ClassAttendance.objects.get(student=self.student, subject=self.subject)
        attendance_by_bsm = ClassAttendanceByBSM.objects.get(
            class_attendance=c
        )
        self.assertIsNotNone(attendance_by_bsm)
        self.assertEqual(attendance_by_bsm.get_attendance_status(), AttendanceStatus.Present)

    def test_create_with_method_absent(self):
        bsm_attendance = ClassAttendanceByBSM.create_with(
            self.student, self.subject, 'absent', self.attendance_marker_user
        )
        class_attendance = bsm_attendance.class_attendance
        self.assertEqual(self.student, class_attendance.student)
        self.assertEqual(self.subject, class_attendance.subject)

        c = ClassAttendance.objects.get(student=self.student, subject=self.subject)
        attendance_by_bsm = ClassAttendanceByBSM.objects.get(
            class_attendance=c
        )
        self.assertIsNotNone(attendance_by_bsm)
        self.assertEqual(attendance_by_bsm.get_attendance_status(), AttendanceStatus.Absent)

