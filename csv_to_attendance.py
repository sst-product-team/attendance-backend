import csv
from attendance.models import SubjectClass, Student, ClassAttendance, ClassAttendanceByBSM

# import argparse

MarkedByBSMMail = 'diwakar.gupta@scaler.com'
SubjectClassId = 1
ClassInCSV = '11/8/2023 WebDev'

IdleValueInCSV = '-'

attendance_status_mapper = {
    'P':'present',
    'A':'absent',
}


bsm = Student.objects.get(mail=MarkedByBSMMail)
subject = SubjectClass.objects.get(id = SubjectClassId)

# Specify the path to your CSV file
csv_file_path = "/Users/diwakargupta/Downloads/SST Attendence sheet - Attendence.csv"

# Open the CSV file using the 'with' statement
with open(csv_file_path, 'r') as file:
    # Create a CSV reader object that returns dictionaries
    csv_reader = csv.DictReader(file)

    # Iterate through each row in the CSV file
    for row in csv_reader:
        # Each 'row' is a dictionary representing a row in the CSV file
        
        if row[ClassInCSV] == IdleValueInCSV or row[ClassInCSV] not in attendance_status_mapper:
            continue
        
        mail = row['mail'].lower()
        if mail.endswith('@ms.sst.scaler.com'):
            mail = mail.replace('@ms.sst.scaler.com', '@sst.scaler.com')

        print(mail)
        
        student, is_created = Student.objects.get_or_create(mail=mail)
        if (student.name == None or len(student.name) == 0):
            student.name = row['NAME']
            student.save()

        attendance_obj = ClassAttendanceByBSM.create_with(
            student=student,
            subject=subject,
            status=attendance_status_mapper.get(row[ClassInCSV]),
            marked_by=bsm
        )
