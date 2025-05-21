from typing import Any

from django.forms import model_to_dict
from typing_extensions import override

from monitoring_provisioner.domain.i_repo.i_task_result_repo import ITaskResultRepo
from monitoring_provisioner.domain.task_result import TaskResult, TaskStatus
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel


class TaskResultRepo(ITaskResultRepo):
    @override
    def find_by_task_id(self, task_id: str) -> TaskResult | None:
        try:
            model = TaskResultModel.objects.get(id=task_id)
            return TaskResult(
                id=model.id,
                task_name=model.task_name,
                status=TaskStatus(model.status),
                result=model.result,
                date_created=model.date_created.isoformat(),
                date_started=(
                    model.date_started.isoformat() if model.date_started else None
                ),
                date_done=model.date_done.isoformat() if model.date_done else None,
                traceback=model.traceback,
                retries=model.retries,
            )
        except TaskResultModel.DoesNotExist:
            return None

    @override
    def save(self, task_result: TaskResult) -> None:
        TaskResultModel.objects.update_or_create(
            id=task_result.id, defaults=task_result.to_dict()
        )

    @override
    def update(self, task_result: TaskResult) -> None:
        TaskResultModel.objects.filter(id=task_result.id).update(
            **task_result.to_dict()
        )

    @override
    def update_fields(self, task_id: str, **fields: Any) -> None:
        TaskResultModel.objects.filter(id=task_id).update(**fields)
