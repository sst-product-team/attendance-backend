from django.test import TestCase, Client
from utils.jwt_token_decryption import encode_payload
import json
from attendance.models import Student, Subject, SubjectClass, ProjectConfiguration
from django.utils import timezone
from utils.validate_location import AVG_LAT, AVG_LON


class EndToEndTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.some_random_did = "1234567890"
        self.fcmtoken = "fcmtokenfcmtokenfcmtoken"

        start_time = timezone.now() - timezone.timedelta(minutes=30)
        end_time = timezone.now() + timezone.timedelta(hours=1, minutes=30)
        attendance_start_time = start_time - timezone.timedelta(minutes=20)
        attendance_end_time = timezone.now() + timezone.timedelta(minutes=30)

        self.coursesubject = Subject.objects.create(
            name="DSA", instructor_name="Test instructor name"
        )
        self.subject = SubjectClass.objects.create(
            name="Test Subject",
            attendance_start_time=(attendance_start_time),
            attendance_end_time=(attendance_end_time),
            class_start_time=(start_time),
            class_end_time=(end_time),
            subject=self.coursesubject,
            is_attendance_by_geo_location_enabled=True,
        )
        self.project_config = ProjectConfiguration.get_config()
        self.project_config.INJEST_ATTENDANCE_IN_REAL_TIME = True
        self.project_config.save()

    def register(self, mail):
        token = encode_payload(
            {
                "iss": mail,
                "did": self.some_random_did,
            }
        )
        body = {
            "name": "Test User",
            "jwtToken": token,
            "fcmtoken": self.fcmtoken,
        }
        return self.client.post(
            "/attendance/register/", json.dumps(body), content_type="application/json"
        )

    def getcurclassattendance(self):
        return self.client.post(
            "/attendance/getcurclassattendance/",
            json.dumps({"token": self.some_random_did}),
            content_type="application/json",
        )

    def mark_attendance(self):
        token = encode_payload(
            {
                "iss": "",
                "did": self.some_random_did,
            }
        )

        body = {
            "jwtToken": token,
            "latitutde": AVG_LAT,
            "longitude": AVG_LON,
            "accuracy": 12,
            "version": self.project_config.MIN_SUPPORTED_APP_VERSION,
        }
        return self.client.post(
            "/attendance/", json.dumps(body), content_type="application/json"
        )

    def fetch_attendance(self):
        response = self.client.post(
            "/attendance/get_aggregated_attendance/",
            json.dumps({"token": self.some_random_did}),
            content_type="application/json",
        )
        content = json.loads(response.content.decode("utf-8"))

        return response, content

    def test_register_backend(self):
        response = self.register("test@sst.scaler.com")
        student = Student.objects.filter(mail="test@sst.scaler.com")
        self.assertTrue(student.exists(), "Student not created after registering")
        self.assertEquals(response.status_code, 200, "Student register failed")

        response = self.getcurclassattendance()
        self.assertEquals(response.status_code, 200, "Fetching Current class failed")

        response, content = self.fetch_attendance()
        self.assertEqual(
            response.status_code,
            200,
            "Fetch attendance failed with no marked attendance",
        )

        response = self.mark_attendance()
        self.assertEquals(200, response.status_code, "Mark attendance failed")

        response, content = self.fetch_attendance()
        self.assertEqual(
            response.status_code,
            200,
            "Fetch attendance failed after marking attendance",
        )

    def test_register_with_non_sst_mail(self):
        from django.db.models import Q

        mail = "test@example.com"
        response = self.register(mail)
        self.assertNotEqual(
            200, response.status_code, f"Student registered with mail {mail}"
        )

        self.assertEqual(
            False, Student.objects.filter(Q(mail=mail) | Q(personal_mail=mail)).exists()
        )

        response = self.register("test@sst.scaler.com")
        student = Student.objects.filter(mail="test@sst.scaler.com").first()
        obj = Student.get_object_with_mail(mail)

        self.assertEqual(None, obj)

        student.personal_mail = mail
        student.save()

        obj = Student.get_object_with_mail(mail)

        self.assertNotEqual(None, obj)
        self.assertEqual(mail, obj.personal_mail)
        self.assertEqual("test@sst.scaler.com", obj.mail)
