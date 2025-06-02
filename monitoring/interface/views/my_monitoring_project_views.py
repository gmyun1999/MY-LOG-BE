from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.views import APIView

from common.interface.response import ErrorResponse, error_response, success_response
from monitoring.domain.monitoring_project import MonitoringProjectWithBothDashboardsDto
from monitoring.interface.DTO.responseDTO import APIResponseList
from monitoring.service.exceptions import MonitoringProjectException
from monitoring.service.monitoring_project_service import MonitoringProjectService
from user.domain.user_role import UserRole
from user.domain.user_token import UserTokenPayload, UserTokenType
from user.interface.validator.user_token_validator import validate_token
from user.service.user_service import UserService
from util.pydantic_serializer import PydanticToDjangoSerializer


class MyMonitoringProjectView(APIView):
    def __init__(self):
        self.project_service = MonitoringProjectService()

    @extend_schema(
        summary="내 모니터링 프로젝트 가져오기",
        parameters=[
            OpenApiParameter(
                name="project_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="프로젝트 UUID",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(APIResponseList),
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
    def get(self, request, project_id: str, token_payload: UserTokenPayload):
        try:
            user = UserService.get_user_from_token_payload(token_payload)
        except ValueError as e:
            return error_response(
                status=status.HTTP_403_FORBIDDEN,
                message=str(e),
            )

        try:
            self.project_service.check_permission(user, project_id)

            dto: MonitoringProjectWithBothDashboardsDto = (
                self.project_service.get_project_detail(
                    project_id=project_id,
                )
            )

            data = dto.to_dict()
            return success_response(
                status=status.HTTP_200_OK,
                message="OK",
                data=data,
            )

        except MonitoringProjectException as e:
            return error_response(
                message=e.message,
                detail=e.detail,
            )
