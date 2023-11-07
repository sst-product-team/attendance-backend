from django.contrib import admin
from attendance.models import Student, SubjectClass, ClassAttendance, GeoLocation

# Register your models here.

admin.site.register(Student)
admin.site.register(SubjectClass)
admin.site.register(ClassAttendance)
admin.site.register(GeoLocation)
