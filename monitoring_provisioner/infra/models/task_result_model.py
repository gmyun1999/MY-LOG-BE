from django.db import models

from monitoring_provisioner.domain.task_result import TaskStatus

class TaskResultModel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,
        editable=False
    )
    task_id = models.CharField(
        max_length=36,
        unique=True
    )
    task_name = models.CharField(max_length=255)

    status = models.CharField(
        max_length=16,
        choices=[(status.value, status.value) for status in TaskStatus],
        default=TaskStatus.PENDING.value
    )

    result = models.JSONField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_started = models.DateTimeField(null=True, blank=True)
    date_done = models.DateTimeField(null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)
    retries = models.IntegerField(default=0)

    class Meta:
        db_table = "task_result_model"