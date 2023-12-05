from django.urls import path, include

from . import views
from . import cache_clear

urlpatterns = [
    path("ping", views.ping, name="index"),
    path("", views.index, name="index"),
    path("version", views.version, name="index"),
    path("register/", views.register, name="register"),
    path("injest_to_scaler/<int:pk>/", views.injest_to_scaler, name="injest_to_scaler"),
    # path("geo/", views.geo, name="register"),
    path(
        "getcurclassattendance/",
        views.getcurclassattendance,
        name="getcurclassattendance",
    ),
    path("getTodaysClass/", views.getTodaysClass, name="getTodaysClass"),
    path("get_all_attendance/", views.get_all_attendance, name="get_all_attendance"),
    path(
        "cache/",
        include(
            [
                path("", cache_clear.home, name="cache_home_page"),
                path(
                    "clear_get_current_class",
                    cache_clear.clear_get_current_class,
                    name="clear_get_current_class",
                ),
                path(
                    "clear_get_current_class_attendance",
                    cache_clear.get_current_class_attendance,
                    name="clear_get_current_class_attendance",
                ),
                path(
                    "clear_get_todays_classs",
                    cache_clear.get_todays_classs,
                    name="clear_get_todays_classs",
                ),
            ]
        ),
    ),
    path("can_mark_attendance/", views.can_mark_attendance, name="can_mark_attendance"),
    path("mark_attendance/", views.mark_attendance, name="mark_attendance"),
    path(
        "mark_attendance/<int:pk>/",
        views.mark_attendance_subject,
        name="mark_attendance_subject",
    ),
    path(
        "getAttendance/",
        views.get_current_class_attendance,
        name="get_current_class_attendance",
    ),
    path("getAttendance/<int:pk>/", views.getAttendance, name="getAttendance"),
    path(
        "getAttendanceView/<int:pk>/", views.getAttendanceView, name="getAttendanceView"
    ),
    path(
        "studentAttendance/<str:mail_prefix>/",
        views.studentAttendance,
        name="studentAttendance",
    ),
    path("sendNotification/<int:pk>/", views.sendNotification, name="sendNotification"),
    path("sendReminderForClass/<int:pk>/", views.sendReminderForClass, name="sendReminderForClass"),
]
