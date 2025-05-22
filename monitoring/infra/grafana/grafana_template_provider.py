import json
from typing import Any

from monitoring.infra.jinja2.jinja2_template_renderer import Jinja2TemplateRenderer
from monitoring.service.i_template_renderer.template_renderer import ITemplateRenderer
from monitoring.service.i_visualization_platform.i_template_provider import (
    VisualizationPlatformTemplateProvider,
)


class GrafanaTemplateProvider(VisualizationPlatformTemplateProvider):
    def __init__(self):
        # TODO: DI
        self.template_provider: ITemplateRenderer = Jinja2TemplateRenderer()

    def render_logs_dashboard_json(
        self,
        user_id: str,
        dashboard_title: str,
        dashboard_uid: str,
        data_source_uid: str = "Elasticsearch",
    ) -> dict[str, Any]:
        dash_board_json = self.template_provider.render(
            "grafana_log_dashboard_json.j2",
            {
                "user_id": user_id,
                "dashboard_title": dashboard_title,
                "dashboard_uid": dashboard_uid,
                "data_source_uid": data_source_uid,
            },
        )
        try:
            return json.loads(dash_board_json)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"로그 대시보드 JSON 파싱 실패: {e}")
