import token
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

import user
from common.domain import Domain


@dataclass
class Dashboard(Domain):
    """
    시각화 플랫폼의 대시보드
    """

    FIELD_ID = "id"
    FIELD_UID = "uid"
    FIELD_TITLE = "title"
    FIELD_USER_ID = "user_id"
    FIELD_PROJECT_ID = "project_id"
    FIELD_ORG_ID = "org_id"
    FIELD_FOLDER_UID = "folder_uid"
    FIELD_URL = "url"
    FIELD_CONFIG_JSON = "config_json"
    FIELD_PANELS = "panels"
    FIELD_TAGS = "tags"
    FIELD_DATA_SOURCES = "data_sources"

    id: str
    uid: str | None  # 플랫폼 내부에서 사용하는 pk
    title: str | None  # 대시보드 제목
    user_id: str | None  # 우리 서비스 내부에서 사용하는 사용자 ID
    project_id: str | None  # 대시보드가 속한 프로젝트 ID
    org_id: str | None  # 대시보드가 속한 조직 ID
    folder_uid: str | None  # 속해 있는 폴더의 UID
    url: str | None  # 대시보드에 접근하기 위한 URL
    config_json: dict[str, Any] | None = None  # 대시보드에에 사용된 원본 config
    panels: list[dict[str, Any]] = field(default_factory=list)
    #   - panels: 대시보드에 포함된 패널 목록. 각 패널은 dict 형태로 설정 정보 포함
    tags: list[str] = field(default_factory=list)
    #   - tags: 대시보드에 붙여진 태그 목록
    data_sources: list[str] = field(default_factory=list)
    #   - data_sources: 대시보드에서 참조하는 데이터 소스의 이름 목록


@dataclass
class PublicDashboard(Domain):
    """
    퍼블릭 대시보드
    """

    FIELD_ID = "id"
    FIELD_UID = "uid"
    FIELD_DASHBOARD_ID = "dashboard_id"
    FIELD_PUBLIC_URL = "public_url"
    FIELD_PROJECT_ID = "project_id"

    id: str
    uid: str  # 퍼블릭 대시보드의 UID
    project_id: str
    dashboard_id: str  # 연결된 대시보드의 ID
    public_url: str
