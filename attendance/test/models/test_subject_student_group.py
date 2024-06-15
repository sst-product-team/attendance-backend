from django.test import TestCase
from attendance.models import SubjectClass, StudentGroupItem, SubjectClassStudentGroups


def get_students_from_group_ids(group_ids):
    # Create a Q object to filter the StudentGroupItem based on the group IDs
    group_items = StudentGroupItem.objects.filter(
        student_group_id__in=group_ids
    ).select_related("student")

    students = set(group_item.student for group_item in group_items)
    return students


class SubjectStudentGroupTest(TestCase):
    fixtures = ["fixtures_dev_db.json"]

    def test_with_geolocation_update(self):
        subject_class_instance = SubjectClass.objects.get(pk=70)
        students = subject_class_instance.get_all_students()
        students = set(students)

        all_group_ids = [
            e.student_group.pk
            for e in subject_class_instance.subjectclassstudentgroups_set.all()
        ]
        all_students = get_students_from_group_ids(all_group_ids)
        all_students = set(all_students)

        self.assertEqual(len(students), len(all_students), "len not equal")
        self.assertEqual(
            students, all_students, "all students for a class is not working"
        )

    def test_attendance_policy(self):
        subject_class_instance = SubjectClass.objects.get(pk=78)
        students_with_policy = (
            subject_class_instance.get_students_with_prioritized_attendance_policy()
        )

        self.assertEqual(len(students_with_policy), 3)

        output = {}
        for e in students_with_policy:
            if e.mail in output:
                self.fail("multiple instances of same student found")
            else:
                output[e.mail] = e.prioritized_attendance_policy

        expected = {
            "diwakar.gupta@scaler.com": SubjectClassStudentGroups.AttendancePolicy.Optional,  # noqa: E501
            "kushagra.23bcs10165@sst.scaler.com": SubjectClassStudentGroups.AttendancePolicy.Mandatory,  # noqa: E501
            "pritam.23bcs10108@sst.scaler.com": SubjectClassStudentGroups.AttendancePolicy.Recommended,  # noqa: E501
        }

        self.assertEqual(
            expected.keys(), output.keys(), "output has different student groups"
        )

        for key in list(expected.keys()):
            self.assertEqual(
                expected[key], output[key], "Prioritised attendance policy incorrect"
            )

    def test_get_all_attendance(self):
        subject_class_instance = SubjectClass.objects.get(pk=78)
        students_with_policy = subject_class_instance.get_all_attendance()

        self.assertEqual(len(students_with_policy), 3)

        output = {}
        for e in students_with_policy:
            if e.mail in output:
                self.fail("multiple instances of same student found")
            else:
                output[e.mail] = {
                    "policy": e.prioritized_attendance_policy,
                    "attendance": e.attendance.pk if e.attendance else None,
                }

        expected = {
            "diwakar.gupta@scaler.com": {
                "policy": SubjectClassStudentGroups.AttendancePolicy.Optional,
                "attendance": None,
            },
            "kushagra.23bcs10165@sst.scaler.com": {
                "policy": SubjectClassStudentGroups.AttendancePolicy.Mandatory,
                "attendance": 5803,
            },
            "pritam.23bcs10108@sst.scaler.com": {
                "policy": SubjectClassStudentGroups.AttendancePolicy.Recommended,
                "attendance": None,
            },
        }

        self.assertEqual(
            expected.keys(), output.keys(), "output has different student groups"
        )

        for key in list(expected.keys()):
            self.assertEqual(
                expected[key], output[key], "Prioritised attendance policy incorrect"
            )
