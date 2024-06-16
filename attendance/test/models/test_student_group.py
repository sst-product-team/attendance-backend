from django.test import TestCase
from attendance.models import (
    Student,
    StudentGroup,
    StudentGroupItem,
)
from django.contrib.auth.models import User


def get_students_from_group_ids(group_ids):
    # Create a Q object to filter the StudentGroupItem based on the group IDs
    group_items = StudentGroupItem.objects.filter(
        student_group_id__in=group_ids
    ).select_related("student")

    students = set(group_item.student for group_item in group_items)
    return students


class Object(object):
    pass


class SubjectStudentGroupTest(TestCase):
    fixtures = ["fixtures_dev_db.json"]

    def test_add_bulk_students_to_group(self):
        group = StudentGroup.objects.get(pk=8)
        success, messge = group.add_students_to_group(["diwakar.gupta@scaler.com"])
        self.assertTrue(success)
        students = get_students_from_group_ids([group.pk])
        self.assertEqual(3, len(students))

        success, messge = group.add_students_to_group(
            ["diwakar.gupta@scaler.com", "siddham.23bcs10103@sst.scaler.com"]
        )
        self.assertTrue(success)
        students = get_students_from_group_ids([group.pk])
        self.assertEqual(4, len(students))

        success, messge = group.add_students_to_group(
            ["random@scaler.co", "siddham.23bcs10103@sst.scaler.com"]
        )
        self.assertFalse(success)
        students = get_students_from_group_ids([group.pk])
        self.assertEqual(4, len(students))

    def test_add_student_to_group_permission(self):
        admin = User.objects.get(email="studentgroup_add@test.com")

        request = Object()
        request.user = admin
        self.assertTrue(Student.can_add_student_to_group(request))

        no_permission_user = User.objects.get(email="no_permission_user@test.com")
        request = Object()
        request.user = no_permission_user
        self.assertFalse(Student.can_add_student_to_group(request))
