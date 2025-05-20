from typing import Any
from typing_extensions import override
from monitoring_provisioner.domain.log_agent.agent_provision_context import AgentProvisioningContext, PlatformType
from monitoring_provisioner.domain.log_agent.log_collector import LogInputType, LogCollectorConfigContext
from monitoring_provisioner.domain.log_agent.log_router import LogRouterConfigContext
from monitoring_provisioner.domain.log_agent.rendered_config import RenderedConfigFile
from monitoring_provisioner.infra.jinja2.jinja2_template_renderer import Jinja2TemplateRenderer
from monitoring_provisioner.service.i_log_agent.i_log_agent_provider import ILogAgentProvider
from monitoring_provisioner.service.i_template_renderer.template_renderer import ITemplateRenderer
import re

class FileBeats(ILogAgentProvider):
    """
    LogCollector 및 Router 설정, Bootstrap 스크립트를 Jinja2 템플릿으로 생성.
    """
    def __init__(self):
        # TODO: DI
        self.template_provider: ITemplateRenderer = Jinja2TemplateRenderer()

    @override
    def create_log_collector_config(
        self,
        context: LogCollectorConfigContext
    ) -> RenderedConfigFile:

        ctx: dict[str, Any] = context.model_dump()

        # []. <>, | 등 구분자 jinja2에서 처리가능하게 변경
        raw: list[str] = ctx.get("custom_plain_fields", [])
        parts: list[str] = []
        for token in raw:
            # 접두·키·접미 분리
            m = re.match(r'^(\W*?)([A-Za-z][A-Za-z0-9_]*)(\W*?)$', token)
            if m:
                prefix, key, suffix = m.groups()
                parts.append(f"{prefix}%{{{key}->}}{suffix}")
            else:
                parts.append(token)

        ctx["tokenizer_parts"] = parts

        # 템플릿 렌더링
        if context.input_type is LogInputType.PLAIN:
            tpl_name = "filebeat_plain_text.j2"
        else:
            tpl_name = "filebeat_json.j2"

        rendered = self.template_provider.render(
            tpl_name,
            ctx
        )
        data = rendered.encode()

        return RenderedConfigFile(
            filename=f"collector_{context.project_id}.yml",
            content=data
        )
        
    @override
    def create_log_router_config(
        self,
        context: LogRouterConfigContext
    ) -> RenderedConfigFile:
        rendered = self.template_provider.render(
            "logstash_conf.j2",
            context.model_dump()
        )
        data = rendered.encode()
        return RenderedConfigFile(
            filename=f"router_{context.project_id}.yml",
            content=data
        )

    @override
    def create_agent_set_up_script(
        self,
        context: AgentProvisioningContext
    ) -> RenderedConfigFile:

        # 플랫폼별 템플릿 선택
        if context.platform == PlatformType.WINDOWS:
            template_name = "setup-agent.bat.j2"
        elif context.platform == PlatformType.LINUX:
            template_name = "setup-agent.sh.j2"
        else:
            raise ValueError(f"Unsupported platform: {context.platform}")

        # 템플릿 렌더링
        rendered = self.template_provider.render(
            template_name,
            context.model_dump()
        )

        rendered = rendered.replace("\n", "\r\n")

        # 플랫폼별 인코딩
        if context.platform == PlatformType.WINDOWS:
            data = rendered.encode("cp949", errors="replace")
        else:
            # Linux 등은 UTF-8
            data = rendered.encode("utf-8")

        return RenderedConfigFile(
            filename=context.script_name,
            content=data
        )