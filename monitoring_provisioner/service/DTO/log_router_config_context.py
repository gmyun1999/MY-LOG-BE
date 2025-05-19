from dataclasses import dataclass


@dataclass
class LogRouterConfigContext:
    """
    router 설정을 렌더링할 때
    필요한 모든 파라미터를 모아놓은 DTO.
    """
    exchange: str 
    exchange_type: str
    key: str
    beats_port: int = 5044
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"
    persistent: bool = True
    heartbeat: int = 30