from django.urls import path, include

from . import views
from . import cache_clear

urlpatterns = [
    path("ping", views.ping, name="index"),
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("injest_to_scaler/<int:pk>/", views.injest_to_scaler, name="injest_to_scaler"),
    # path("geo/", views.geo, name="register"),
    path("getcurclassattendance/", views.getcurclassattendance, name="getcurclassattendance"),
    path("get_all_attendance/", views.get_all_attendance, name="get_all_attendance"),
    path("cache/", include([
        path("", cache_clear.home, name="cache_home_page"),
        path("clear_get_current_class", cache_clear.clear_get_current_class, name='clear_get_current_class'),
        path("get_current_class_attendance", cache_clear.get_current_class_attendance, name='clear_get_current_class_attendance'),
    ])),
    path('get_current_class_attendance/', views.get_current_class_attendance, name='get_current_class_attendance'),
    path('can_mark_attendance/', views.can_mark_attendance, name='can_mark_attendance'),
]