from django.core.management.base import BaseCommand

from attendance.models import ClassAttendance
from tqdm import tqdm


class Command(BaseCommand):
    help = "Injests attendance to upstream server"

    def add_arguments(self, parser):
        parser.add_argument("count", type=int)
        parser.add_argument(
            "--subject_pk", type=int, default=None, help="Filter by subject PrimaryKey"
        )

    def handle(self, *args, **options):
        PROCESS_N_VALUES = options["count"]
        subject_pk = options["subject_pk"]

        filter_criteria = {
            "is_injested": False,
            "subject__class_topic_slug__gt": "",
            "subject__super_batch_id__gt": 0,
        }

        if subject_pk is not None:
            filter_criteria["subject__pk"] = subject_pk

        attendances = ClassAttendance.objects.filter(**filter_criteria)

        self.stdout.write("Total entries:%s" % len(attendances))

        if PROCESS_N_VALUES < len(attendances):
            attendances = attendances[:PROCESS_N_VALUES]
        else:
            PROCESS_N_VALUES = len(attendances)

        total_entries = len(attendances)
        self.stdout.write("Injesting %s entries" % total_entries)
        pbar = tqdm(attendances, total=total_entries)

        success_pk = []
        failed_pk = []
        for attendance in pbar:
            result = attendance.injest_to_scaler()
            if result:
                success_pk.append(attendance.pk)
            else:
                failed_pk.append(attendance.pk)

        if len(failed_pk) > 0:
            self.stdout.write("Faliled to injest %s entries." % len(failed_pk))
            self.stdout.write(str(failed_pk))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully injested %s entries" % PROCESS_N_VALUES
                )
            )
