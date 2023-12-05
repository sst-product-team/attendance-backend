from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from django.urls import reverse


def home(request):
    if not request.user.is_staff:
        return JsonResponse(
            {
                "message": "You are not authorized to access this page",
                "status": "error",
            },
            status=403,
        )

    clear_get_current_class_url = reverse("clear_get_current_class")
    clear_get_current_class_attendance = reverse("clear_get_current_class_attendance")
    clear_get_todays_classs = reverse("clear_get_todays_classs")

    data_to_render = [
        {"name": "clear_get_current_class_url", "url": clear_get_current_class_url},
        {"name": "clear_get_current_class_attendance", "url": clear_get_current_class_attendance},
        {"name": "clear_get_todays_classs", "url": clear_get_todays_classs},
    ]
    return render(request,"cache.html",{"data_to_render": data_to_render})


def clear_get_current_class(request):
    if not request.user.is_staff:
        return JsonResponse(
            {
                "message": "You are not authorized to access this page",
                "status": "error",
            },
            status=403,
        )

    cache.delete("get_current_class")
    return JsonResponse({"message": "Removed"})


def get_current_class_attendance(request):
    if not request.user.is_staff:
        return JsonResponse(
            {
                "message": "You are not authorized to access this page",
                "status": "error",
            },
            status=403,
        )

    cache.delete("get_current_class_attendance")
    return JsonResponse({"message": "Removed"})

def get_todays_classs(request):
    if not request.user.is_staff:
        return JsonResponse(
            {
                "message": "You are not authorized to access this page",
                "status": "error",
            },
            status=403,
        )

    cache.delete("get_todays_classs")
    return JsonResponse({"message": "Removed"})