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

    return render(
        request,
        "cache.html",
        {
            "clear_get_current_class_url": clear_get_current_class_url,
            "clear_get_current_class_attendance": clear_get_current_class_attendance,
        },
    )


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
