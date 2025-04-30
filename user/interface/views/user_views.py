import uuid
from dataclasses import dataclass

import arrow
from django.http import HttpRequest
from pydantic import BaseModel, Field
from rest_framework import status
from rest_framework.views import APIView

from common.interface.response import ErrorResponse, success_response
from common.interface.validators import validate_query_params
from common.response_msg import LoginMessage
from user.domain.user import OAuthType, User
from user.domain.user_role import UserRole
from user.domain.user_token import UserTokenPayload, UserTokenType
from user.interface.validator.user_token_validator import validate_token
from user.service.oauth.i_oauth_provider import IOAuthProvider
from user.service.oauth.oauth_factory import OauthFactory
from user.service.user_service import UserService
from drf_spectacular.utils import extend_schema, OpenApiResponse

from util.pydantic_serializer import PydanticToDjangoSerializer

class OAuthLoginView(APIView):
    @dataclass
    
    class AuthCode(BaseModel):
        code: str = Field(min_length=32)

    def __init__(self):
        self.oauth_factory = OauthFactory()
        self.user_service = UserService()

    @extend_schema(
        summary="OAuth 로그인 엔드포인트",
        description="code 쿼리 파라미터를 사용하여 OAuth 인증을 진행하고, 회원가입 또는 로그인 후 access/refresh 토큰을 반환합니다.",
        parameters=[
            PydanticToDjangoSerializer.convert(AuthCode)
        ],
        responses={
            200: OpenApiResponse(
                description="로그인 성공 시 access/refresh 토큰 반환",
                response={
                    "type": "object",
                    "properties": {
                        "access": {
                            "type": "string",
                            "description": "액세스 토큰 (JWT)"
                        },
                        "refresh": {
                            "type": "string",
                            "description": "리프레시 토큰 (JWT)"
                        }
                    },
                    "required": ["access", "refresh"]
                }
            ),
            400: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(ErrorResponse),
                description="code 누락 등 파라미터 오류"
            ),
            403: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(ErrorResponse),
                description="인증 실패 혹은 권한 없음"
            ),
            503: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(ErrorResponse),
                description="서버 오류"
            ),
        }
    )
    @validate_query_params(AuthCode)
    def get(self, request, auth_server: str, params: AuthCode):
        auth_server = OAuthType(auth_server)
        oauth_provider_vo: IOAuthProvider = self.oauth_factory.create(auth_server)
        token = oauth_provider_vo.get_oauth_token(oauth_code=params.code)
        oauth_user_vo = oauth_provider_vo.get_oauth_user(access_token=token)

        user = self.user_service.get_user_from_oauth_user(oauth_user=oauth_user_vo)

        if user is None:
            now = arrow.now().isoformat()
            user = self.user_service.create_user(
                User(
                    id=str(uuid.uuid4()),
                    name=oauth_user_vo.name,
                    email=oauth_user_vo.email,
                    mobile_no=oauth_user_vo.mobile_no,
                    oauth_type=auth_server,
                    oauth_id=oauth_user_vo.id,
                    tos_agreed=False,
                    created_at=now,
                    updated_at=now,
                )
            )

        token_dict = self.user_service.create_user_token(user_id=user.id)
        return success_response(status=status.HTTP_200_OK, data=token_dict, message=LoginMessage.LOGIN_SUCCESS)


class UserView(APIView):
    pass


class RefreshTokenView(APIView):
    def __init__(self):
        self.user_service = UserService()

    @extend_schema(
        summary="Access 토큰 재발급",
        description="Refresh 토큰을 기반으로 새로운 Access 토큰을 발급합니다.",
        responses={
            200: OpenApiResponse(
                description="access 토큰 재발급 성공",
                response={
                    "type": "object",
                    "properties": {
                        "access": {
                            "type": "string",
                            "description": "새로 발급된 access JWT"
                        }
                    },
                    "required": ["access"]
                }
            ),
            403: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(ErrorResponse),
                description="Refresh 토큰 만료 혹은 유효하지 않음"
            ),
            503: OpenApiResponse(
                response=PydanticToDjangoSerializer.convert(ErrorResponse),
                description="서버 오류"
            ),
        }
    )
    @validate_token(
        roles=[UserRole.USER, UserRole.ADMIN], validate_type=UserTokenType.REFRESH
    )
    def get(
        self,
        request: HttpRequest,
        token_payload: UserTokenPayload,
    ):
        if token_payload.admin_id is not None:
            user_id = token_payload.admin_id
        elif token_payload.user_id is not None:
            user_id = token_payload.user_id

        token: dict = self.user_service.create_access_token(user_id=user_id)

        return success_response(status=status.HTTP_200_OK, data=token)
