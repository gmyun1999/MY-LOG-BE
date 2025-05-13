from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitoring_provisioner"

    def ready(self) -> None:
        pass