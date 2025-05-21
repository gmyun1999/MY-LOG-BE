from dataclasses import dataclass

from common.domain import Domain


@dataclass
class ServiceAccount(Domain):
    id: str
    account_id: int
    user_id: str
    name: str
    is_disabled: bool
    role: str
    token: str | None = None
