from django.contrib import admin
from attendance.models import Student, SubjectClass, ClassAttendance, GeoLocation, ClassAttendanceWithGeoLocation, FalseAttempt

# Register your models here.

class ClassAttendanceWithGeoLocationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status',)
    list_filter = ('status', 'class_attendance__subject', 'class_attendance__student')  # Add the fields you want to use as filters
    list_editable = ('status',)


class ClassAttendanceAdmin(admin.ModelAdmin):
    # list_display = ('__str__',)
    list_filter = ('subject', 'student')  # Add the fields you want to use as filters


admin.site.register(Student)
admin.site.register(SubjectClass)
admin.site.register(ClassAttendance, ClassAttendanceAdmin)
admin.site.register(GeoLocation)
admin.site.register(ClassAttendanceWithGeoLocation, ClassAttendanceWithGeoLocationAdmin)
admin.site.register(FalseAttempt)
