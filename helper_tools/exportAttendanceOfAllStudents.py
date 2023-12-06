import csv
from attendance.models import Student, Subject

file_path = 'attendance.csv'
cf=open(file_path, 'w', newline='')
csv_writer = csv.writer(cf)

subjects = [s.name for s in Subject.objects.all()]

csv_writer.writerow(['name', 'mail', *subjects])

students = Student.get_all_students()
i=0
for student in students:
    data = Student.get_aggregated_attendance(student = student)
    # print(data)

    d = [student.name, student.mail]
    for s in subjects:
        if s in data:
            present = data[s]["Present"] if "Present" in data[s] else 0
            totalClasses = data[s]["totalClassCount"] if "totalClassCount" in data[s] else 100000000

            p = round(100 * (present / totalClasses), 1)
            d.append(p)
        else:
            d.append('-')
            
    csv_writer.writerow(d)
    print(i)
    i += 1


 



