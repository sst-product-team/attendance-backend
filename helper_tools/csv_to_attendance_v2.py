import csv
from attendance.models import (
    SubjectClass,
    Student,
    ClassAttendanceByBSM,
)
from django.contrib.auth.models import User
import json

# import time
from tqdm import tqdm


meta_file_path = "helper_tools/meta.json"


def read_meta_file():
    file = open(meta_file_path, "r")
    meta_instructions = json.load(file)
    file.close()
    return meta_instructions


def write_to_meta_file(d):
    file = open(meta_file_path, "w")
    json.dump(d, file, indent=2)
    file.close()


iosUsers = []
iosUsers = [s.lower() for s in iosUsers]

attendance_status_mapper = {
    "P": "present",
    "A": "absent",
}
# Specify the path to your CSV file
csv_file_path = ""


def process(SubjectClassId, MarkedByBSMMail, ClassInCSV, ios_only):
    bsm = User.objects.get(email=MarkedByBSMMail)
    subject = SubjectClass.objects.get(id=SubjectClassId)

    # Open the CSV file
    file = open(csv_file_path, "r")
    csv_reader = csv.DictReader(file)

    # Iterate through each row in the CSV file
    all_rows = list(csv_reader)
    print(len(all_rows))
    pbar = tqdm(all_rows, total=len(all_rows))
    for row in pbar:
        # for row in csv_reader:

        if (
            row[ClassInCSV] != "P"  # Assuming "A" is the IdleValueInCSV
            or row[ClassInCSV] not in attendance_status_mapper
        ):
            continue

        mail = row["mail"].lower()
        if ios_only and (mail not in iosUsers):
            continue

        if mail.endswith("@ms.sst.scaler.com"):
            mail = mail.replace("@ms.sst.scaler.com", "@sst.scaler.com")

        pbar.set_description(f"Processing {mail}")

        student, _ = Student.objects.get_or_create(mail=mail)
        if student.name is None or len(student.name) == 0:
            student.name = row["NAME"]
            student.save()

        ClassAttendanceByBSM.create_with(
            student=student,
            subject=subject,
            status=attendance_status_mapper.get(row[ClassInCSV]),
            marked_by=bsm,
        )
        # time.sleep(1)

    file.close()


meta_instructions = read_meta_file()
i = 0
while i < len(meta_instructions):
    d = meta_instructions[i]

    SubjectClassId = d["SubjectClassId"]
    MarkedByBSMMail = d["MarkedByBSMMail"]
    ClassInCSV = d["ClassInCSV"]
    ios_only = d["ios_only"]

    if not d["done"]:
        print("Injesting:", d)
        process(SubjectClassId, MarkedByBSMMail, ClassInCSV, ios_only)
        d["done"] = True

        meta_instructions = read_meta_file()
        meta_instructions[i] = d
        write_to_meta_file(meta_instructions)
    i += 1
