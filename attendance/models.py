from django.db import models
from django.db.models import Min
from django.db.models import F
from django.utils import timezone


def round_coordinates(num):
    X = 1e10
    return int(num*X)/X

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
        current_time = timezone.now()
        filtered_subject_class = SubjectClass.objects.filter(start_time__lte=current_time, end_time__gte=current_time).first()
        if filtered_subject_class:
            return filtered_subject_class
        else:
            return None
    
    def is_active(self):
        current_time = timezone.now()
        return self.start_time <= current_time <= (self.end_time if self.end_time else current_time)

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
    lat = models.DecimalField(max_digits=13,decimal_places=10)
    lon = models.DecimalField(max_digits=13,decimal_places=10)
    accuracy = models.DecimalField(max_digits=13,decimal_places=10)
    class_attendance = models.ForeignKey(ClassAttendance, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.lat = round_coordinates(self.lat)
        self.lon = round_coordinates(self.lon)
        self.accuracy = round_coordinates(self.accuracy)
        
        super().save(*args, **kwargs)


    @classmethod
    def create_with(cls, student, subject, lat, lon, accuracy):
        class_attendance = ClassAttendance.objects.create(student=student, subject=subject)
        class_attendance.save()
        attendance = ClassAttendanceWithGeoLocation.objects.create(lat=lat, lon=lon, class_attendance=class_attendance, accuracy=accuracy)
        attendance.save()
        return attendance

class GeoLocation(models.Model):
    label = models.SmallIntegerField(default=-2)
    token = models.CharField(max_length=100, blank=False, null=False)
    lat = models.DecimalField(max_digits=13,decimal_places=10)
    lon = models.DecimalField(max_digits=13,decimal_places=10)
    accuracy = models.DecimalField(max_digits=13,decimal_places=10)
    
    def save(self, *args, **kwargs):
        self.lat = round_coordinates(self.lat)
        self.lon = round_coordinates(self.lon)
        self.accuracy = round_coordinates(self.accuracy)
        
        super().save(*args, **kwargs)


class FalseAttempt(models.Model):
    token = models.CharField(max_length=100, blank=False, null=False)
    lat = models.DecimalField(max_digits=13,decimal_places=10)
    lon = models.DecimalField(max_digits=13,decimal_places=10)
    accuracy = models.DecimalField(max_digits=13,decimal_places=10)

    def save(self, *args, **kwargs):
        self.lat = round_coordinates(self.lat)
        self.lon = round_coordinates(self.lon)
        self.accuracy = round_coordinates(self.accuracy)
        
        super().save(*args, **kwargs)

