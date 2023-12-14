import csv
from attendance.models import Student, SubjectClass, ClassAttendance, AttendanceStatus
from tqdm import tqdm

file_path = "attendance.csv"
cf = open(file_path, "w", newline="")
csv_writer = csv.writer(cf)

classes = (
    SubjectClass.objects.filter(is_attendance_mandatory=True)
    .order_by("class_start_time")
    .all()
)

csv_writer.writerow(["name", "mail", *[str(c) for c in classes]])

students = Student.get_all_students().order_by("name")
i = 0
for student in tqdm(students):
    row = [student.name, student.mail]
    for subject in classes:
        status = ClassAttendance.get_attendance_status_for(
            student=student, subject=subject
        )

        if status == AttendanceStatus.Present:
            row.append("P")
        else:
            row.append("A")

    csv_writer.writerow(row)
    # print(i)
    i += 1
