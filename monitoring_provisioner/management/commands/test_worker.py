from django.core.management.base import BaseCommand

from monitoring_provisioner.infra.celery.executor.grafana_executor import (
    GrafanaExecutor,
)


class Command(BaseCommand):
    help = "Create Grafana dashboard via Celery task"

    def handle(self, *args, **kwargs):
        executor = GrafanaExecutor()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()
        executor.create_dashboard()

        self.stdout.write(
            self.style.SUCCESS("Dashboard creation task has been queued.")
        )
