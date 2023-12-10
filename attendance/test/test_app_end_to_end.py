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
        )
        self.project_config = ProjectConfiguration.get_config()

    def register(self):
        token = encode_payload(
            {
                "iss": "test@sst.scaler.com",
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
        response = self.register()
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
        self.assertEquals(response.status_code, 200, "Mark attendance failed")

        response, content = self.fetch_attendance()
        self.assertEqual(
            response.status_code,
            200,
            "Fetch attendance failed after marking attendance",
        )
