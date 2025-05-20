from enum import StrEnum
from pydantic import BaseModel, model_validator


class PlatformType(StrEnum):
    WINDOWS = "windows"
    LINUX = "linux"
    
class AgentProvisioningContext(BaseModel):
    base_static_url: str
    collector_config_url: str
    router_config_url: str

    filebeat_dir: str = "filebeat"
    logstash_dir: str = "logstash-9.0.1"

    script_name: str = "setup-agent.bat"
    timestamp: int | None = None
    platform: PlatformType = PlatformType.WINDOWS
