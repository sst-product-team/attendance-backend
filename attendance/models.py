from django.core.cache import cache
from django.db import models
from django.db.models import Min
from django.db.models import F
from django.utils import timezone
from enum import Enum


def round_coordinates(num):
    return round(num, 10)


class AttendanceStatus(Enum):
    Present = 1
    Proxy = 2
    Absent = 3


# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=50)
    mail = models.EmailField(max_length=80, blank=False, null=False, unique=True)
    token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    def get_id_number(self):
        if self.mail.endswith('@scaler.com'):
            return None
        return self.mail.split('.')[1].split('@')[0]

    def __str__(self):
        return self.mail

    @classmethod
    def get_object_with_token(cls, token):
        return Student.objects.get(token=token)
    
    @classmethod
    def get_all_students(cls):
        return Student.objects.filter(mail__endswith='@sst.scaler.com')


class SubjectClass(models.Model):
    name = models.CharField(max_length=50)
    attendance_start_time = models.DateTimeField()
    attendance_end_time = models.DateTimeField(blank=True, null=True)
    class_start_time = models.DateTimeField(db_index=True)
    class_end_time = models.DateTimeField()


    def __str__(self):
        return f"{self.class_start_time.astimezone().strftime('%d/%m/%Y')} => {self.name}"

    @classmethod
    def get_current_class(cls):
        cache_key = 'get_current_class'
        result = cache.get(cache_key)

        if result is not None:
            return result

        current_time = timezone.now()
        filtered_subject_class = SubjectClass.objects.filter(class_start_time__lte=current_time, class_end_time__gte=current_time).first()
        
        if filtered_subject_class:
            result = filtered_subject_class
        else:
            nearest_next_class = SubjectClass.objects.filter(class_start_time__gt=current_time).order_by('class_start_time').first()
            if nearest_next_class:
                result = nearest_next_class
            else:
                result = None
        
        cache.set(cache_key, result, 60 * 5)
        return result

    
    def is_in_attendance_window(self):
        current_time = timezone.now()
        return self.attendance_start_time <= current_time <= (self.attendance_end_time if self.attendance_end_time else self.class_end_time)

    def get_all_attendance(self):
        all_students = ClassAttendance.objects.filter(subject=self).select_related('student').all()
        return all_students

class ClassAttendance(models.Model):
    creation_time = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_index=True)
    subject = models.ForeignKey(SubjectClass, on_delete=models.CASCADE, db_index=True)

    class Meta:
        # Make the combination of student and subject unique
        unique_together = ('student', 'subject')

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

    def get_attendance_by_bsm_status(self):
        marked_by_bsm = ClassAttendanceByBSM.objects.filter(class_attendance=self).first()
        if marked_by_bsm == None:
            return None
        return marked_by_bsm.get_attendance_status()
    
    def get_attendance_with_geo_location_status(self):
        with_geo_location = ClassAttendanceWithGeoLocation.objects.filter(class_attendance=self).first()
        if with_geo_location == None:
            return None
        return with_geo_location.get_attendance_status()
    
    def get_attendance_status(self):

        by_bsm = self.get_attendance_by_bsm_status()
        if by_bsm != None:
            return by_bsm
        else:
            with_geo_location = self.get_attendance_with_geo_location_status()
            if with_geo_location != None:
                return with_geo_location
            else:
                return AttendanceStatus.Absent


class ClassAttendanceWithGeoLocation(models.Model):
    STATUS_CHOICES = [
        ('proxy', 'Proxy'),
        ('verified', 'Verified'),
        ('standby', 'Standby'),
        ('flaggers', 'Flaggers'),
    ]

    lat = models.DecimalField(max_digits=13,decimal_places=10)
    lon = models.DecimalField(max_digits=13,decimal_places=10)
    accuracy = models.DecimalField(max_digits=13,decimal_places=10)
    class_attendance = models.OneToOneField(ClassAttendance, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='standby',  # Set the default value if needed
        db_index=True
    )

    def get_attendance_status(self):

        status_mapping = {
            'verified': AttendanceStatus.Present,
            'standby': AttendanceStatus.Present,
            'proxy': AttendanceStatus.Proxy,
        }
        return status_mapping.get(self.status)

    def save(self, *args, **kwargs):
        self.lat = round_coordinates(self.lat)
        self.lon = round_coordinates(self.lon)
        self.accuracy = round_coordinates(self.accuracy)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.class_attendance)

    @classmethod
    def create_with(cls, student, subject, lat, lon, accuracy):
        class_attendance, is_created = ClassAttendance.objects.get_or_create(student=student, subject=subject)
        
        attendance = ClassAttendanceWithGeoLocation.objects.create(lat=lat, lon=lon, class_attendance=class_attendance, accuracy=accuracy)
        attendance.save()
        return attendance


class ClassAttendanceByBSM(models.Model):
    STATUS_CHOICES = [
        ('proxy', 'Proxy'),
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]
    marked_by = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_attendance = models.OneToOneField(ClassAttendance, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='present'
    )

    def __str__(self):
        return f"{self.class_attendance.student.name} {self.class_attendance.subject.name}"

    def get_attendance_status(self):
        
        status_mapping = {
            'present': AttendanceStatus.Present,
            'proxy': AttendanceStatus.Proxy,
            'absent': AttendanceStatus.Absent,
        }
        return status_mapping.get(self.status)
    
    @classmethod
    def create_with(cls, student, subject, status, marked_by):
        class_attendance, _ = ClassAttendance.objects.get_or_create(student=student, subject=subject)
        
        attendance, _ = ClassAttendanceByBSM.objects.update_or_create(
            class_attendance=class_attendance,
            defaults={'marked_by':marked_by, 'status':status},
        )
        attendance.save()
        return attendance


class GeoLocationDataContrib(models.Model):
    label = models.SmallIntegerField(default=-2)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lat = models.DecimalField(max_digits=13,decimal_places=10)
    lon = models.DecimalField(max_digits=13,decimal_places=10)
    accuracy = models.DecimalField(max_digits=13,decimal_places=10)
    
    def save(self, *args, **kwargs):
        self.lat = round_coordinates(self.lat)
        self.lon = round_coordinates(self.lon)
        self.accuracy = round_coordinates(self.accuracy)
        
        super().save(*args, **kwargs)


class FalseAttemptGeoLocation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_index=True)
    lat = models.DecimalField(max_digits=13,decimal_places=10)
    lon = models.DecimalField(max_digits=13,decimal_places=10)
    accuracy = models.DecimalField(max_digits=13,decimal_places=10)
    creation_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    subject = models.ForeignKey(SubjectClass, on_delete=models.CASCADE, db_index=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.lat = round_coordinates(self.lat)
        self.lon = round_coordinates(self.lon)
        self.accuracy = round_coordinates(self.accuracy)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.student.mail)

