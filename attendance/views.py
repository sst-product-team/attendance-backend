from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from attendance.models import (
    SubjectClass,
    Student,
    ProjectConfiguration,
    ClassAttendanceByBSM,
    AttendanceStatus,
    ClassAttendance,
    ProblemSolvingPercentage,
    GeoLocationDataContrib,
    FalseAttemptGeoLocation,
    ClassAttendanceWithGeoLocation,
)
from django.views.decorators.csrf import csrf_exempt
from utils.jwt_token_decryption import decode_jwt_token
import json
from utils.version_checker import compare_versions
from django.shortcuts import redirect, render
from django.urls import reverse
from utils.validate_location import is_in_class
from utils.pushNotification import pushNotification
from utils.push_to_google_sheet import sync_subject_class, can_sync_subject_class
from django.http import HttpResponse
import csv

import logging

db_logger = logging.getLogger("db")


def psp(request, mail_prefix):
    response = []

    student = Student.objects.get(mail__startswith=mail_prefix + "@")
    for p in ProblemSolvingPercentage.objects.filter(student=student):
        data = {}
        data["name"] = p.subject.name
        data["total_questions"] = p.total_questions
        data["solved_questions"] = p.solved_questions
        response.append(data)

    return JsonResponse({"data": response, "status": "success"})


def version(request):
    config = ProjectConfiguration.get_config()
    return JsonResponse(
        {
            "version": config.APP_LATEST_VERSION,
            "APK_FILE": config.APK_FILE,
            "VERSION_NAME": config.VERSION_NAME,
        }
    )


def ping(request):
    return JsonResponse({"message": "pong"})


@csrf_exempt
def index(request):
    data = json.loads(request.body)

    if (
        "accuracy" not in data
        or "version" not in data
        or compare_versions(
            data["version"], ProjectConfiguration.get_config().MIN_SUPPORTED_APP_VERSION
        )
        < 0
    ):
        return JsonResponse({"message": "Please update your app"}, status=400)

    payload = decode_jwt_token(data["jwtToken"])

    if "error" in payload:
        return JsonResponse({"message": data["error"]}, status=400)

    lat = data["latitutde"]
    lon = data["longitude"]
    token = payload["did"]

    accuracy = data["accuracy"]

    student = Student.objects.get(token=token)
    curr_class = SubjectClass.get_current_class()
    if curr_class is None:
        return JsonResponse({"message": "No class active for attendance"}, status=400)
    if not curr_class.is_attendance_by_geo_location_enabled:
        return JsonResponse(
            {"message": "Attendance can only be marked by BSM's for this class"},
            status=400,
        )
    if not curr_class.is_in_attendance_window():
        return JsonResponse(
            {
                "message": "You can mark Attendance between "
                + curr_class.attendance_start_time.astimezone().strftime("%I:%M %p")
                + " to "
                + curr_class.attendance_end_time.astimezone().strftime("%I:%M %p")
            },
            status=400,
        )

    if is_in_class(lat, lon, accuracy):
        if (
            ClassAttendance.get_attendance_status_for(
                student=student, subject=curr_class
            )
            == AttendanceStatus.Present
        ):
            return JsonResponse(
                {
                    "message": "Your attendance is already marked",
                    "class": curr_class.name,
                    "time": curr_class.attendance_start_time,
                }
            )
        attendance_geo = ClassAttendanceWithGeoLocation.create_with(
            student, curr_class, lat, lon, accuracy
        )
        attendance = attendance_geo.class_attendance
        if attendance.get_attendance_status() == AttendanceStatus.Present:
            if ProjectConfiguration.get_config().INJEST_ATTENDANCE_IN_REAL_TIME:
                try:
                    attendance.injest_to_scaler()
                except Exception:
                    pass
            return JsonResponse(
                {
                    "message": "Your attendance has been marked",
                    "class": curr_class.name,
                    "time": curr_class.attendance_start_time,
                }
            )
        else:
            return JsonResponse(
                {
                    "message": "Your attendance will be verified by BSM",
                    "status": "info",
                }
            )
    else:
        FalseAttemptGeoLocation.objects.create(
            student=student, subject=curr_class, lat=lat, lon=lon, accuracy=accuracy
        ).save()
        return JsonResponse(
            {"message": "Move a little inside classroom and mark again"}, status=400
        )


