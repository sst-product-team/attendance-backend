from django.contrib import admin
from django.urls import reverse
from attendance.models import Student, SubjectClass, ClassAttendance, ProjectConfiguration, GeoLocationDataContrib, ClassAttendanceWithGeoLocation, FalseAttemptGeoLocation, ClassAttendanceByBSM

# Register your models here.

class ClassAttendanceWithGeoLocationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status',)
    list_filter = ('status', 'class_attendance__subject', 'class_attendance__student')  # Add the fields you want to use as filters
    list_editable = ('status',)


class ClassAttendanceAdmin(admin.ModelAdmin):
    # list_display = ('__str__',)
    list_filter = ('subject', 'student')  # Add the fields you want to use as filters


class FalseAttemptAdmin(admin.ModelAdmin):
    list_filter = ('subject', 'student')  # Add the fields you want to use as filters

class ClassAttendanceByBSMAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status')  # Add the fields you want to use as filters
    list_filter = ('status', 'class_attendance__subject', 'class_attendance__student')  # Add the fields you want to use as filters
    list_editable = ('status',)


class SubjectClassAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_attendance_mandatory', 'custom_action_button', 'mark_attendance')


    def mark_attendance(self, obj):
        from django.utils.html import format_html
        return format_html('<a class="button" target="_blank" href="{}">Mark Attendance</a>', reverse('getAttendanceView', args=[obj.pk]))

    def custom_action_button(self, obj):
        from django.utils.html import format_html
        return format_html('<a class="button" target="_blank" href="{}">Injest to Scaler</a>', reverse('injest_to_scaler', args=[obj.pk]))

    
admin.site.register(ClassAttendanceByBSM, ClassAttendanceByBSMAdmin)
admin.site.register(Student)
admin.site.register(SubjectClass, SubjectClassAdmin)
admin.site.register(ClassAttendance, ClassAttendanceAdmin)
admin.site.register(GeoLocationDataContrib)
admin.site.register(ClassAttendanceWithGeoLocation, ClassAttendanceWithGeoLocationAdmin)
admin.site.register(FalseAttemptGeoLocation, FalseAttemptAdmin)
admin.site.register(ProjectConfiguration)
