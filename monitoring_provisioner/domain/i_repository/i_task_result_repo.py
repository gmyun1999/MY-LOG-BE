from abc import ABC, abstractmethod

from monitoring_provisioner.domain.task_result import TaskResult


class ITaskResultRepository(ABC):
    @abstractmethod
    def save(self, task_result: TaskResult) -> TaskResult:
        pass

    @abstractmethod
    def update(self, task_result: TaskResult) -> None:
        pass

    @abstractmethod
    def find_by_id(self, task_result_id: int) -> TaskResult | None:
        pass
