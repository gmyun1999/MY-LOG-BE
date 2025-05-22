from abc import ABC, abstractmethod
from typing import Any, Dict


class VisualizationPlatformTemplateProvider(ABC):
    @abstractmethod
    def render_logs_dashboard_json(
        self,
        user_id: str,
        dashboard_title: str,
        dashboard_uid: str,
        data_source_uid: str = "Elasticsearch",
    ) -> Dict[str, Any]:
        """
        로그 대시보드용 JSON 구조를 렌더링하여
        바로 API 호출에 사용할 dict 형태로 반환.
        """
        ...
