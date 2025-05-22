from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitoring"

    def ready(self) -> None:
        import monitoring.infra.models.task_result_model
        import monitoring.infra.models.visualization_platform_model
