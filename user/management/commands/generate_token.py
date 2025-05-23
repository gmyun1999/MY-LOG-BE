from django.core.management.base import BaseCommand

from common.service.token.i_token_manager import ITokenManager
from user.domain.user import OAuthType, User
from user.infra.token.user_token_manager import UserTokenManager
from user.service.user_service import UserService


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        user = User(
            id="7673a900-4f76-4e8b-bd40-18d8136e9a5b",
            name="gyumin",
            email="gyumin@example.com",
            mobile_no="1234567890",
            oauth_type=OAuthType.GOOGLE,
            oauth_id="goodsq-oauth-id",
            tos_agreed=True,
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        user = UserService().create_user(user)
        token_manager: ITokenManager = UserTokenManager()
        user_refresh = token_manager.create_user_refresh_token(user_id=user.id)
        user_access = token_manager.create_user_access_token(user_id=user.id)
        print("user_refresh:")
        print(user_refresh)
        print("")
        print("")
        print("user_access:")
        print(user_access)
