from django.core.cache import cache
from django.db import models
from django.db.models import Count, F, Q, Min, Prefetch, OuterRef, Subquery
from django.utils import timezone
from enum import Enum
from django.contrib.auth.models import User
from enumfields import EnumField


def round_coordinates(num):
    return round(num, 10)


class AttendanceStatus(Enum):
    Present = 1
    Proxy = 2
    Absent = 3

    @classmethod
    def get_all_status(cls):
        return [x.name for x in list(cls)]


# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=50)
    mail = models.EmailField(
        max_length=80, blank=False, null=False, unique=True, db_index=True
    )
    personal_mail = models.EmailField(
        max_length=80, blank=True, null=True, unique=True, db_index=True
    )
    token = models.CharField(
        max_length=100, blank=True, null=True, unique=True, db_index=True
    )
    user = models.ForeignKey(
        User, default=None, null=True, blank=True, on_delete=models.SET_NULL
    )
    fcmtoken = models.CharField(max_length=255, blank=True, null=True)

    @classmethod
    def can_mark_attendance(cls, request):
        return request.user.has_perm("attendance.can_mark_attendance")

    @classmethod
    def can_send_notifications(cls, request):
        return request.user.has_perm("attendance.can_send_notifications")

    @classmethod
    def can_verify_false_attempt(cls, request):
        return request.user.has_perm("attendance.verify_false_attempt")

    @classmethod
    def can_sync_to_gsheet(cls, request):
        return request.user.has_perm("attendance.can_sync_to_gsheet")

    @classmethod
    def can_injest_to_scaler(cls, request):
        return request.user.has_perm("attendance.can_injest_to_scaler")

    def get_id_number(self):
        if self.mail.endswith("@scaler.com"):
            return None
        return self.mail.split(".")[1].split("@")[0]

    def __str__(self):
        return self.mail

    @classmethod
    def get_object_with_token(cls, token):
        return Student.objects.get(token=token)

    @classmethod
    def get_object_with_mail(cls, mail):
        return cls.objects.filter(Q(mail=mail) | Q(personal_mail=mail)).first()

    @classmethod
    def get_all_students(cls):
        return Student.objects.filter(mail__endswith="@sst.scaler.com")

    def save(self, *args, **kwargs):
        self.mail = self.mail.lower()

        super().save(*args, **kwargs)

    def create_django_user(self):
        user = User.objects.create_user(
            username=self.mail, email=self.mail, password=None
        )
        user.set_unusable_password()
        user.save()
        return user

    def get_all_attendance(self, include_optional=False):
        if include_optional:
            return ClassAttendance.objects.filter(student=self)
        else:
            return ClassAttendance.objects.filter(
                student=self, subject__is_attendance_mandatory=True
            )

    @classmethod
    def get_aggregated_attendance(
        cls, attendances=None, student=None, include_optional=False
    ):
        if student and not attendances:
            # If only the student is provided, fetch all attendances for the student
            attendances = student.get_all_attendance(include_optional)
        elif not include_optional:
            attendances = attendances.filter(subject__is_attendance_mandatory=True)

        if include_optional:
            subject_all_classe = (
                SubjectClass.objects.all()
                .annotate(course=F("subject__name"))
                .values("subject__name")
                .annotate(count=Count("id"))
            )
        else:
            subject_all_classe = (
                SubjectClass.objects.filter(is_attendance_mandatory=True)
                .annotate(course=F("subject__name"))
                .values("subject__name")
                .annotate(count=Count("id"))
            )

        # Annotate each attendance with status_by_bsm and status_by_geo
        annotated_attendances = attendances.annotate(
            subject_name=F("subject__subject__name"),
            status_by_bsm=F("classattendancebybsm__status"),
            status_by_geo=F("classattendancewithgeolocation__status"),
        )

        # Use Case and When to count occurrences of each status combination
        aggregated_data = annotated_attendances.values(
            "subject_name", "status_by_bsm", "status_by_geo"
        ).annotate(count=Count("id"))

        # Create the final aggregated result
        result = {}
        uncategorised = "uncategorised"
        for item in aggregated_data:
            subject_name, status_by_geo, status_by_bsm = (
                item["subject_name"],
                item["status_by_geo"],
                item["status_by_bsm"],
            )
            if not subject_name:
                subject_name = uncategorised
            status_by_geo = ClassAttendanceWithGeoLocation.status_mapping.get(
                status_by_geo
            )
            status_by_bsm = ClassAttendanceByBSM.status_mapping.get(status_by_bsm)
            status = ClassAttendance.get_attendance_status_by_status(
                status_by_bsm, status_by_geo
            ).name

            if subject_name not in result:
                result[subject_name] = {}

            if status not in result[subject_name]:
                result[subject_name][status] = 0
            result[subject_name][status] += item["count"]

        for item in subject_all_classe:
            # print(item)
            name, count = item["subject__name"], item["count"]
            if not name:
                name = uncategorised
            if name not in result:
                result[name] = {}
            result[name]["totalClassCount"] = count

        for key in result:
            obj = result[key]
            total = obj["totalClassCount"]
            for sub in obj:
                if sub != "totalClassCount":
                    total -= obj[sub]
            if AttendanceStatus.Absent.name not in obj:
                obj[AttendanceStatus.Absent.name] = 0
            obj[AttendanceStatus.Absent.name] += total

        return result


