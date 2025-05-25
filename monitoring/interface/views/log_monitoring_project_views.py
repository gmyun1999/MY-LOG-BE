import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from pydantic import BaseModel, Field
from rest_framework import status
from rest_framework.views import APIView

from common.interface.response import ErrorResponse, error_response, success_response
from common.interface.validators import validate_body
from monitoring.domain.log_agent.agent_provision_context import PlatformType
from monitoring.domain.log_agent.log_collector import (
    FilterCondition,
    JsonFieldMapping,
    LogCollectorConfigContext,
    LogInputType,
)
from monitoring.domain.log_agent.log_router import LogRouterConfigContext
from monitoring.service.exceptions import MonitoringProjectException
from monitoring.service.monitoring_project_service import MonitoringProjectService
from user.domain.user import User
from user.domain.user_role import UserRole
from user.domain.user_token import UserTokenPayload, UserTokenType
from user.interface.validator.user_token_validator import validate_token
from user.service.user_service import UserService
from util.pydantic_serializer import PydanticToDjangoSerializer


class LogMonitoringProjectStep1View(APIView):

    class Step1Request(BaseModel):
        log_paths: list[str]
        project_name: str
        project_description: str

        multiline_pattern: str | None = None  # plain 로그의 멀티라인 패턴
        custom_plain_fields: list[str] = []  # plain 로그의  필드

        timestamp_field: str | None = None  # json 로그의 타임스템프 필드
        timestamp_json_path: str | None = None  # json 로그의 타임스탬프 필드 경로
        log_level: str | None = None  # json 로그의 로그 레벨 필드
        log_level_json_path: str | None = None  # json 로그의 로그 레벨 필드 경로
        custom_json_fields: list[JsonFieldMapping] = []
        filters: list[FilterCondition] = []
        platform: PlatformType = PlatformType.WINDOWS

    def __init__(self):
        self.project_service = MonitoringProjectService()

    @extend_schema(
        summary="로그 프로젝트 생성 (1단계)",
        request=PydanticToDjangoSerializer.convert(Step1Request),
        responses={
            200: OpenApiResponse(
                description="프로젝트 생성 및 에이전트 다운로드 경로 반환",
                response={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "set_up_script_url": {"type": "string"},
                    },
                    "required": ["project_id", "set_up_script_url"],
                },
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
        roles=[UserRole.USER, UserRole.USER], validate_type=UserTokenType.ACCESS
    )
    @validate_body(Step1Request)
    def post(self, request, token_payload: UserTokenPayload, body: Step1Request):
        try:
            user = UserService.get_user_from_token_payload(token_payload)
        except ValueError as e:
            return error_response(status=status.HTTP_403_FORBIDDEN, message=str(e))
        # TODO: hash테이블 적용해서 알맞은 큐에 집어넣는 로직 추가해야함
        project_id = str(uuid.uuid4())

        collector_ctx = LogCollectorConfigContext(
            project_id=project_id,
            hosts=["127.0.0.1:5044"],
            log_paths=body.log_paths,
            # input_type=(
            #     LogInputType.JSON if body.timestamp_field else LogInputType.PLAIN
            # ),
            input_type=LogInputType.PLAIN,  # test용
            multiline_pattern=body.multiline_pattern,
            custom_plain_fields=body.custom_plain_fields,
            timestamp_field=None,  # test용
            # timestamp_field=body.timestamp_field,
            timestamp_json_path=body.timestamp_json_path,
            log_level=None,  # test용
            # log_level=body.log_level,
            log_level_json_path=body.log_level_json_path,
            custom_json_fields=body.custom_json_fields,
            filters=body.filters,
        )

        router_ctx = LogRouterConfigContext(
            project_id=project_id,
            beats_port=5044,
            mq_host="127.0.0.1",
            mq_port=5672,
            mq_user="guest",
            mq_password="guest",
            mq_vhost="/",
            mq_exchange="app_logs_exchange",
            mq_exchange_type="direct",
            mq_routing_key="logs_1",
            mq_persistent=True,
            mq_heartbeat=30,
        )
        try:
            user = UserService.get_user_from_token_payload(token_payload)
        except ValueError as e:
            return error_response(status=status.HTTP_403_FORBIDDEN, message=str(e))

        project = self.project_service.start_log_project_step1(
            user=user,
            project_name=body.project_name,
            project_description=body.project_description,
            log_collector_ctx=collector_ctx,
            log_router_ctx=router_ctx,
            platform=body.platform,
        )

        return success_response(
            status=status.HTTP_200_OK,
            message="OK",
            data={
                "project_id": project.id,
                "set_up_script_url": project.agent_context.set_up_script_url,
            },
        )


class LogMonitoringProjectStep2View(APIView):
    class Step2Request(BaseModel):
        project_id: str = Field(min_length=32)

    def __init__(self):
        self.project_service = MonitoringProjectService()

    @extend_schema(
        summary="로그 프로젝트 설정 완료 처리 (2단계)",
        request=PydanticToDjangoSerializer.convert(Step2Request),
        responses={
            200: OpenApiResponse(description="OK"),
            403: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(ErrorResponse)
            ),
            503: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(ErrorResponse)
            ),
        },
    )
    @validate_token(
        roles=[UserRole.USER, UserRole.USER], validate_type=UserTokenType.ACCESS
    )
    @validate_body(Step2Request)
    def post(self, request, token_payload: UserTokenPayload, body: Step2Request):
        try:
            user = UserService.get_user_from_token_payload(token_payload)
        except ValueError as e:
            return error_response(status=status.HTTP_403_FORBIDDEN, message=str(e))
        try:
            self.project_service.start_log_project_step2(
                user=user,
                project_id=body.project_id,
            )

            return success_response(status=status.HTTP_200_OK, message="OK", data={})
        except MonitoringProjectException as e:
            return error_response(
                message=e.message,
                detail=e.detail,
            )
