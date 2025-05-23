from dataclasses import dataclass
from enum import IntEnum

import user
from common.domain import Domain


class FolderPermissionLevel(IntEnum):
    VIEW = 1
    EDIT = 2
    ADMIN = 4


@dataclass
class FolderPermission(Domain):
    id: str
    service_account_id: str
    folder_uid: str
    permission: FolderPermissionLevel


@dataclass
class UserFolder(Domain):
    id: str
    uid: str  # Grafana의 folder UID
    user_id: str
    name: str
    org_id: str | None = None
    created_by_task: str | None = None
