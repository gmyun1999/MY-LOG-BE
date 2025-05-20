from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


class LogRouterConfigContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    FIELD_PROJECT_ID: str = "project_id"
    FIELD_BEATS_PORT: str = "beats_port"
    FIELD_MQ_HOST: str = "mq_host"
    FIELD_MQ_PORT: str = "mq_port"
    FIELD_MQ_USER: str = "mq_user"
    FIELD_MQ_PASSWORD: str = "mq_password"
    FIELD_MQ_VHOST: str = "mq_vhost"
    FIELD_MQ_EXCHANGE: str = "mq_exchange"
    FIELD_MQ_EXCHANGE_TYPE: str = "mq_exchange_type"
    FIELD_MQ_ROUTING_KEY: str = "mq_routing_key"
    FIELD_MQ_PERSISTENT: str = "mq_persistent"
    FIELD_MQ_HEARTBEAT: str = "mq_heartbeat"
    
    project_id: str
    beats_port: int = 5044

    mq_host: str
    mq_port: int
    mq_user: str
    mq_password: str
    mq_vhost: str
    mq_exchange: str
    mq_exchange_type: str
    mq_routing_key: str
    
    mq_persistent: bool = True
    mq_heartbeat: int = 30

