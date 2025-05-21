from django.apps import AppConfig


class MonitoringProvisionerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitoring_provisioner"

    def ready(self) -> None:
        import monitoring_provisioner.infra.models.task_result_model
        import monitoring_provisioner.infra.models.visualization_platform_model