class StudentGroup(models.Model):
    name = models.CharField(max_length=50)
    students = models.ManyToManyField(Student, through="StudentGroupItem")

    def __str__(self):
        return self.name


class StudentGroupItem(models.Model):
    student_group = models.ForeignKey(
        StudentGroup, on_delete=models.CASCADE, db_index=True
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_index=True)
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "student_group")


class Subject(models.Model):
    name = models.CharField(max_length=50)
    instructor_name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class SubjectClass(models.Model):
    scaler_class_url = models.URLField(max_length=400, blank=True)
    class_topic_slug = models.CharField(max_length=300, blank=True)
    super_batch_id = models.PositiveIntegerField(blank=True, null=True)
    name = models.CharField(max_length=50)
    attendance_start_time = models.DateTimeField()
    attendance_end_time = models.DateTimeField(blank=True, null=True)
    class_start_time = models.DateTimeField(db_index=True)
    class_end_time = models.DateTimeField()
    is_attendance_mandatory = models.BooleanField(default=True)
    subject = models.ForeignKey(
        Subject, default=None, null=True, blank=True, on_delete=models.CASCADE
    )
    is_attendance_by_geo_location_enabled = models.BooleanField(default=True)
    merge_attendace_with_class = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.SET_DEFAULT, default=None
    )

    def __str__(self):
        return (
            f"{self.class_start_time.astimezone().strftime('%d/%m/%Y')} => {self.name}"
        )

    def save(self, *args, **kwargs):
        if self.scaler_class_url:
            self.parse_slug_super_batch()
        super().save(*args, **kwargs)

    def can_injest(self):
        return self.super_batch_id and self.class_topic_slug

    def get_all_students_group(self):
        return SubjectClassStudentGroups.objects.filter(subject_class=self)

    def get_students_with_prioritized_attendance_policy(self):
        subject_class_instance = self

        subject_class_student_groups = (
            subject_class_instance.subjectclassstudentgroups_set.all().values(
                "student_group_id", "attendance_policy"
            )
        )

        # Subquery to get the minimum attendance policy for each student group
        min_attendance_policy_subquery = subject_class_student_groups.annotate(
            min_policy=Subquery(
                SubjectClassStudentGroups.objects.filter(
                    student_group_id=OuterRef("student_group_id")
                )
                .order_by("attendance_policy")
                .values("attendance_policy")[:1]
            )
        ).values("student_group_id", "min_policy")

        students = Student.objects.filter(
            studentgroupitem__student_group__in=subject_class_student_groups.values_list(  # noqa: E501
                "student_group_id", flat=True
            )
        ).annotate(
            prioritized_attendance_policy=Min(
                Subquery(
                    min_attendance_policy_subquery.filter(
                        student_group_id=OuterRef("studentgroupitem__student_group_id")
                    ).values("min_policy")
                )
            )
        )

        return students

    def get_all_students(self):
        subject_class_instance = self

        subject_class_student_groups = (
            subject_class_instance.subjectclassstudentgroups_set.all().values(
                "student_group_id", "attendance_policy"
            )
        )

        # Subquery to get the minimum attendance policy for each student group
        min_attendance_policy_subquery = subject_class_student_groups.annotate(
            min_policy=Subquery(
                SubjectClassStudentGroups.objects.filter(
                    student_group_id=OuterRef("student_group_id")
                )
                .order_by("attendance_policy")
                .values("attendance_policy")[:1]
            )
        ).values("student_group_id", "min_policy")

        students = (
            Student.objects.filter(
                studentgroupitem__student_group__in=subject_class_student_groups.values_list(  # noqa: E501
                    "student_group_id", flat=True
                )
            )
            .annotate(
                prioritized_attendance_policy=Subquery(
                    min_attendance_policy_subquery.filter(
                        student_group_id=OuterRef("studentgroupitem__student_group_id")
                    ).values("min_policy")[:1]
                )
            )
            .distinct()
        )
        return students

    def parse_slug_super_batch(self):
        if not self.scaler_class_url:
            return

        self.super_batch_id = int(self.scaler_class_url.split("/")[5])
        self.class_topic_slug = self.scaler_class_url.split("/")[7]

    def get_all_students_attendance_status(self):
        allClassAttendance = self.get_all_attendance()

        json_attendance = []
        mail_set = set()
        for attendance in allClassAttendance:
            json_attendance.append((attendance.student, attendance.attendance_status))
            mail_set.add(attendance.student.mail)

        all_students = Student.get_all_students()

        for student in all_students:
            if student.mail not in mail_set:
                json_attendance.append((student, AttendanceStatus.Absent))

        return json_attendance

    @classmethod
    def get_current_class(cls):
        cache_key = "get_current_class"
        result = cache.get(cache_key)

        if result is not None:
            return result

        current_time = timezone.now()
        filtered_subject_class = SubjectClass.objects.filter(
            class_start_time__lte=current_time, class_end_time__gte=current_time
        ).first()

        if filtered_subject_class:
            result = filtered_subject_class
        else:
            nearest_next_class = (
                SubjectClass.objects.filter(class_start_time__gt=current_time)
                .order_by("class_start_time")
                .first()
            )
            if nearest_next_class:
                result = nearest_next_class
            else:
                result = None

        cache.set(cache_key, result, 60 * 5)
        return result

    @classmethod
    def get_classes_for(
        cls, start=timezone.now().astimezone().date(), next_x_days=1, use_cache=True
    ):
        cache_key = "get_todays_classs"

        if use_cache:
            result = cache.get(cache_key)
            if result is not None:
                return result

        end = start + timezone.timedelta(days=next_x_days - 1)
        filtered_subject_class = SubjectClass.objects.filter(
            class_start_time__date__lte=start, class_end_time__date__gte=end
        )
        if use_cache:
            cache.set(cache_key, filtered_subject_class, 60 * 5)
        return filtered_subject_class

    def is_in_attendance_window(self):
        current_time = timezone.now()
        return (
            self.attendance_start_time
            <= current_time
            <= (
                self.attendance_end_time
                if self.attendance_end_time
                else self.class_end_time
            )
        )

    def get_all_attendance(self):
        subject_class_instance = self

        subject_class_student_groups = (
            subject_class_instance.subjectclassstudentgroups_set.all().values(
                "student_group_id", "attendance_policy"
            )
        )

        # Subquery to get the minimum attendance policy for each student group
        min_attendance_policy_subquery = subject_class_student_groups.annotate(
            min_policy=Subquery(
                SubjectClassStudentGroups.objects.filter(
                    student_group_id=OuterRef("student_group_id")
                )
                .order_by("attendance_policy")
                .values("attendance_policy")[:1]
            )
        ).values("student_group_id", "min_policy")

        student_group_ids = subject_class_student_groups.values_list(
            "student_group_id", flat=True
        )

        students_with_attendance = (
            Student.objects.filter(
                studentgroupitem__student_group_id__in=student_group_ids
            )
            .annotate(
                prioritized_attendance_policy=Min(
                    Subquery(
                        min_attendance_policy_subquery.filter(
                            student_group_id=OuterRef(
                                "studentgroupitem__student_group_id"
                            )
                        ).values("min_policy")
                    )
                )
            )
            .prefetch_related(
                Prefetch(
                    "classattendance_set",
                    queryset=ClassAttendance.objects.filter(
                        subject=subject_class_instance
                    ),
                    to_attr="attendance_obj",
                )
            )
        )

        for student in students_with_attendance:
            if student.attendance_obj:
                student.attendance = student.attendance_obj[0]
            else:
                student.attendance = None

        return students_with_attendance

    @classmethod
    def get_all_classes(cls, include_optional=False):
        if include_optional:
            return cls.objects.all()
        else:
            return cls.objects.filter(is_attendance_mandatory=True)


