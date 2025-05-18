from django.core.management.base import BaseCommand

from monitoring_provisioner.infra.celery.executor.grafana_executor import GrafanaExecutor


class Command(BaseCommand):
    help = "Create Grafana resources via Celery tasks"

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=str, default="test_user_123")
        parser.add_argument('--user-name', type=str, default="Test User")
        parser.add_argument('--dashboard-title', type=str, default="Test Dashboard")

    def handle(self, *args, **options):
        executor = GrafanaExecutor()
        
        user_id = options['user_id']
        user_name = options['user_name']
        dashboard_title = options['dashboard_title']
        
        # 사용자 폴더 생성
        self.stdout.write("Creating user folder...")
        task_id = executor.create_user_folder(user_id, user_name)
        self.stdout.write(self.style.SUCCESS(f"User folder creation task has been queued. Task ID: {task_id}"))
        
        # 대시보드 생성
        self.stdout.write("Creating dashboard...")
        executor.create_dashboard(
            user_id=user_id,
            title=dashboard_title,
            panels=[
                {
                    "id": 1,
                    "type": "graph",
                    "title": "CPU Usage",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "type": "graph",
                    "title": "Memory Usage",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                }
            ]
        )
        self.stdout.write(self.style.SUCCESS("Dashboard creation task has been queued."))