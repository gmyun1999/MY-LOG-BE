from monitoring_provisioner.domain.i_repository.i_task_result_repo import (
    ITaskResultRepository,
)
from monitoring_provisioner.domain.task_result import TaskResult
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel


class TaskResultRepository(ITaskResultRepository):
    def save(self, task_result: TaskResult) -> TaskResult:

        fields = task_result.to_dict()
        TaskResultModel.objects.create(**fields)
        return task_result

    def update(self, task_result: TaskResult) -> None:
        fields = task_result.to_dict(
            excludes=[
                task_result.FIELD_ID,
                task_result.FIELD_TASK_ID,
                task_result.FIELD_TASK_NAME,
                task_result.FIELD_DATE_CREATED,
            ]
        )
        TaskResultModel.objects.filter(id=task_result.id).update(**fields)

    def find_by_id(self, task_result_id: int) -> TaskResult | None:
        try:
            obj = TaskResultModel.objects.get(id=task_result_id)
            return self._to_domain(obj)
        except TaskResultModel.DoesNotExist:
            return None

    def _to_domain(self, obj: TaskResultModel) -> TaskResult:
        return TaskResult.from_dict(
            {
                "id": obj.id,
                "task_id": obj.task_id,
                "task_name": obj.task_name,
                "status": obj.status,
                "result": obj.result,
                "date_created": obj.date_created.isoformat(),
                "date_done": obj.date_done.isoformat() if obj.date_done else None,
                "traceback": obj.traceback,
                "retries": obj.retries,
            }
        )