class SubjectClassStudentGroups(models.Model):
    class AttendancePolicy(Enum):
        Mandatory = 0
        Recommended = 1
        Optional = 2

    subject_class = models.ForeignKey(
        SubjectClass, on_delete=models.CASCADE, db_index=True
    )
    student_group = models.ForeignKey(
        StudentGroup, on_delete=models.CASCADE, db_index=True
    )
    attendance_policy = EnumField(AttendancePolicy, default=AttendancePolicy.Mandatory)

    class Meta:
        unique_together = ("subject_class", "student_group")


class ClassAttendance(models.Model):
    date_updated = models.DateTimeField(default=timezone.now)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        db_index=True,
    )
    subject = models.ForeignKey(SubjectClass, on_delete=models.CASCADE, db_index=True)
    attendance_status = EnumField(AttendanceStatus, default=AttendanceStatus.Absent)
    is_injested = models.BooleanField(default=False)

    class Meta:
        # Make the combination of student and subject unique
        unique_together = ("student", "subject")
        permissions = [
            ("can_mark_attendance", "Can Mark Attendance"),
            ("can_send_notifications", "Can Send Notifications"),
            ("verify_false_attempt", "Verify False Attempt GeoLocation"),
            ("can_injest_to_scaler", "Can Injest to Scaler"),
        ]

    def __str__(self):
        return self.student.mail + " " + self.subject.name

    def save(self, injested=False, *args, **kwargs):
        if not injested:
            self.is_injested = False
            self.date_updated = timezone.now()

        super().save(*args, **kwargs)

    def injest_to_scaler(self):
        from utils.injest_attendance import injest_class_attendance_to_scaler

        if not self.subject.can_injest():
            return False

        if injest_class_attendance_to_scaler(self):
            self.is_injested = True
            self.save(injested=True)
            return True
        else:
            return False

    @classmethod
    def get_attendance_status_for(cls, student, subject):
        obj = ClassAttendance.objects.filter(student=student, subject=subject)
        if obj.exists():
            return obj.first().get_attendance_status()
        else:
            return AttendanceStatus.Absent

    def get_attendance_by_bsm_status(self):
        if not hasattr(self, "classattendancebybsm"):
            return None
        return ClassAttendanceByBSM.objects.get(
            pk=self.classattendancebybsm.pk
        ).get_attendance_status()

    def get_attendance_with_geo_location_status(self):
        if not hasattr(self, "classattendancewithgeolocation"):
            return None
        return ClassAttendanceWithGeoLocation.objects.get(
            pk=self.classattendancewithgeolocation.pk
        ).get_attendance_status()

    def get_attendance_status(self, use_field=True):
        if not use_field:
            by_bsm = self.get_attendance_by_bsm_status()
            with_geo_location = self.get_attendance_with_geo_location_status()
            attendance_status = ClassAttendance.get_attendance_status_by_status(
                by_bsm, with_geo_location
            )
            return attendance_status
        return self.attendance_status

    @classmethod
    def get_attendance_status_by_status(cls, status_by_bsm, status_by_geo):
        if status_by_bsm == AttendanceStatus.Present:
            return AttendanceStatus.Present

        if status_by_bsm == AttendanceStatus.Proxy:
            return AttendanceStatus.Proxy

        if status_by_geo == AttendanceStatus.Present:
            return AttendanceStatus.Present
        if status_by_geo == AttendanceStatus.Proxy:
            return AttendanceStatus.Proxy

        return AttendanceStatus.Absent

    def update_attendance_status(self):
        self.attendance_status = self.get_attendance_status(use_field=False)
        self.save()


