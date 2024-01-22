import hmac
import requests
import json
import hashlib
from attendance.models import AttendanceStatus
from django.conf import settings

headers = {
    "Content-Type": "application/json",
}


def format_payload(data):
    return f"{data['user_email']}|{data['class_topic_slug']}|{data['super_batch_id']}|{data['attendance']}"


def generate_hmac(key, data, hash_function=hashlib.sha256):
    """Generate HMAC for the given data and key using the specified hash function."""
    hmac_hash = hmac.new(key.encode("utf-8"), data.encode("utf-8"), hash_function)
    return hmac_hash.hexdigest()


def make_http_request(data):
    url = settings.ATTENDANCE_INJESTION_URL
    json_payload = json.dumps(data)
    response = requests.post(url, data=json_payload, headers=headers)
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False


def injest_class_attendance_to_scaler(class_attendance):
    data = {
        "user_email": class_attendance.student.mail.replace(
            "@sst.scaler.com", "@ms.sst.scaler.com"
        ),
        "class_topic_slug": class_attendance.subject.class_topic_slug,
        "super_batch_id": class_attendance.subject.super_batch_id,
        "attendance": 1
        if class_attendance.attendance_status == AttendanceStatus.Present
        else 0,
    }
    payload = format_payload(data)
    data["checksum"] = generate_hmac(settings.ATTENDANCE_INJESTION_SIGNATURE, payload)

    return make_http_request(data)
