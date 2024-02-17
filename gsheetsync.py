import gspread
from attendance.models import AttendanceStatus, SubjectClass, Student
from gspread.utils import rowcol_to_a1
from django.conf import settings


gc = gspread.service_account_from_dict(settings.GOOGLE_SHEET_CREDENTIAL)
sh = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/19rE4LVyjeERJCbP8UkpAvYXYrtt-iGNxBJnG2jqrddc/edit?usp=sharing"
)

ATTENDANCE_FROM = 4


def update_range(sheet, data, start_row, start_col):
    range_value = (
        f"{rowcol_to_a1(start_row, start_col)}"
        ":"
        f"{rowcol_to_a1(start_row+len(data)-1, start_col + len(data[0])-1)}"
    )
    sheet.update(
        range_value,
        data,
    )


def init_sheet_with_data(sheet, subject_class):
    data = [["email", "name"]]

    students = Student.get_all_students()
    mail_name = []
    for student in students:
        mail_name.append([student.mail.lower(), student.name.lower()])

    mail_name = sorted(mail_name, key=lambda x: x[0])

    data.extend(mail_name)
    update_range(sheet, data, 1, 1)


def get_or_create_subject_sheet(subject):
    try:
        return sh.worksheet(subject.name), False
    except gspread.exceptions.WorksheetNotFound:
        sh.add_worksheet(subject.name, rows=1000, cols=1000)
        return sh.worksheet(subject.name), True


def get_col_for_subject_class(sheet, subject_class):
    col = len(sheet.row_values(1)) + 1
    return col


def get_attendance_mapping(mails, subject_class):
    attendances = subject_class.get_all_attendance()
    status_map = {}
    for att in attendances:
        status_map[att.student.mail] = (
            1 if AttendanceStatus.Present == att.attendance_status else 0
        )

    return_status = []
    for mail in mails:
        if mail in status_map:
            return_status.append(status_map[mail])
        else:
            return_status.append(0)

    return return_status


def sync_subject_class(subject_class):
    sheet, created = get_or_create_subject_sheet(subject_class.subject)
    if created:
        init_sheet_with_data(sheet, subject_class)

    col = get_col_for_subject_class(sheet, subject_class)
    mails = sheet.col_values(1)[1:]
    attendance_data = get_attendance_mapping(mails, subject_class)

    data = [str(subject_class)]
    data.extend(attendance_data)
    update_range(sheet, [[e] for e in data], 1, col)


subject_class = SubjectClass.objects.first()
sync_subject_class(subject_class)
print(sh.sheet1.cell(1, 1).value)