class ClassAttendanceChildManager(models.QuerySet):
    def save(self, *args, **kwargs):
        for obj in self:
            obj.save()
        super(ClassAttendanceChildManager, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for obj in self:
            obj.delete()
        super(ClassAttendanceChildManager, self).delete(*args, **kwargs)


class ClassAttendanceWithGeoLocation(models.Model):
    objects = ClassAttendanceChildManager.as_manager()

    STATUS_CHOICES = [
        ("proxy", "Proxy"),
        ("verified", "Verified"),
        ("standby", "Standby"),
        ("flaggers", "Flaggers"),
    ]
    status_mapping = {
        "verified": AttendanceStatus.Present,
        "standby": AttendanceStatus.Present,
        "proxy": AttendanceStatus.Proxy,
    }
    date_updated = models.DateTimeField(auto_now=True)
    lat = models.DecimalField(max_digits=13, decimal_places=10)
    lon = models.DecimalField(max_digits=13, decimal_places=10)
    accuracy = models.DecimalField(max_digits=13, decimal_places=10)
    class_attendance = models.OneToOneField(
        ClassAttendance, on_delete=models.CASCADE, db_index=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="standby",  # Set the default value if needed
        db_index=True,
    )
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, default=None, blank=True, null=True
    )

    def get_attendance_status(self):
        return self.status_mapping.get(self.status)

    def save(self, *args, **kwargs):
        self.lat = round_coordinates(self.lat)
        self.lon = round_coordinates(self.lon)
        self.accuracy = round_coordinates(self.accuracy)

        super().save(*args, **kwargs)
        self.class_attendance.update_attendance_status()

    def delete(self, *args, **kwargs):
        class_attendance__pk = self.class_attendance.pk
        super().delete(*args, **kwargs)
        ClassAttendance.objects.get(pk=class_attendance__pk).update_attendance_status()

    def __str__(self):
        return str(self.class_attendance)

    @classmethod
    def create_with(cls, student, subject, lat, lon, accuracy):
        class_attendance, _ = ClassAttendance.objects.get_or_create(
            student=student, subject=subject
        )

        attendance, _ = ClassAttendanceWithGeoLocation.objects.get_or_create(
            class_attendance=class_attendance,
            defaults={"lat": lat, "lon": lon, "accuracy": accuracy},
        )
        attendance.save()
        return attendance

    @classmethod
    def create_from(cls, false_attempt, verified_by):
        obj = cls.create_with(
            false_attempt.student,
            false_attempt.subject,
            false_attempt.lat,
            false_attempt.lon,
            false_attempt.accuracy,
        )
        obj.status = "verified"
        obj.verified_by = verified_by
        obj.save()


