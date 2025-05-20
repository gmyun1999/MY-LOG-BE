from dataclasses import dataclass, field
from typing import Dict, List, Any
from common.domain import Domain


@dataclass
class GrafanaDashboard(Domain):
    """
    그라파나 대시보드 도메인 객체
    """
    FIELD_ID = "id"
    FIELD_UID = "uid"
    FIELD_TITLE = "title"
    FIELD_USER_ID = "user_id"
    FIELD_FOLDER_UID = "folder_uid"
    FIELD_URL = "url"
    FIELD_PANELS = "panels"
    FIELD_TAGS = "tags"
    FIELD_DATA_SOURCES = "data_sources"
    
    # 실제 인스턴스 속성
    id: str = None                         # 대시보드 고유 ID (숫자형이 문자열로 올 수 있음)
    uid: str = None                        # Grafana 내부에서 사용하는 유니크 식별자
    title: str = None                      # 대시보드 제목
    user_id: str = None                    # 소유자(사용자) ID
    folder_uid: str = None                 # 속해 있는 폴더의 UID
    url: str = None                        # 대시보드에 접근하기 위한 URL
    panels: List[Dict[str, Any]] = field(default_factory=list)
    #   - panels: 대시보드에 포함된 패널 목록. 각 패널은 dict 형태로 설정 정보 포함
    tags: List[str] = field(default_factory=list)
    #   - tags: 대시보드에 붙여진 태그 목록
    data_sources: List[str] = field(default_factory=list)
    #   - data_sources: 대시보드에서 참조하는 데이터 소스의 이름 목록