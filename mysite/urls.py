"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import redirect, reverse


def replyPing(request):
    return JsonResponse({"message": "pong"})


def getAttendanceView(request):
    from attendance import views
    from attendance.models import SubjectClass

    curr_class = SubjectClass.get_current_class()
    if not curr_class:
        return views.getAttendanceView(request, curr_class.pk if curr_class else None)
    else:
        return redirect(reverse("getAttendanceView", args=[curr_class.pk]))


urlpatterns = [
    path("", getAttendanceView, name="index"),
    path("ping/", replyPing, name="ping"),
    path("attendance/", include("attendance.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
]