@csrf_exempt
def register(request):
    details = {}

    data = json.loads(request.body)

    if "jwtToken" not in data:
        return JsonResponse({"message": "Please update your app"}, status=400)

    details["name"] = data["name"]
    if "fcmtoken" in data:
        details["fcmtoken"] = data["fcmtoken"]
    else:
        details["fcmtoken"] = None
    data = decode_jwt_token(data["jwtToken"])

    if "error" in data:
        return JsonResponse({"message": data["error"]}, status=400)

    details["mail"] = data["iss"].lower()
    details["token"] = data["did"]

    user_obj = Student.get_object_with_mail(mail=details["mail"])
    if user_obj:
        if not user_obj.name:
            user_obj.name = details["name"]
            user_obj.save()

        if details["fcmtoken"] is not None:
            user_obj.fcmtoken = details["fcmtoken"]
            user_obj.save()

        if not user_obj.token:
            user_obj.token = details["token"]
            user_obj.save()
            return JsonResponse(details)
        elif user_obj.token == details["token"]:
            details["status"] = "success"
            return JsonResponse(details)
        else:
            # TODO: add to database and report to bsm
            return JsonResponse(
                {"message": "you can loggin in only one device", "status": "error"},
                status=400,
            )
    elif details["mail"].endswith("@sst.scaler.com") or details["mail"].endswith(
        "@scaler.com"
    ):
        student = Student.objects.create(
            name=details["name"],
            mail=details["mail"],
            token=details["token"],
            fcmtoken=details["fcmtoken"],
        )
        student.save()

        if details["mail"].endswith("@scaler.com"):
            student.create_django_user()
    else:
        return JsonResponse(
            {"message": "mail should end with @sst.scaler.com"}, status=400
        )

    details["status"] = "success"
    return JsonResponse(details)


@csrf_exempt
def geo(request):
    # check if request.body.token
    # print(request.body)
    data = json.loads(request.body)
    token = data["uid"]
    lat = str(data["latitutde"])
    lon = str(data["longitude"])
    accuracy = str(data["accuracy"])
    label = int(data["label"])

    student = Student.objects.get(token=token)

    obj = GeoLocationDataContrib.objects.create(
        label=label, student=student, lat=lat, lon=lon, accuracy=accuracy
    )
    obj.save()
    return JsonResponse({})


def fetchLatestAttendances(
    current_class, setForUnavailable=AttendanceStatus.Absent.name
):
    if not current_class:
        return JsonResponse(None, safe=False)

    all_attendance = current_class.get_all_attendance()

    details = {}
    details["name"] = current_class.name
    details["class_start_time"] = current_class.class_start_time
    details["class_end_time"] = current_class.class_end_time
    details["attendance_start_time"] = current_class.attendance_start_time
    details["attendance_end_time"] = current_class.attendance_end_time

    json_attendance = []
    mail_set = set()
    for attendance in all_attendance:
        json_attendance.append(
            {
                "mail": attendance.student.mail,
                "name": attendance.student.name,
                "status": attendance.get_attendance_status().name,
            }
        )
        mail_set.add(attendance.student.mail)
    response = {}
    response["current_class"] = details
    response["all_attendance"] = json_attendance

    all_students = current_class.get_all_students()

    for student in all_students:
        if student.mail not in mail_set:
            json_attendance.append(
                {
                    "mail": student.mail,
                    "name": student.name,
                    "status": setForUnavailable,
                }
            )
    return response


@csrf_exempt
def getcurclassattendance(request):
    data = json.loads(request.body)
    token = data["token"]

    curr_class = SubjectClass.get_current_class()
    if curr_class is None:
        return JsonResponse(None, safe=False)

    details = {}
    details["name"] = curr_class.name
    details["class_start_time"] = curr_class.class_start_time
    details["class_end_time"] = curr_class.class_end_time
    details["attendance_start_time"] = curr_class.attendance_start_time
    details["attendance_end_time"] = curr_class.attendance_end_time

    student = Student.get_object_with_token(token)
    attendance_status = ClassAttendance.get_attendance_status_for(
        student, curr_class
    ).name

    details["attendance_status"] = attendance_status

    return JsonResponse(details)


def injest_to_scaler(request, pk):
    if not Student.can_injest_to_scaler(request):
        return JsonResponse(
            {
                "message": "You are not authorized to access this page",
                "status": "error",
            },
            status=403,
        )

    attendances = ClassAttendance.objects.filter(
        is_injested=False,
        subject__class_topic_slug__gt="",
        subject__super_batch_id__gt=0,
        subject__pk=pk,
    )
    total_entries = len(attendances)

    success_pk = []
    failed_pk = []
    for attendance in attendances:
        result = attendance.injest_to_scaler()
        if result:
            success_pk.append(attendance.pk)
        else:
            failed_pk.append(attendance.pk)

    return JsonResponse(
        {
            "total_entries": total_entries,
            "success_count": len(success_pk),
            "failed_count": len(failed_pk),
            "failed_pk": failed_pk,
        }
    )


