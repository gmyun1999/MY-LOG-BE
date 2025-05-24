from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# 1) Dashboard 응답용 Pydantic 모델
class PublicDashboardResponse(BaseModel):
    id: str
    uid: str
    public_url: str


# 2) MonitoringProjectWithDashboardDto 응답용 Pydantic 모델
class MonitoringProjectWithPublicDashboardResponse(BaseModel):
    id: str
    user_id: str
    name: str
    project_type: str
    status: str
    service_account_id: Optional[str] = None
    description: Optional[str] = None
    user_folder_id: Optional[str] = None
    dashboard: str | None = None
    public_dashboard: PublicDashboardResponse | None = None


class APIResponse(BaseModel):
    data: MonitoringProjectWithPublicDashboardResponse
    message: str


class PagedProjectsResponse(BaseModel):
    items: List[MonitoringProjectWithPublicDashboardResponse]
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
    has_previous: bool
    has_next: bool


class APIResponseList(BaseModel):
    data: PagedProjectsResponse
    message: str
