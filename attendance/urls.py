from django.urls import path, include

from . import views
from . import cache_clear
from .v0 import views as v0_view, urls as v0_urls

urlpatterns = [
    path("v0/", include(v0_urls.urlpatterns)),
    path("ping", views.ping, name="index"),
    path("", views.index, name="index"),
    path("student_psp/<str:mail_prefix>/", views.psp, name="getPsp"),
    path("version", views.version, name="index"),
    path("register/", views.register, name="register"),
    path("injest_to_scaler/<int:pk>/", views.injest_to_scaler, name="injest_to_scaler"),
    path("student_group/", v0_view.StudentGroupView.as_view(), name = "student_group"),
    path(
        "injest_to_backend/<int:pk>/",
        v0_view.mark_attendance.BulkMarkAttendanceByBSMView.as_view(),
        name="injest_to_backend",
    ),
    # path("geo/", views.geo, name="register"),
    path(
        "getcurclassattendance/",
        views.getcurclassattendance,
        name="getcurclassattendance",
    ),
    path("getTodaysClass/", views.getTodaysClass, name="getTodaysClass"),
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
    path(
        "mark_attendance/<int:pk>/",
        views.mark_attendance_subject,
        name="mark_attendance_subject",
    ),
    path("getAttendance/<int:pk>/", views.getAttendance, name="getAttendance"),
    path(
        "getAttendance/<int:pk>/download/",
        views.download_attendance_csv_for_subject_class,
        name="downloadAttendance",
    ),
    path(
        "getAttendanceView/<int:pk>/", views.getAttendanceView, name="getAttendanceView"
    ),
    path(
        "studentAttendance/<str:mail_prefix>/",
        views.studentAttendance,
        name="studentAttendance",
    ),
    path("sendNotification/<int:pk>/", views.sendNotification, name="sendNotification"),
    path(
        "sendReminderForClass/<int:pk>/",
        views.sendReminderForClass,
        name="sendReminderForClass",
    ),
    path(
        "get_aggregated_attendance/",
        views.get_aggregated_attendance,
        name="get_aggregated_attendance",
    ),
    path(
        "falseattempt/<int:pk>/verify/",
        views.verify_false_attempt,
        name="verify_false_attempt",
    ),
    path(
        "sync_class_with_google_drive/<int:pk>/",
        views.sync_class_with_google_sheet_admin,
        name="sync_class_with_google_sheet_admin",
    ),
    path(
        "cron/",
        include(
            [
                path(
                    "sync_todays_class_with_google_drive/<str:cron_token>/",
                    views.sync_todays_class_with_google_drive,
                    name="sync_todays_class_with_google_drive",
                ),
            ]
        ),
    ),
]
