import re
from typing import Any

from typing_extensions import override

from monitoring.domain.log_agent.agent_provision_context import (
    AgentProvisioningContext,
    PlatformType,
)
from monitoring.domain.log_agent.log_collector import (
    LogCollectorConfigContext,
    LogInputType,
)
from monitoring.domain.log_agent.log_router import LogRouterConfigContext
from monitoring.domain.log_agent.rendered_config import RenderedConfigFile
from monitoring.infra.jinja2.jinja2_template_renderer import Jinja2TemplateRenderer
from monitoring.service.i_log_agent.i_log_agent_provider import ILogAgentProvider
from monitoring.service.i_template_renderer.template_renderer import ITemplateRenderer


class FileBeats(ILogAgentProvider):
    """
    LogCollector 및 Router 설정, Bootstrap 스크립트를 Jinja2 템플릿으로 생성.
    """

    def __init__(self):
        # TODO: DI
        self.template_provider: ITemplateRenderer = Jinja2TemplateRenderer()

    @override
    def create_log_collector_config(
        self, context: LogCollectorConfigContext
    ) -> RenderedConfigFile:

        if context.input_type is LogInputType.PLAIN:
            ctx = self._build_plain_log_context(context)
            tpl_name = "filebeat_plain_text.j2"
        else:
            ctx = self._build_json_log_context(context)
            tpl_name = "filebeat_json.j2"

        rendered = self.template_provider.render(tpl_name, ctx)
        data = rendered.encode()

        return RenderedConfigFile(
            filename=f"collector_{context.project_id}.yml", content=data
        )

    def _build_plain_log_context(
        self, context: LogCollectorConfigContext
    ) -> dict[str, Any]:
        raw_fields = context.custom_plain_fields or []
        return {
            "project_id": context.project_id,
            "hosts": context.hosts,
            "log_paths": context.log_paths,
            "multiline_pattern": context.multiline_pattern,
            "filters": context.filters,
            "tokenizer_parts": self._build_tokenizer_parts(raw_fields),
            "fields": list({flt.field for flt in context.filters}),
        }

    def _build_json_log_context(
        self, context: LogCollectorConfigContext
    ) -> dict[str, Any]:
        return {
            "project_id": context.project_id,
            "hosts": context.hosts,
            "log_paths": context.log_paths,
            "filters": context.filters,
            "timestamp_field": context.timestamp_field,
            "timestamp_json_path": context.timestamp_json_path,
            "log_level": context.log_level,
            "log_level_json_path": context.log_level_json_path,
            "custom_json_fields": context.custom_json_fields,
        }

    def _build_tokenizer_parts(self, tokens: list[str]) -> list[str]:
        parts: list[str] = []
        for token in tokens:
            if re.fullmatch(r"\+?[A-Za-z_][A-Za-z0-9_]*", token):
                parts.append(f"%{{{token}}}")
            else:
                parts.append(token)
        return parts

    @override
    def create_log_router_config(
        self, context: LogRouterConfigContext
    ) -> RenderedConfigFile:
        rendered = self.template_provider.render(
            "logstash_conf.j2", context.model_dump()
        )
        data = rendered.encode()
        return RenderedConfigFile(
            filename=f"router_{context.project_id}.yml", content=data
        )

    @override
    def create_agent_set_up_script(
        self, context: AgentProvisioningContext
    ) -> RenderedConfigFile:

        # 플랫폼별 템플릿 선택
        if context.platform == PlatformType.WINDOWS:
            template_name = "setup-agent.bat.j2"
        elif context.platform == PlatformType.LINUX:
            template_name = "setup-agent.sh.j2"
        else:
            raise ValueError(f"Unsupported platform: {context.platform}")

        # 템플릿 렌더링
        rendered = self.template_provider.render(template_name, context.model_dump())

        rendered = rendered.replace("\n", "\r\n")

        # 플랫폼별 인코딩
        if context.platform == PlatformType.WINDOWS:
            data = rendered.encode("cp949", errors="replace")
        else:
            # Linux 등은 UTF-8
            data = rendered.encode("utf-8")

        return RenderedConfigFile(filename=context.script_name, content=data)