class ProblemSolvingPercentage(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_index=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_index=True)

    solved_questions = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.student.mail)

    class Meta:
        # Make the combination of student and subject unique
        unique_together = ("student", "subject")


class ClassAttendanceByBSM(models.Model):
    objects = ClassAttendanceChildManager.as_manager()
    STATUS_CHOICES = [
        ("proxy", "Proxy"),
        ("present", "Present"),
        ("absent", "Absent"),
    ]
    status_mapping = {
        "present": AttendanceStatus.Present,
        "proxy": AttendanceStatus.Proxy,
        "absent": AttendanceStatus.Absent,
    }

    date_updated = models.DateTimeField(auto_now=True)
    marked_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    class_attendance = models.OneToOneField(
        ClassAttendance, on_delete=models.CASCADE, db_index=True
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="present", db_index=True
    )

    def __str__(self):
        return (
            f"{self.class_attendance.student.name} {self.class_attendance.subject.name}"
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.class_attendance.update_attendance_status()

    def delete(self, *args, **kwargs):
        class_attendance__pk = self.class_attendance.pk
        super().delete(*args, **kwargs)
        ClassAttendance.objects.get(pk=class_attendance__pk).update_attendance_status()

    def get_attendance_status(self):
        return self.status_mapping.get(self.status)

    @classmethod
    def create_with(cls, student, subject, status, marked_by):
        class_attendance, _ = ClassAttendance.objects.get_or_create(
            student=student, subject=subject
        )

        attendance, _ = ClassAttendanceByBSM.objects.update_or_create(
            class_attendance=class_attendance,
            defaults={"marked_by": marked_by, "status": status},
        )
        attendance.save()
        return attendance


class GeoLocationDataContrib(models.Model):
    label = models.SmallIntegerField(default=-2)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lat = models.DecimalField(max_digits=13, decimal_places=10)
    lon = models.DecimalField(max_digits=13, decimal_places=10)
    accuracy = models.DecimalField(max_digits=13, decimal_places=10)

    def save(self, *args, **kwargs):
        self.lat = round_coordinates(self.lat)
        self.lon = round_coordinates(self.lon)
        self.accuracy = round_coordinates(self.accuracy)

        super().save(*args, **kwargs)


class FalseAttemptGeoLocation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_index=True)
    lat = models.DecimalField(max_digits=13, decimal_places=10)
    lon = models.DecimalField(max_digits=13, decimal_places=10)
    accuracy = models.DecimalField(max_digits=13, decimal_places=10)
    creation_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    subject = models.ForeignKey(
        SubjectClass, on_delete=models.CASCADE, db_index=True, blank=True, null=True
    )

    def save(self, *args, **kwargs):
        self.lat = round_coordinates(self.lat)
        self.lon = round_coordinates(self.lon)
        self.accuracy = round_coordinates(self.accuracy)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject.name}: {self.student.mail.split('@')[0]}"


class ProjectConfiguration(models.Model):
    APP_LATEST_VERSION = models.CharField(max_length=12)
    MIN_SUPPORTED_APP_VERSION = models.CharField(max_length=12, default="1.0.0")
    APK_FILE = models.TextField()
    VERSION_NAME = models.CharField(max_length=20, default="")
    INJEST_ATTENDANCE_IN_REAL_TIME = models.BooleanField(default=False)
    CRON_TOKEN = models.CharField(max_length=200, default=None, null=True, blank=True)

    class Meta:
        permissions = [
            ("can_sync_to_gsheet", "Can Sync Attendance with Gsheet"),
        ]

    def save(self, *args, **kwargs):
        # Override save to ensure only one instance is saved
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        cache_key = "ProjectConfigurationSingeltonObject"
        result = cache.get(cache_key)

        if result is not None:
            return result
        # Load the singleton object and return its configuration values
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "APP_LATEST_VERSION": "0.2.5",
                "APK_FILE": "https://drive.google.com/file/d/1dgL7fEq16OugBBxLo2Twn_SC6IGXYmjp/view?usp=sharing",  # noqa: E501
            },
        )
        cache.set(cache_key, obj, 60 * 5)
        return obj
