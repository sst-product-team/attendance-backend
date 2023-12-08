from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from attendance.models import (
    SubjectClass,
    Student,
    ProjectConfiguration,
    ClassAttendanceByBSM,
    AttendanceStatus,
    ClassAttendance,
    GeoLocationDataContrib,
    FalseAttemptGeoLocation,
    ClassAttendanceWithGeoLocation,
)
import json
from rest_framework import status
from django.core.cache import cache
from utils.version_checker import compare_versions
from .models import SubjectClass
from .views import fetchLatestAttendances
from utils.jwt_token_decryption import decode_jwt_token
from utils.validate_location import is_in_class
from utils.pushNotification import pushNotification
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect



title = "Attendance lagaya kya? 🧐"
description = "Lagao jaldi 🤬"

# Method 1
@api_view(['GET'])
def version(request):
    config = ProjectConfiguration.get_config()
    return Response({
        "version": config.APP_LATEST_VERSION, 
        "APK_FILE": config.APK_FILE
    })



# Method 2
@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    return Response({"message": "pong"})

# Method 3
def index(request):
    return redirect('AttendanceView')

class AttendanceView(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data

        if (
            "accuracy" not in data
            or "version" not in data
            or compare_versions(
                data["version"], ProjectConfiguration.get_config().APP_LATEST_VERSION
            )
            < 0
        ):
            return Response({"message": "Please update your app"}, status=status.HTTP_400_BAD_REQUEST)

        payload = decode_jwt_token(data["jwtToken"])

        if "error" in payload:
            return Response({"message": data["error"]}, status=status.HTTP_400_BAD_REQUEST)

        lat = data["latitutde"]
        lon = data["longitude"]
        token = payload["did"]

        accuracy = data["accuracy"]

        student = Student.objects.get(token=token)
        curr_class = SubjectClass.get_current_class()
        if curr_class == None:
            return Response({"message": "No class active for attendance"}, status=status.HTTP_400_BAD_REQUEST)
        if not curr_class.is_attendance_by_geo_location_enabled:
            return Response(
                {
                    "message": "Attendance can only be marked by BSM's for this class"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not curr_class.is_in_attendance_window():
            return Response(
                {
                    "message": "You can mark Attendance between "
                    + curr_class.attendance_start_time.astimezone().strftime("%I:%M %p")
                    + " to "
                    + curr_class.attendance_end_time.astimezone().strftime("%I:%M %p")
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_in_class(lat, lon, accuracy):
            if ClassAttendance.get_attendance_status_for(student=student, subject=curr_class) == AttendanceStatus.Present:
                return Response(
                    {"message": "Your attendance is already marked", "class": curr_class.name, "time": curr_class.attendance_start_time}
                )
            attendance = ClassAttendanceWithGeoLocation.create_with(
                student, curr_class, lat, lon, accuracy
            )
            if attendance.get_attendance_status() == AttendanceStatus.Present:
                return Response(
                    {"message": "Your attendance has been marked", "class": curr_class.name, "time": curr_class.attendance_start_time}
                )
            else:
                return Response(
                    {"message": "Your attendance will be verified by BSM", "status":"info",}
                )
        else:
            FalseAttemptGeoLocation.objects.create(
                student=student, subject=curr_class, lat=lat, lon=lon, accuracy=accuracy
            ).save()
            return Response(
                {"message": "Move a little inside classroom and mark again"}, status=status.HTTP_400_BAD_REQUEST
            )

    
# Method 4
def register(request):
    return redirect('RegisterView')

class RegisterView(APIView):
    @csrf_exempt
    def post(self, request):
        details = {}

        data = request.data

        if "jwtToken" not in data:
            return Response({"message": "Please update your app"}, status=400)

        details["name"] = data["name"]
        if "fcmtoken" in data:
            details["fcmtoken"] = data["fcmtoken"]
        else:
            details["fcmtoken"] = None 
        data = decode_jwt_token(data["jwtToken"])

        if "error" in data:
            return Response({"message": data["error"]}, status=400)

        details["mail"] = data["iss"].lower()
        details["token"] = data["did"]

        if not (
            details["mail"].endswith("@sst.scaler.com")
            or details["mail"].endswith("@scaler.com")
        ):
            return Response(
                {"message": "mail should end with @sst.scaler.com"}, status=400
            )

        user_object_query = Student.objects.filter(mail=details["mail"])
        if user_object_query.exists():
            user_obj = user_object_query.first()

            if not user_obj.name:
                user_obj.name = details["name"]
                user_obj.save()
            
            if  details["fcmtoken"] != None:
                user_obj.fcmtoken = details["fcmtoken"]
                user_obj.save()

            if not user_obj.token:
                user_obj.token = details["token"]
                user_obj.save()
                return Response(details)
            elif user_obj.token == details["token"]:
                details["status"] = "success"
                return Response(details)
            else:
                # TODO: add to database and report to bsm
                return Response(
                    {"message": "you can loggin in only one device", "status": "error"},
                    status=400,
                )
        else:
            student = Student.objects.create(
                name=details["name"], mail=details["mail"], token=details["token"], fcmtoken=details["fcmtoken"]
            )
            student.save()

            if details["mail"].endswith("@scaler.com"):
                student.create_django_user()

        details["status"] = "success"
        return Response(details)
    
# Method 5
def geo(request):
    return redirect('GeoView')

class GeoView(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
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
        return Response(status=status.HTTP_200_OK)

# Method 6
def get_all_attendance(request):
    return redirect('AllAttendanceView')

class AllAttendanceView(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        token = data["token"]

        student = Student.get_object_with_token(token)
        all_attendances_obj = ClassAttendance.all_subject_attendance(student)

        all_attendances = []
        for subject_class in all_attendances_obj:
            details = {}
            details["name"] = subject_class["name"]
            details["class_start_time"] = subject_class["class_start_time"]
            details["class_end_time"] = subject_class["class_end_time"]
            details["attendance_time"] = subject_class["min_creation_time"]
            all_attendances.append(details)

        return Response(all_attendances)
    
# Method 7
def fetchLatestAttendances(current_class):
    return redirect('LatestAttendanceView')

class LatestAttendanceView(APIView):
    @csrf_exempt
    def post(self, request, current_class):
        if not current_class:
            return Response(None, status=status.HTTP_204_NO_CONTENT)

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

        all_students = Student.get_all_students()

        for student in all_students:
            if student.mail not in mail_set:
                json_attendance.append(
                    {
                        "mail": student.mail,
                        "name": student.name,
                        "status": AttendanceStatus.Absent.name,
                    }
                )
        return Response(response)

## Method 8
@api_view(['GET'])
def get_current_class_attendance(request):
    cache_key = "get_current_class_attendance"

    if not request.user.is_staff:
        result = cache.get(cache_key)
        if result is not None:
            return Response(result)

    current_class = SubjectClass.get_current_class()
    response = fetchLatestAttendances(current_class)
    cache.set(cache_key, response, 60 * 5)

    return Response(response)

# Method 9
@api_view(['POST'])
@csrf_exempt
def getcurclassattendance(request):
    data = json.loads(request.body)
    token = data["token"]

    curr_class = SubjectClass.get_current_class()
    if curr_class == None:
        return Response(None)

    details = {}
    details["name"] = curr_class.name
    details["class_start_time"] = curr_class.class_start_time
    details["class_end_time"] = curr_class.class_end_time
    details["attendance_start_time"] = curr_class.attendance_start_time
    details["attendance_end_time"] = curr_class.attendance_end_time

    student = Student.get_object_with_token(token)
    attendance_status = ClassAttendance.get_attendance_status_for(student, curr_class).name

    details["attendance_status"] = attendance_status

    return Response(details)

#Method 10
@api_view(['GET'])
def injest_to_scaler(request, pk):
    if not request.user.is_superuser:
        return Response(
            {
                "message": "You are not authorized to access this page",
                "status": "error",
            },
            status=403,
        )

    return Response({"PK": pk})

# Method 11
@api_view(['GET'])
def can_mark_attendance(request):
    return Response(request.user.is_staff)

# Method 12
def mark_attendance(request):
    return redirect('MarkAttendance')

class MarkAttendance(APIView):
    @csrf_exempt
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {
                    "message": "You are not authorized to access this page",
                    "status": "error",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        curr_class = SubjectClass.get_current_class()
        if curr_class == None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        mail = data["mail"]
        status = data["status"]

        student = Student.objects.get(mail=mail)

        attendance = ClassAttendanceByBSM.create_with(
            student, curr_class, status, request.user
        )
        attendance.save()

        return Response(
            {
                "mail": mail,
                "status": attendance.class_attendance.get_attendance_status().name,
            }
        )
    
# Method 12
def mark_attendance_subject(request, pk):
    return redirect('MarkAttendanceSubject')

class MarkAttendanceSubject(APIView):
    @csrf_exempt
    def post(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {
                    "message": "You are not authorized to access this page",
                    "status": "error",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        curr_class = SubjectClass.objects.get(pk=pk)
        if curr_class == None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        print(data)
        mail = data["mail"]
        status = data["status"]

        student = Student.objects.get(mail=mail)

        attendance = ClassAttendanceByBSM.create_with(
            student, curr_class, status, request.user
        )
        attendance.save()

        return Response(
            {
                "mail": mail,
                "status": attendance.class_attendance.get_attendance_status().name,
            }
        )

# Method 13
def getAttendance(request, pk):
    return redirect('GetAttendance')

class GetAttendance(APIView):
    def get(self, request, pk):
        cache_key = f"get_current_class_attendance_{pk}"
        if not request.user.is_staff:
            result = cache.get(cache_key)
            if result is not None:
                return Response(result)

        query_class = SubjectClass.objects.get(pk=pk)
        response = fetchLatestAttendances(query_class)

        if (not request.user.is_staff) or (cache.get(cache_key) != None):
            cache.set(cache_key, response, 60 * 5)
        return Response(response)
    
# Method 14
def getAttendanceView(request, pk):
    return redirect('GetAttendanceView')

class GetAttendanceView(APIView):
    def get(self, request, pk):
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
            {"markAttendanceURL": markAttendanceURL, "getAttendanceURL": getAttendanceURL, "noclass": noclass},
        )
    
# Method 15
def studentAttendance(request, mail_prefix):
    return redirect('StudentAttendance')

class StudentAttendance(APIView):
    def get(self, request, mail_prefix):
        student = Student.objects.get(mail=mail_prefix + "@sst.scaler.com")
        response = fetchAllStudentAttendances(student)
        for a in response['all_attendance']:
            if not a['status']:
               a['status'] = AttendanceStatus.Absent.name 
        return Response(response)
    
# Method 16
def fetchAllStudentAttendances(request, student):
    if not student:
        return Response(None)

    all_attendance = student.get_all_attendance()

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

    all_subjects = SubjectClass.get_all_classes()

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
    return Response(response)

# Method 17

def sendNotification(request, pk):
    if not request.user.is_superuser:
        return Response({"message": "Forbidden"}, status=400)
    student = Student.objects.get(pk = pk)
    if not student.fcmtoken:
        return Response({"message": "not send"}, status=400)
    pushNotification([student.fcmtoken], title, description)

    return Response({"message": "sent"})

# Method 18
def sendReminderForClass(request, pk):
    if not request.user.is_superuser:
        return Response({"message": "Forbidden"}, status=400)
     
    subject = SubjectClass.objects.get(pk = pk)
    student_status = subject.get_all_students_attendance_status()
    students = [student for student, status in student_status if status == AttendanceStatus.Absent]
    students = [student for student in students if student.fcmtoken] 
    fcmtokens = [student.fcmtoken for student in students]

    admin = Student.objects.get(mail = 'diwakar.gupta@scaler.com')
    if admin.fcmtoken:
        fcmtokens.append(admin.fcmtoken)
    pushNotification(fcmtokens, title, description)
    
    return Response({"message": f"Sent to {len(fcmtokens)} students", "sent_to": [
        s.name for s in students
    ]})

# Method 19
@api_view(['POST'])
def getTodaysClass(request):
    data = json.loads(request.body)
    token = data["token"]

    today_classes = SubjectClass.get_classes_for()
    student = Student.get_object_with_token(token)

    response = []

    for curr_class in today_classes:
        details = {}
        ioclass.is_in_attendance_window()

        attendance_status = ClassAttendance.get_attendance_status_for(student, curr_class).name
        details["attendance_status"] = attendance_status
        
        response.append(details)

    return Response(response)

# Method 20
@api_view(['POST'])
def get_aggregated_attendance(request):
    data = json.loads(request.body)
    token = data["token"]

    student = Student.get_object_with_token(token)
    response = Student.get_aggregated_attendance(student=student, include_optional=False)

    return Response(response)
