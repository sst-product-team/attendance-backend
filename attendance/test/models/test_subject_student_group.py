from django.test import TestCase
from attendance.models import SubjectClass, SubjectClassStudentGroups

def get_students_from_group_ids(group_ids):
    from django.db.models import Q
    from attendance.models import Student, StudentGroup, StudentGroupItem
    # Create a Q object to filter the StudentGroupItem based on the group IDs
    group_items = StudentGroupItem.objects.filter(
        student_group_id__in=group_ids
    ).select_related('student')

    students = set(group_item.student for group_item in group_items)
    return students

class SubjectStudentGroupTest(TestCase):
    fixtures = ["fixtures_dev_db.json"]

    def test_with_geolocation_update(self):
        subject_class_instance = SubjectClass.objects.get(pk=70)
        students = subject_class_instance.get_all_students()
        students = set(students)

        all_group_ids = [e.student_group.pk for e in subject_class_instance.subjectclassstudentgroups_set.all()]
        all_students = get_students_from_group_ids(all_group_ids)
        all_students = set(all_students)
        
        self.assertEqual(len(students), len(all_students), "len not equal")        
        self.assertEqual(students, all_students, "all students for a class is not working")
        

    def test_attendance_policy(self):
        subject_class_instance = SubjectClass.objects.get(pk=78)
        students_with_policy = subject_class_instance.get_students_with_prioritized_attendance_policy()
        
        self.assertEqual(len(students_with_policy), 3)
        
        output = {}
        for e in students_with_policy:
            output[e.mail] = e.prioritized_attendance_policy
        
        expected = {
            "diwakar.gupta@scaler.com": SubjectClassStudentGroups.AttendancePolicy.Optional,
            "kushagra.23bcs10165@sst.scaler.com": SubjectClassStudentGroups.AttendancePolicy.Mandatory,
            "pritam.23bcs10108@sst.scaler.com": SubjectClassStudentGroups.AttendancePolicy.Recommended
        }
        self.assertEqual(output, expected, "attendance priority in grould not working")
