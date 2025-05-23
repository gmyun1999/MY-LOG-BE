from common.service.token.i_token_manager import ITokenManager
from user.domain.user import OAuthUser
from user.domain.user import User
from user.domain.user import User as UserVo
from user.domain.user_token import UserTokenPayload
from user.infra.repository.user_repo import UserRepo
from user.infra.token.user_token_manager import UserTokenManager
from user.service.repository.i_user_repo import IUserRepo


class UserService:
    def __init__(self):
        # TODO: DI 적용
        self.user_token_manager: ITokenManager = UserTokenManager()
        self.user_repo: IUserRepo = UserRepo()

    @staticmethod
    def get_user_from_token_payload(token_payload: UserTokenPayload) -> User:
        user_id = (
            token_payload.user_id or token_payload.admin_id or token_payload.guest_id
        )
        if user_id is None:
            raise ValueError("No user/admin/guest ID found in token payload.")

        user_service = UserService()
        user = user_service.get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"User not found for ID: {user_id}")
        return user

    def create_access_token(self, user_id: str) -> dict:
        return {"access": self.user_token_manager.create_user_access_token(user_id)}

    def get_user_by_id(self, user_id: str) -> UserVo | None:
        """
        user_id로 유저를 가져온다.
        """
        user_filter = self.user_repo.Filter(user_id=user_id)
        return self.user_repo.get_user(filter=user_filter)

    def get_user_from_oauth_user(self, oauth_user: OAuthUser) -> UserVo | None:
        oauth_id = oauth_user.id
        oauth_type = oauth_user.oauth_type

        user_filter = self.user_repo.Filter(oauth_id=oauth_id, oauth_type=oauth_type)
        return self.user_repo.get_user(filter=user_filter)

    def create_user(self, user: UserVo) -> UserVo:
        """
        그냥 user 만든다음에 db에 밀어넣으면됨.
        """
        return self.user_repo.create(user_vo=user)

    def create_user_token(self, user_id: str) -> dict[str, str]:
        """
        access, refresh 모두 만들어서 돌려줌.
        return :  {
            access: access_token,
            refresh: refresh_token
        }
        """
        return {
            "access": self.user_token_manager.create_user_access_token(user_id),
            "refresh": self.user_token_manager.create_user_refresh_token(user_id),
        }
