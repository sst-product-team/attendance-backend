from django.http import HttpResponse, JsonResponse
from attendance.models import SubjectClass, Student, ClassAttendance, GeoLocation
from django.views.decorators.csrf import csrf_exempt
import json


AVG_LAT = 12.83849392
AVG_LON = 77.66468718

def is_in_class(lat, lon):
    # return True
    return abs(AVG_LAT - lat) < 0.0001 and abs(AVG_LON - lon) < 0.0001

def ping(request):
    return JsonResponse({"message": "pong"})

@csrf_exempt
def index(request):
    data = json.loads(request.body)
    lat = (data['latitutde'])
    lon = (data['longitude'])
    token = data["token"]

    if is_in_class(lat, lon):
        student = Student.objects.filter(token=token)[:1].get()
        curr_class = SubjectClass.get_current_class()

        if ClassAttendance.objects.filter(student = student, subject=curr_class).exists():
            print(f"Attendance already marked of {student.name} for class {curr_class.name}")
            return JsonResponse({
                "class": curr_class.name,
                "time": curr_class.start_time
            })

        print(f"Marked attendance of {student.name} for class {curr_class.name}")
        ClassAttendance.objects.create(student = student, subject=curr_class).save()
        return JsonResponse({
            "class": curr_class.name,
            "time": curr_class.start_time
        })
    else:
        return JsonResponse({
            "message": "You are outside the class range"
        }, status=400)

@csrf_exempt
def register(request):
    details = {}
    
    data = json.loads(request.body)

    details['mail'] = data["email"]
    if not (details['mail'].endswith("@sst.scaler.com") or details['mail'].endswith("@scaler.com")):
        return JsonResponse({"message": "mail should end with @sst.scaler.com"}, status=400)
    
    details['token'] = data["uid"]

    print(details)

    user_object_query = Student.objects.filter(mail=details['mail'])
    if user_object_query.exists():
        user_obj = user_object_query[:1].get()
        if user_obj.token == details['token']:
            return JsonResponse({})
        else:
            # TODO: add to database and report to bsm
            return JsonResponse({"message": "if you are bad I am your dad"}, status=400)
    else:
        student = Student.objects.create(name="", mail=details['mail'], token=details['token'])
        student.save()

    return JsonResponse(details)


@csrf_exempt
def geo(request):
    # check if request.body.token
    print(request.body)
    data = json.loads(request.body)
    token = data['uid']
    lat = str(data['latitutde'])
    lon = str(data['longitude'])

    obj = GeoLocation.objects.create(token = token, lat=lat, lon=lon)
    obj.save()
    return JsonResponse({})


@csrf_exempt
def get_all_attendance(request):
    data = json.loads(request.body)
    token = data['token']

    student = Student.get_object_with_token(token)
    all_attendances_obj = ClassAttendance.all_subject_attendance(student)

    all_attendances = []
    for subject_class in all_attendances_obj:
        details = {}
        details["name"] = subject_class['name']
        details["start_time"] = subject_class['start_time']
        details["end_time"] = subject_class['end_time']
        details["present_time"] = subject_class['min_creation_time']
        # print(f"Subject: {name}, Start Time: {start_time}, End Time: {end_time}, Min Creation Time: {min_creation_time}")
        all_attendances.append(details)

    return JsonResponse(all_attendances, safe=False)


@csrf_exempt
def getcurclassattendance(request):
    data = json.loads(request.body)
    token = data['token']

    curr_class = SubjectClass.get_current_class()
    if curr_class == None:
        return JsonResponse({}, status=404)
    
    details = {}
    details["name"] = curr_class.name
    details["start_time"] = curr_class.start_time
    details["end_time"] = curr_class.end_time

    student = Student.get_object_with_token(token)
    time = ClassAttendance.get_latest_attendance_time(student, curr_class)

    details["present_time"] = time

    return JsonResponse(details)