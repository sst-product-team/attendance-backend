from django.urls import path
from .views.mark_attendance import MarkAttendanceByGeoView

urlpatterns = [
    path("mark/geo/", MarkAttendanceByGeoView.as_view(), name="mark-attendance-by-geo"),
]
