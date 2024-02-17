import gspread
from attendance.models import AttendanceStatus, Student
from gspread.utils import rowcol_to_a1
from django.conf import settings


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


def init_sheet_with_data(sheet):
    data = [["email", "name", ""]]

    students = Student.get_all_students()
    mail_name = []
    for student in students:
        mail_name.append([student.mail.lower(), student.name.lower()])

    mail_name = sorted(mail_name, key=lambda x: x[0])

    data.extend(mail_name)
    update_range(sheet, data, 1, 1)


def get_or_create_subject_sheet(sh, subject):
    try:
        return sh.worksheet(subject.name), False
    except gspread.exceptions.WorksheetNotFound:
        sh.add_worksheet(subject.name, rows=1000, cols=1000)
        return sh.worksheet(subject.name), True


def subject_to_col_title(subject_class):
    return str(subject_class)


def get_col_for_subject_class(sheet, subject_class):
    title = subject_to_col_title(subject_class)
    row_values = sheet.row_values(1)
    for idx, value in enumerate(row_values):
        if value == title:
            return idx + 1
    return len(row_values) + 1


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


def get_spreadsheet():
    if not settings.GOOGLE_SHEET_CREDENTIAL:
        return None
    gc = gspread.service_account_from_dict(settings.GOOGLE_SHEET_CREDENTIAL)
    sh = gc.open_by_url(settings.GOOGLE_SHEET_LINK)
    return sh


def can_sync_subject_class(subject_class):
    if not settings.GOOGLE_SHEET_LINK:
        return False
    if not settings.GOOGLE_SHEET_CREDENTIAL:
        return False
    return hasattr(subject_class, "subject")


def sync_subject_class(subject_class):
    sh = get_spreadsheet()
    if not sh:
        return False

    sheet, created = get_or_create_subject_sheet(sh, subject_class.subject)
    if created:
        init_sheet_with_data(sheet)

    col = get_col_for_subject_class(sheet, subject_class)
    mails = sheet.col_values(1)[1:]
    attendance_data = get_attendance_mapping(mails, subject_class)

    data = [subject_to_col_title(subject_class)]
    data.extend(attendance_data)
    update_range(sheet, [[e] for e in data], 1, col)

    return True
