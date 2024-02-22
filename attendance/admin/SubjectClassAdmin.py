from django.contrib import admin
from django.urls import reverse
from attendance.models import SubjectClass
from django import forms
from django.urls import path
from django.shortcuts import redirect


class ButtonWidget(forms.Widget):
    template_name = "your_button_widget.html"


class SubjectClassAdminForm(forms.ModelForm):
    your_button = forms.CharField(label="Your Button", widget=ButtonWidget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["your_button"].widget.attrs["onclick"] = "handleButtonClick()"

    def save(self, commit=True):
        # Handle button click actions here
        super().save(commit)


class SubjectClassAdmin(admin.ModelAdmin):
    form = SubjectClassAdminForm
    list_display = (
        "__str__",
        "subject",
        "is_attendance_mandatory",
        "injest_to_scaler",
        "mark_attendance",
        "send_reminder",
    )
    list_filter = (
        "subject",
        "is_attendance_mandatory",
    )
    ordering = ["-class_start_time"]
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "your-button-action/<int:id>/",
                self.your_button_action,
                name="your_button_action",
            ),
        ]
        return custom_urls + urls

    def your_button_action(self, request, id):
        obj = SubjectClass.objects.get(id=id)
        # ... perform actions on obj ...
        print(obj)
        return redirect("..")


admin.site.register(SubjectClass, SubjectClassAdmin)
