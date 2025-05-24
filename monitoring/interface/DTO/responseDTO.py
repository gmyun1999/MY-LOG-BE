from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    id: str
    uid: Optional[str] = None
    title: Optional[str] = None
    folder_uid: Optional[str] = None
    url: Optional[str] = None
    panels: List[Dict[str, Any]] = []
    tags: List[str] = []
    data_sources: List[str] = []


class PublicDashboardResponse(BaseModel):
    id: str
    uid: str
    public_url: str
    project_id: str
    dashboard_id: str


class MonitoringProjectWithBothDashboardsResponse(BaseModel):
    id: str
    user_id: str
    name: str
    project_type: str
    status: str
    service_account_id: Optional[str] = None
    description: Optional[str] = None
    user_folder_id: Optional[str] = None
    dashboard: Optional[DashboardResponse] = None
    public_dashboard: Optional[PublicDashboardResponse] = None


class APIResponse(BaseModel):
    data: MonitoringProjectWithBothDashboardsResponse
    message: str


class PagedProjectsResponse(BaseModel):
    items: List[MonitoringProjectWithBothDashboardsResponse]
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
    has_previous: bool
    has_next: bool


class APIResponseList(BaseModel):
    data: PagedProjectsResponse
    message: str
