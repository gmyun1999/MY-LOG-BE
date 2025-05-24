from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from pydantic import BaseModel, Field
from rest_framework import status
from rest_framework.views import APIView

from common.interface.response import ErrorResponse, success_response
from common.interface.validators import validate_query_params
from common.service.paging import Paginator
from monitoring.interface.DTO.responseDTO import (
    APIResponseList,
    MonitoringProjectWithDashboardResponse,
    PagedProjectsResponse,
)
from monitoring.service.monitoring_project_service import MonitoringProjectService
from user.domain.user_role import UserRole
from user.domain.user_token import UserTokenPayload, UserTokenType
from user.interface.validator.user_token_validator import validate_token
from user.service.user_service import UserService
from util.pydantic_serializer import PydanticToDjangoSerializer


class MyProjectsQueryParams(BaseModel):
    page: int = Field(1, ge=1, description="페이지 번호")
    page_size: int = Field(
        10,
        ge=1,
        le=Paginator.MAX_PAGE_SIZE,
        description=f"페이지 크기 (1~{Paginator.MAX_PAGE_SIZE})",
    )


class MyMonitoringProjectsView(APIView):
    def __init__(self):
        self.project_service = MonitoringProjectService()

    @extend_schema(
        summary="내 모든 모니터링 프로젝트 상세 조회",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="페이지 번호 (기본:1)",
                required=False,
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description=f"페이지 크기 (기본:10, 최대:{Paginator.MAX_PAGE_SIZE})",
                required=False,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(APIResponseList),
                description="페이징된 프로젝트 리스트",
            ),
            403: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(ErrorResponse)
            ),
            503: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(ErrorResponse)
            ),
        },
    )
    @validate_token(
        roles=[UserRole.USER, UserRole.ADMIN],
        validate_type=UserTokenType.ACCESS,
    )
    @validate_query_params(MyProjectsQueryParams)
    def get(
        self,
        request,
        token_payload: UserTokenPayload,
        params: MyProjectsQueryParams,
    ):
        # user 추출
        user = UserService.get_user_from_token_payload(token_payload)

        # 서비스 호출 (paging은 서비스 레이어에서 처리됨)
        paged = self.project_service.get_my_projects_detail(
            user_id=user.id,
            page=params.page,
            page_size=params.page_size,
        )

        # DTO → Pydantic 변환
        items: list[MonitoringProjectWithDashboardResponse] = [
            MonitoringProjectWithDashboardResponse(**dto.to_dict())
            for dto in paged.items
        ]
        payload = APIResponseList(
            data=PagedProjectsResponse(
                items=items,
                total_items=paged.total_items,
                total_pages=paged.total_pages,
                current_page=paged.current_page,
                page_size=paged.page_size,
                has_previous=paged.has_previous,
                has_next=paged.has_next,
            ),
            message="OK",
        )

        return success_response(
            status=status.HTTP_200_OK,
            message=payload.message,
            data=payload.data.model_dump(),
        )
