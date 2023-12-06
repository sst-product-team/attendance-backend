from django.contrib import admin
from django.urls import reverse
from attendance.models import (
    Student,
    Subject,
    SubjectClass,
    ClassAttendance,
    ProjectConfiguration,
    GeoLocationDataContrib,
    ClassAttendanceWithGeoLocation,
    FalseAttemptGeoLocation,
    ClassAttendanceByBSM,
)

# Register your models here.


class ClassAttendanceWithGeoLocationAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "status",
    )
    list_filter = (
        "status",
        "class_attendance__subject",
        "class_attendance__student",
    )  # Add the fields you want to use as filters
    list_editable = ("status",)


class ClassAttendanceAdmin(admin.ModelAdmin):
    # list_display = ('__str__',)
    list_filter = ("subject", "student")  # Add the fields you want to use as filters
    autocomplete_fields = ["student"]


class FalseAttemptAdmin(admin.ModelAdmin):
    list_filter = ("subject", "student")  # Add the fields you want to use as filters


class ClassAttendanceByBSMAdmin(admin.ModelAdmin):
    list_display = ("__str__", "status")  # Add the fields you want to use as filters
    list_filter = (
        "status",
        "class_attendance__subject",
        "class_attendance__student",
    )  # Add the fields you want to use as filters
    list_editable = ("status",)


class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "mail", "show_attendance", "send_notification")
    search_fields = ["name", "mail"]

    def show_attendance(self, obj):
        from django.utils.html import format_html

        return format_html(
            '<a class="button" target="_blank" href="{}">Show Attendance</a>',
            reverse("studentAttendance", args=[obj.mail.split("@")[0]]),
        )
    
    def send_notification(self, obj):
        from django.utils.html import format_html

        return format_html(
            '<a class="button" {} target="_blank" href="{}">Send Notification</a>',
            'disabled' if not obj.fcmtoken else '',
            reverse("sendNotification", args=[obj.pk]),
        )
    send_notification.short_description = "Send Reminder"


class SubjectClassAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "is_attendance_mandatory",
        "injest_to_scaler",
        "mark_attendance",
        "send_reminder"
    )
    save_as = True
    search_fields = ["name"]

    def mark_attendance(self, obj):
        from django.utils.html import format_html

        return format_html(
            '<a class="button" target="_blank" href="{}">Mark Attendance</a>',
            reverse("getAttendanceView", args=[obj.pk]),
        )

    def injest_to_scaler(self, obj):
        from django.utils.html import format_html

        return format_html(
            '<a class="button" target="_blank" href="{}">Injest to Scaler</a>',
            reverse("injest_to_scaler", args=[obj.pk]),
        )
    
    def send_reminder(self, obj):
        from django.utils.html import format_html

        return format_html(
            '<a class="button" target="_blank" href="{}">Remind Absenties</a>',
            reverse("sendReminderForClass", args=[obj.pk]),
        )


admin.site.register(ClassAttendanceByBSM, ClassAttendanceByBSMAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(SubjectClass, SubjectClassAdmin)
admin.site.register(ClassAttendance, ClassAttendanceAdmin)
admin.site.register(GeoLocationDataContrib)
admin.site.register(ClassAttendanceWithGeoLocation, ClassAttendanceWithGeoLocationAdmin)
admin.site.register(FalseAttemptGeoLocation, FalseAttemptAdmin)
admin.site.register(ProjectConfiguration)
admin.site.register(Subject)
