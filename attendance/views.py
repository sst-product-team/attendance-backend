from django.http import HttpResponse, JsonResponse
from attendance.models import SubjectClass, Student, ClassAttendance
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def index(request):
    data = json.loads(request.body)
    location = data["location"]
    token = data["token"]

    student = Student.objects.filter(token=token)[:1].get()
    curr_class = SubjectClass.get_current_class()

    print(f"Marked attendance of {student.name} for class {curr_class.name}")
    return JsonResponse(f"Marked attendance of {student.name} for class {curr_class.name}")

@csrf_exempt
def getattendance(request):
    data = json.loads(request.body)
    token = data['token']

    student = Student.objects.get(token = token)
    all_attendances = ClassAttendance.objects.filter(student=student)

    attendance_response = []

    for attendance in all_attendances:
        attendance_response.append({
            "mail": attendance.student.mail,
            "subject": attendance.subject.name,
            "classStartTime": attendance.subject.start_time
        })

    return JsonResponse(attendance_response, safe=False)

@csrf_exempt
def register(request):
    details = {}
    
    data = json.loads(request.body)

    details['mail'] = data["email"]
    if not details['mail'].endswith("@sst.scaler.com"):
        return JsonResponse({"message": "mail should end with @sst.scaler.com"}, status=400)
    
    details['token'] = data["uid"]

    print(details)

    user_object_query = Student.objects.filter(mail=details['mail'])
    if user_object_query.exists():
        user_obj = user_object_query[:1].get()
        if user_obj.token == details['token']:
            return JsonResponse({})
        else:
            return JsonResponse({"message": "if you are bad I am your dad"}, status=400)
    else:
        student = Student.objects.create(name="", mail=details['mail'], token=details['token'])
        student.save()

    return JsonResponse(details)