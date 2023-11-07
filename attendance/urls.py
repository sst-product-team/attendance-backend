from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("geo/", views.geo, name="register"),
    # path("getattendance/", views.getattendance, name="getattendance"),
    path("getcurclassattendance/", views.getcurclassattendance, name="getcurclassattendance"),
    path("get_all_attendance/", views.get_all_attendance, name="get_all_attendance"),
]