@csrf_exempt
def mark_attendance_subject(request, pk):
    if not Student.can_mark_attendance(request):
        return JsonResponse(
            {
                "message": "You are not authorized to access this page",
                "status": "error",
            },
            status=403,
        )
    db_logger.info(
        f"""[Mark Attendance]
by: {request.user.email},
body: {request.body},
url: {request.build_absolute_uri()}"""
    )
    curr_class = SubjectClass.objects.get(pk=pk)
    if curr_class is None:
        return JsonResponse({}, status=400)

    data = json.loads(request.body)

    mail = data["mail"]
    status = data["status"]

    student = Student.objects.get(mail=mail)

    bsm_attendance = ClassAttendanceByBSM.create_with(
        student, curr_class, status, request.user
    )
    attendance = bsm_attendance.class_attendance
    if ProjectConfiguration.get_config().INJEST_ATTENDANCE_IN_REAL_TIME:
        try:
            if not attendance.injest_to_scaler():
                print("unable to injest pk", attendance.class_attendance.pk)
        except Exception as e:
            print(e)

    return JsonResponse(
        {
            "mail": mail,
            "status": attendance.get_attendance_status().name,
        }
    )


def getAttendance(request, pk):
    cache_key = f"get_current_class_attendance_{pk}"
    if not request.user.is_staff:
        result = cache.get(cache_key)
        if result is not None:
            result["can_mark_attendance"] = Student.can_mark_attendance(request)
            return JsonResponse(result, safe=False)

    query_class = SubjectClass.objects.get(pk=pk)
    response = fetchLatestAttendances(query_class, setForUnavailable="-")

    if (not request.user.is_staff) or (cache.get(cache_key) is not None):
        cache.set(cache_key, response, 60 * 5)

    response["can_mark_attendance"] = Student.can_mark_attendance(request)

    return JsonResponse(response, safe=False)


def getAttendanceView(request, pk):
    if pk:
        getAttendanceURL = reverse("getAttendance", args=[pk])
        markAttendanceURL = reverse("mark_attendance_subject", args=[pk])
        noclass = False
    else:
        getAttendanceURL = None
        markAttendanceURL = None
        noclass = True
    return render(
        request,
        "attendance/index.html",
        {
            "markAttendanceURL": markAttendanceURL,
            "getAttendanceURL": getAttendanceURL,
            "noclass": noclass,
            "can_mark_attendance": Student.can_mark_attendance(request),
        },
    )


def studentAttendance(request, mail_prefix):
    student = Student.objects.get(mail__startswith=mail_prefix + "@")
    response = fetchAllStudentAttendances(student, include_optional=True)

    for a in response["all_attendance"]:
        if not a["status"]:
            a["status"] = AttendanceStatus.Absent.name

    sorted_attendance = sorted(
        response["all_attendance"], key=lambda x: x["class_start_time"], reverse=True
    )
    response["all_attendance"] = sorted_attendance

    aggregated_attendance = Student.get_aggregated_attendance(
        student=student, include_optional=False
    )

    overall_attendance = {}
    keys = ["totalClassCount", *AttendanceStatus.get_all_status()]
    for key in keys:
        overall_attendance[key] = 0

    for subject in aggregated_attendance:
        for key in keys:
            if key in aggregated_attendance[subject]:
                overall_attendance[key] += aggregated_attendance[subject][key]

    return render(
        request,
        "attendance/studentAttendance.html",
        {"data": response, "overall_attendance": overall_attendance},
    )


def fetchAllStudentAttendances(student, include_optional=False):
    if not student:
        return JsonResponse(None, safe=False)

    all_attendance = student.get_all_attendance(include_optional=include_optional)
    json_attendance = []
    subject_pk_set = set()
    for attendance in all_attendance:
        json_attendance.append(
            {
                "name": attendance.subject.name,
                "class_start_time": attendance.subject.class_start_time,
                "class_end_time": attendance.subject.class_end_time,
                "is_attendance_mandatory": attendance.subject.is_attendance_mandatory,
                "status": attendance.get_attendance_status().name,
            }
        )
        subject_pk_set.add(attendance.subject.pk)
    response = {}
    response["student"] = {
        "name": student.name,
        "mail": student.mail,
    }
    response["all_attendance"] = json_attendance

    all_subjects = SubjectClass.get_all_classes(include_optional=include_optional)

    for subject in all_subjects:
        if subject.pk not in subject_pk_set:
            json_attendance.append(
                {
                    "name": subject.name,
                    "class_start_time": subject.class_start_time,
                    "class_end_time": subject.class_end_time,
                    "is_attendance_mandatory": subject.is_attendance_mandatory,
                    "status": None,
                }
            )
    return response


title = "Attendance lagaya kya? 🧐"
description = "Lagao jaldi 🤬"


