from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=50)
    mail = models.EmailField(max_length=80, blank=False, null=False)
    token = models.CharField(max_length=100, blank=False, null=False)
    # mail = models.DateTimeField("date published")


class SubjectClass(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    @classmethod
    def get_current_class(cls):
        return SubjectClass.objects.filter()[:1].get()


class ClassAttendance(models.Model):
    creation_time = models.DateTimeField(auto_created=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(SubjectClass, on_delete=models.CASCADE)
    
