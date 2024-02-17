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
    ProblemSolvingPercentage,
)
from django.utils.html import format_html


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
    readonly_fields = [
        "date_updated",
        "class_attendance",
        "status",
        "lat",
        "lon",
        "accuracy",
        "verified_by",
    ]


class ClassAttendanceByBSMInlineAdmin(admin.StackedInline):
    readonly_fields = [
        "date_updated",
        "marked_by",
        "class_attendance",
        "status",
        "change_attendance",
    ]
    model = ClassAttendanceByBSM

    def change_attendance(self, obj):
        url = reverse("getAttendanceView", args=[obj.class_attendance.subject.pk])
        return format_html(
            """<a class="button" href='%s'>update attendance</a>""" % url
        )


class ClassAttendanceWithGeoLocationInlineAdmin(admin.StackedInline):
    readonly_fields = [
        "date_updated",
        "class_attendance",
        "status",
        "lat",
        "lon",
        "accuracy",
        "verified_by",
    ]
    model = ClassAttendanceWithGeoLocation


class ClassAttendanceAdmin(admin.ModelAdmin):
    inlines = [
        ClassAttendanceByBSMInlineAdmin,
        ClassAttendanceWithGeoLocationInlineAdmin,
    ]
    list_display = ("__str__", "attendance_status", "is_injested")
    list_filter = ("subject", "attendance_status", "student")
    autocomplete_fields = ["student"]
    readonly_fields = [
        "date_updated",
        "is_injested",
        "student",
        "subject",
        "attendance_status",
        "change_attendance",
    ]

    def change_attendance(self, obj):
        url = reverse("getAttendanceView", args=[obj.subject.pk])
        return format_html(
            """<a class="button" href='%s'>update attendance</a>""" % url
        )


class FalseAttemptAdmin(admin.ModelAdmin):
    list_display = ("__str__", "verify")
    list_filter = ("subject", "student")  # Add the fields you want to use as filters

    def verify(self, obj):
        return format_html(
            '<a class="button" target="_blank" href="{}">Verify</a>',
            reverse("verify_false_attempt", args=[obj.pk]),
        )


class ClassAttendanceByBSMAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "status",
        "marked_by",
    )  # Add the fields you want to use as filters
    list_filter = (
        "status",
        "class_attendance__subject",
        "class_attendance__student",
    )  # Add the fields you want to use as filters
    readonly_fields = ["date_updated", "marked_by", "class_attendance", "status"]


class ProblemSolvingPercentageAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "subject",
        "percentage",
        "solved_questions",
        "total_questions",
    )

    def percentage(self, obj):
        if obj.total_questions == 0:
            return 0
        return int((obj.solved_questions / obj.total_questions) * 100)


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
            "disabled" if not obj.fcmtoken else "",
            reverse("sendNotification", args=[obj.pk]),
        )

    send_notification.short_description = "Send Reminder"


class SubjectClassAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "subject",
        "is_attendance_mandatory",
        "mark_attendance",
    )
    list_filter = (
        "subject",
        "is_attendance_mandatory",
    )
    ordering = ["-class_start_time"]
    save_as = True
    search_fields = ["name"]

    readonly_fields = ["mark_attendance", "send_reminder", "injest_to_scaler"]

    def mark_attendance(self, obj):
        from django.utils.html import format_html

        if obj.pk:
            return format_html(
                '<a class="button" target="_blank" href="{}">Mark Attendance</a>',
                reverse("getAttendanceView", args=[obj.pk]),
            )
        else:
            return format_html(
                '<a class="button" target="_blank" disabled>Mark Attendance</a>'
            )

    def injest_to_scaler(self, obj):
        from django.utils.html import format_html

        if obj.pk:
            return format_html(
                '<a class="button" target="_blank" href="{}">Injest to Scaler</a>',
                reverse("injest_to_scaler", args=[obj.pk]),
            )
        else:
            return format_html(
                '<a class="button" target="_blank" disabled>Injest to Scaler</a>',
            )

    def send_reminder(self, obj):
        from django.utils.html import format_html

        if obj.pk:
            return format_html(
                '<a class="button" target="_blank" href="{}">Remind Absenties</a>',
                reverse("sendReminderForClass", args=[obj.pk]),
            )
        else:
            return format_html(
                '<a class="button" target="_blank" disabled>Remind Absenties</a>'
            )

    def has_change_permission(self, request, obj=None):
        from django.utils import timezone

        current_time = timezone.now()

        if (
            obj is not None
            and obj.class_end_time < current_time
            and not request.user.is_superuser
        ):
            return False
        return super().has_change_permission(request, obj=obj)


admin.site.register(ProblemSolvingPercentage, ProblemSolvingPercentageAdmin)
admin.site.register(ClassAttendanceByBSM, ClassAttendanceByBSMAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(SubjectClass, SubjectClassAdmin)
admin.site.register(ClassAttendance, ClassAttendanceAdmin)
admin.site.register(GeoLocationDataContrib)
admin.site.register(ClassAttendanceWithGeoLocation, ClassAttendanceWithGeoLocationAdmin)
admin.site.register(FalseAttemptGeoLocation, FalseAttemptAdmin)
admin.site.register(ProjectConfiguration)
admin.site.register(Subject)
