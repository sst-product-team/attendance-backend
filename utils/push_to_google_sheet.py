import gspread
from attendance.models import AttendanceStatus, Student
from gspread.utils import rowcol_to_a1
from django.conf import settings

# GSHEEET FORMAT
# -    ,            ,12 feb 2023    ,  13 feb 2024
# email,user_name   ,Morning class  , Evening Class
# mail1, name1      ,1              ,0
# mail2, name2      ,1              ,1
# ...  , ...        ,0              ,1


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
    data = [["", ""], ["email", "user name"]]

    students = Student.get_all_students()
    mail_name = []
    for student in students:
        mail_name.append([student.mail.lower(), student.name.lower()])

    mail_name = sorted(mail_name, key=lambda x: x[0])

    data.extend(mail_name)
    update_range(sheet, data, 1, 1)


def get_or_create_subject_sheet(sh, subject):
    title = subject.name if subject else "-"
    try:
        return sh.worksheet(title), False
    except gspread.exceptions.WorksheetNotFound:
        sh.add_worksheet(title, rows=1000, cols=1000)
        return sh.worksheet(title), True


def subject_to_col_title(subject_class):
    return (
        subject_class.class_start_time.strftime("%d %b %Y"),
        subject_class.name,
    )


def get_col_for_subject_class(sheet, subject_class):
    PADDING_START = 2
    (date, title) = subject_to_col_title(subject_class)
    date_row_values = sheet.row_values(1)[PADDING_START:]
    title_row_values = sheet.row_values(2)[PADDING_START:]
    for idx, (row_date, row_title) in enumerate(zip(date_row_values, title_row_values)):
        print(idx, row_date, row_title, date, title)
        if row_date == date and row_title == title:
            return idx + 1 + PADDING_START
    return len(date_row_values) + 1 + PADDING_START


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
            value = status_map[mail]
        else:
            value = 0

        return_status.append(1 if value else 0)

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
    mails = sheet.col_values(1)[2:]
    attendance_data = get_attendance_mapping(mails, subject_class)

    data = [*subject_to_col_title(subject_class)]
    data.extend(attendance_data)
    update_range(sheet, [[e] for e in data], 1, col)

    return True
