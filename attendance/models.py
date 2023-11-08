from django.db import models
from django.db.models import Min
from django.db.models import F

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=50)
    mail = models.EmailField(max_length=80, blank=False, null=False, unique=True)
    token = models.CharField(max_length=100, blank=False, null=False, unique=True)
    # mail = models.DateTimeField("date published")

    def __str__(self):
        return self.mail

    @classmethod
    def get_object_with_token(cls, token):
        return Student.objects.filter(token=token)[:1].get()


class SubjectClass(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.start_time}"

    @classmethod
    def get_current_class(cls):
        return SubjectClass.objects.filter().last()


class ClassAttendance(models.Model):
    creation_time = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(SubjectClass, on_delete=models.CASCADE)

    def __str__(self):
        return self.student.mail + " " + self.subject.name

    @classmethod
    def get_latest_attendance_time(cls, student, subject):
        obj = ClassAttendance.objects.filter(student=student, subject=subject).order_by("creation_time").first()
        if obj == None:
            return None
        else:
            return obj.creation_time

    @classmethod
    def all_subject_attendance(cls, student):
        from django.db.models import Min, OuterRef, Subquery
        min_creation_time_subquery = ClassAttendance.objects.filter(
            student=student,
            subject=OuterRef('pk')
        ).values('subject').annotate(min_creation_time=Min('creation_time')).values('min_creation_time')

        subject_classes_with_attendance = SubjectClass.objects.annotate(
            min_creation_time=Subquery(min_creation_time_subquery)
        ).values('name', 'start_time', 'end_time', 'min_creation_time')

        return subject_classes_with_attendance

    # @classmethod
    # def get_all_student_attendance(cls, student):
    #     return ClassAttendance.objects.filter(student=student).values("subject").annotate(min_creation_time=Min('creation_time')).all()

class ClassAttendanceWithGeoLocation(models.Model):
    lat = models.CharField(max_length=15)
    lon = models.CharField(max_length=15)

    class_attendance = models.ForeignKey(ClassAttendance, on_delete=models.CASCADE)

    @classmethod
    def create_with(cls, student, subject, lat, lon):
        class_attendance = ClassAttendance.objects.create(student=student, subject=subject)
        class_attendance.save()
        attendance = ClassAttendanceWithGeoLocation.objects.create(lat=lat, lon=lon, class_attendance=class_attendance)
        attendance.save()
        return attendance

class GeoLocation(models.Model):
    label = models.SmallIntegerField(default=-2)
    token = models.CharField(max_length=100, blank=False, null=False)
    lat = models.CharField(max_length=15)
    lon = models.CharField(max_length=15)
    accuracy = models.CharField(max_length=15, default="")
