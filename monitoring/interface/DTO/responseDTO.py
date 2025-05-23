from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# 1) Dashboard 응답용 Pydantic 모델
class DashboardResponse(BaseModel):
    id: str
    uid: Optional[str]
    title: Optional[str]
    folder_uid: Optional[str]
    url: Optional[str]
    panels: List[Dict[str, Any]] = []
    tags: List[str] = []
    data_sources: List[str] = []


# 2) MonitoringProjectWithDashboardDto 응답용 Pydantic 모델
class MonitoringProjectWithDashboardResponse(BaseModel):
    id: str
    user_id: str
    name: str
    project_type: str
    status: str
    service_account_id: Optional[str] = None
    description: Optional[str] = None
    user_folder_id: Optional[str] = None
    dashboard: DashboardResponse


class APIResponse(BaseModel):
    data: MonitoringProjectWithDashboardResponse
    message: str


class PagedProjectsResponse(BaseModel):
    items: List[MonitoringProjectWithDashboardResponse]
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
    has_previous: bool
    has_next: bool


class APIResponseList(BaseModel):
    data: PagedProjectsResponse
    message: str
