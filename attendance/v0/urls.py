from django.urls import path
from .views import mark_attendance

urlpatterns = [
    path(
        "builk_mark_attendance/<int:pk>/",
        mark_attendance.BuldMarkAttendanceByBSMView.as_view(),
        name="builk_mark_attendance",
    ),
]
