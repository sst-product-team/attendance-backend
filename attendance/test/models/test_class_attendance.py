from django.test import TestCase
from attendance.models import (
    ClassAttendanceWithGeoLocation,
    ClassAttendance,
    Student,
    SubjectClass,
    AttendanceStatus,
    ClassAttendanceByBSM,
)
from django.contrib.auth.models import User
from django.utils import timezone

class ClassAttendanceTest(TestCase):

    # bsm_status, geo_status, expected_result
    test_comninations = [
        ('proxy', 'proxy', AttendanceStatus.Proxy),
        ('proxy', 'verified', AttendanceStatus.Proxy),
        ('proxy', 'standby', AttendanceStatus.Proxy),
        ('proxy', 'flaggers', AttendanceStatus.Proxy),

        ('present', 'proxy', AttendanceStatus.Present),
        ('present', 'verified', AttendanceStatus.Present),
        ('present', 'standby', AttendanceStatus.Present),
        ('present', 'flaggers', AttendanceStatus.Present),
        
        ('absent', 'proxy', AttendanceStatus.Proxy),
        ('absent', 'verified', AttendanceStatus.Present),
        ('absent', 'standby', AttendanceStatus.Present),
        ('absent', 'flaggers', AttendanceStatus.Absent),
    ]
    
    def setUp(self):
        
        self.student = Student.objects.create(
            name="Test Student", mail="teststudent@sst.scaler.com"
        )
        start_time = timezone.datetime(year=2023, month=12, day=8, hour=9, minute=0)
        end_time = timezone.datetime(year=2023, month=12, day=8, hour=12, minute=0)
        attendance_start_time = timezone.datetime(year=2023, month=12, day=8, hour=8, minute=50)
        attendance_end_time = timezone.datetime(year=2023, month=12, day=8, hour=9, minute=30)
    
        self.subject = SubjectClass.objects.create(
            name="Test Subject",
            attendance_start_time=timezone.make_aware(attendance_start_time),
            attendance_end_time=timezone.make_aware(attendance_end_time),
            class_start_time=timezone.make_aware(start_time),
            class_end_time=timezone.make_aware(end_time),
        )
        self.user = User.objects.create(username="admin@admin.com")

    def test_with_geolocation_update(self):
        lat, lon, accuracy = 12.9715987, 77.5945627, 10.0

        class_attendance, geo_attendance = ClassAttendanceWithGeoLocation.create_with(
            self.student, self.subject, lat, lon, accuracy, return_obj=True
        )
        class_attendance_t, bsm_attendance = ClassAttendanceByBSM.create_with(
            self.student, self.subject, 'present', self.user, return_obj=True
        )

        self.assertEqual(class_attendance, class_attendance_t)
        self.assertEqual(class_attendance.get_attendance_status(), AttendanceStatus.Present)

        import random
        random.shuffle(ClassAttendanceTest.test_comninations)
        for (bsm_status, geo_status, expected_result) in ClassAttendanceTest.test_comninations:
            geo_attendance.status = geo_status
            geo_attendance.save()

            bsm_attendance.status = bsm_status
            bsm_attendance.save()

            result = ClassAttendance.objects.get(pk = class_attendance.pk).get_attendance_status()
            self.assertEqual(
                expected_result,
                result,
                f"With BSM status: {bsm_attendance.get_attendance_status()} & Geo status: {geo_attendance.get_attendance_status()} Expected was: {expected_result} but found {result}"
            )
