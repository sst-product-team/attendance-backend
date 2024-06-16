from django.test import TestCase
from django.urls import reverse
from attendance.models import SubjectClass


class DownloadCsvTest(TestCase):
    fixtures = ["fixtures_dev_db.json"]

    def test_generate_csv(self):
        subject_class = SubjectClass.objects.get(pk=78)

        expected_csv_content = (
            ",DSA 13/12/2023 => DSA 101: Linked Lists IV\r\n"
            "diwakar.gupta@scaler.com,Absent\r\n"
            "kushagra.23bcs10165@sst.scaler.com,Present\r\n"
            "pritam.23bcs10108@sst.scaler.com,Absent\r\n"
        )

        # Reverse the URL to get the absolute path
        url = reverse("downloadAttendance", args=[subject_class.pk])

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