def sendNotification(request, pk):
    if not Student.can_send_notifications(request):
        return JsonResponse({"message": "Forbidden"}, status=400)
    student = Student.objects.get(pk=pk)
    if not student.fcmtoken:
        return JsonResponse({"message": "not send"}, status=400)
    pushNotification([student.fcmtoken], title, description)

    return JsonResponse({"message": "sent"})


def sendReminderForClass(request, pk):
    if not Student.can_send_notifications(request):
        return JsonResponse({"message": "Forbidden"}, status=400)

    subject = SubjectClass.objects.get(pk=pk)
    student_status = subject.get_all_students_attendance_status()
    students = [
        student
        for student, status in student_status
        if status == AttendanceStatus.Absent
    ]
    students = [student for student in students if student.fcmtoken]
    fcmtokens = [student.fcmtoken for student in students]

    admin = Student.objects.get(mail="diwakar.gupta@scaler.com")
    if admin.fcmtoken:
        fcmtokens.append(admin.fcmtoken)
    pushNotification(fcmtokens, title, description)

    return JsonResponse(
        {
            "message": f"Sent to {len(fcmtokens)} students",
            "sent_to": [s.name for s in students],
        }
    )


@csrf_exempt
def getTodaysClass(request):
    data = json.loads(request.body)
    token = data["token"]

    today_classes = SubjectClass.get_classes_for()
    student = Student.get_object_with_token(token)

    response = []

    for curr_class in today_classes:
        details = {}
        details["name"] = curr_class.name
        details["class_start_time"] = curr_class.class_start_time
        details["class_end_time"] = curr_class.class_end_time
        details["attendance_start_time"] = curr_class.attendance_start_time
        details["attendance_end_time"] = curr_class.attendance_end_time
        details["is_attendance_mandatory"] = curr_class.is_attendance_mandatory
        details["is_in_attendance_window"] = curr_class.is_in_attendance_window()
        details[
            "attendance_by_bsm_only"
        ] = not curr_class.is_attendance_by_geo_location_enabled
        attendance_status = ClassAttendance.get_attendance_status_for(
            student, curr_class
        ).name
        details["attendance_status"] = attendance_status

        response.append(details)

    return JsonResponse(response, safe=False)


@csrf_exempt
def get_aggregated_attendance(request):
    data = json.loads(request.body)
    token = data["token"]

    student = Student.get_object_with_token(token)
    response = Student.get_aggregated_attendance(
        student=student, include_optional=False
    )

    return JsonResponse(response)


def verify_false_attempt(request, pk):
    if not Student.can_verify_false_attempt(request):
        return JsonResponse({"message": "Forbidden"}, status=400)

    false_attempt = FalseAttemptGeoLocation.objects.get(pk=pk)
    ClassAttendanceWithGeoLocation.create_from(false_attempt, request.user)
    return JsonResponse({"message": "ok"})


def download_attendance_csv_for_subject_class(request, pk):
    query_class = SubjectClass.objects.get(pk=pk)
    attendanceData = fetchLatestAttendances(query_class)
    attendanceData = attendanceData["all_attendance"]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{str(query_class)}.csv"'

    csv_writer = csv.writer(response)
    csv_writer.writerow(
        [
            "",
            (query_class.subject.name if query_class.subject else "")
            + " "
            + str(query_class),
        ]
    )
    attendanceTable = []
    for at in attendanceData:
        attendanceTable.append([at["mail"], at["status"]])

    csv_writer.writerows(attendanceTable)

    return response


def sync_todays_class_with_google_drive(request, cron_token):
    if (
        not ProjectConfiguration.get_config().CRON_TOKEN
        or ProjectConfiguration.get_config().CRON_TOKEN != cron_token
    ):
        return JsonResponse({"message": "Forbidden"}, status=403)

    subjects = SubjectClass.get_classes_for()
    response = []
    for subject in subjects:
        if can_sync_subject_class(subject):
            sync_subject_class(subject)
            response.append(str(subject.pk) + " " + str(subject))

    db_logger.info(f"CRON: sync attendance with gsheet for {len(response)} classes")
    return JsonResponse(
        {
            "message": f"Synced {len(response)} classes",
            "subjects": response,
            "sheet_link": settings.GOOGLE_SHEET_LINK,
        }
    )


def sync_class_with_google_sheet_admin(request, pk):
    if not Student.can_sync_to_gsheet(request):
        return JsonResponse(
            {
                "message": "You are not authorized to access this page",
                "status": "error",
            },
            status=403,
        )
    curr_class = SubjectClass.objects.get(pk=pk)
    result = sync_subject_class(curr_class)
    if result:
        return redirect(settings.GOOGLE_SHEET_LINK)
    return JsonResponse(
        {
            "message": f"Syncing class {str(curr_class)} result: {result}",
            "sheet_link": settings.GOOGLE_SHEET_LINK,
        }
    )
