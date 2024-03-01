from django.contrib import admin
from django.urls import reverse
from attendance.models import (
    Student,
    StudentGroup,
    StudentGroupItem,
    Subject,
    SubjectClass,
    ClassAttendance,
    ProjectConfiguration,
    GeoLocationDataContrib,
    ClassAttendanceWithGeoLocation,
    FalseAttemptGeoLocation,
    ClassAttendanceByBSM,
    ProblemSolvingPercentage,
    SubjectClassStudentGroups,
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


class SubjectClassStudentGroupsInline(admin.TabularInline):
    model = SubjectClassStudentGroups
    autocomplete_fields = ["student_group"]


class SubjectClassAdmin(admin.ModelAdmin):
    inlines = [SubjectClassStudentGroupsInline]
    list_display = (
        "__str__",
        "subject",
        "is_attendance_mandatory",
        "mark_attendance",
        "download_attendance_csv",
        "sync_with_gsheet",
    )
    list_filter = (
        "subject",
        "is_attendance_mandatory",
    )
    ordering = ["-class_start_time"]
    save_as = True
    search_fields = ["name"]

    readonly_fields = [
        "mark_attendance",
        "send_reminder",
        "injest_to_scaler",
        "sync_with_gsheet",
        "injest_to_backend",
    ]

    def sync_with_gsheet(self, obj):
        from django.utils.html import format_html

        if obj.pk:
            return format_html(
                '<a class="button" target="_blank" href="{}">Sync to gsheet</a>',
                reverse("sync_class_with_google_sheet_admin", args=[obj.pk]),
            )
        else:
            return format_html(
                '<a class="button" target="_blank" disabled>Sync to gsheet</a>'
            )

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

    def injest_to_backend(self, obj):
        from django.utils.html import format_html

        if obj.pk:
            return format_html(
                '<a class="button" target="_blank" href="{}">Injest to Backend</a>',
                reverse("injest_to_backend", args=[obj.pk]),
            )
        else:
            return format_html(
                '<a class="button" target="_blank" disabled>Injest to Backend</a>'
            )

    def download_attendance_csv(self, obj):
        from django.utils.html import format_html

        if obj.pk:
            return format_html(
                '<a class="button" target="_blank" href="{}">Download Csv</a>',
                reverse("downloadAttendance", args=[obj.pk]),
            )
        else:
            return format_html(
                '<a class="button" target="_blank" disabled>Download Csv</a>'
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


class StudentGroupItemInline(admin.TabularInline):
    model = StudentGroupItem
    autocomplete_fields = ["student"]


class StudentGroupAdmin(admin.ModelAdmin):
    inlines = [StudentGroupItemInline]
    search_fields = ["name"]


admin.site.register(StudentGroup, StudentGroupAdmin)
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
