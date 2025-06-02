from django.core.management.base import BaseCommand

from monitoring.domain.task_result import TaskStatus
from monitoring.infra.models.task_result_model import TaskResultModel


class Command(BaseCommand):
    help = "Delete task results with FAILURE or PENDING status"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Delete all task results regardless of status",
        )
        parser.add_argument(
            "--status",
            type=str,
            help="Delete tasks with specific status (FAILURE, PENDING, STARTED, SUCCESS)",
        )

    def handle(self, *args, **options):
        if options["all"]:
            count, details = TaskResultModel.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {count} task results of all statuses"
                )
            )
            return

        if options["status"]:
            status = options["status"].upper()
            count, details = TaskResultModel.objects.filter(status=status).delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {count} task results with status {status}"
                )
            )
            return

        # 기본: FAILURE 및 PENDING 삭제
        failed_count, _ = TaskResultModel.objects.filter(
            status=TaskStatus.FAILURE
        ).delete()
        pending_count, _ = TaskResultModel.objects.filter(
            status=TaskStatus.PENDING
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {failed_count} FAILURE and {pending_count} PENDING task results"
            )
        )
