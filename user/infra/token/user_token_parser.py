from typing import Any

import jwt
from django.http.request import HttpHeaders

from common import response_msg
from common.constant import RequestHeader
from common.service.token.i_token_parser import ITokenParser
from config.settings import JWT_SECRET
from user.domain.user_token import UserTokenPayload


class UserTokenParser(ITokenParser):
    JWT_ALGORITHM = "HS512"
    JWT_SECRET = JWT_SECRET

    def _validate_token(
        self, token: str, validate_type: str, allowed_roles: list[str]
    ) -> tuple[UserTokenPayload | None, str]:
        if not token:
            return None, response_msg.TokenMessage.NOT_FOUND.value

        try:
            payload = self.decode_token(token)

            if payload[UserTokenPayload.FIELD_TYPE] != validate_type:
                return None, response_msg.TokenMessage.WRONG_TYPE.value

            if not payload[UserTokenPayload.FIELD_ROLE] in allowed_roles:
                return None, response_msg.TokenMessage.ROLE_NO_PERMISSION.value

            user_token_payload_vo = UserTokenPayload.from_dict(payload)
            return user_token_payload_vo, response_msg.TokenMessage.VALID.value

        except jwt.ExpiredSignatureError:
            return None, response_msg.TokenMessage.EXPIRED.value

    def check_token(
        self, token: str, allowed_roles: list[str], validate_type: str
    ) -> tuple[UserTokenPayload | None, str]:
        payload_vo, msg = self._validate_token(
            token=token, validate_type=validate_type, allowed_roles=allowed_roles
        )

        if not payload_vo:
            return None, msg

        return payload_vo, msg

    def decode_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self.JWT_SECRET, algorithms=[self.JWT_ALGORITHM])

    def get_token(self, http_header: HttpHeaders) -> str:
        authorization = http_header.get(RequestHeader.HEADER_AUTHORIZATION, "")
        return authorization.replace(RequestHeader.HEADER_PREFIX_BEARER, "")
