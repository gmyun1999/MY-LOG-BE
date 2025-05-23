from abc import ABC, abstractmethod
from typing import Any

from monitoring.domain.task_result import TaskResult


class ITaskResultRepo(ABC):
    @abstractmethod
    def save(self, task_result: TaskResult) -> None:
        pass

    @abstractmethod
    def update(self, task_result: TaskResult) -> None:
        pass

    @abstractmethod
    def find_by_task_id(self, task_id: str) -> TaskResult | None:
        pass

    @abstractmethod
    def update_fields(self, task_id: str, **fields: Any) -> None:
        """
        SELECT 없이 단일 UPDATE 수행
        """
        pass

    @abstractmethod
    def bulk_upsert(self, task_results: list[TaskResult]) -> None:
        """
        Django 4.1+ bulk_create의 update_conflicts 옵션을 활용한 upsert 예시.
        존재하지 않으면 insert, 존재하면 update 합니다.
        """
        pass
