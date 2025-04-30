from abc import ABCMeta, abstractmethod


class ITokenManager(metaclass=ABCMeta):
<<<<<<< HEAD
    @abstractmethod
    def create_admin_access_token(self, admin_id: str) -> str:
        pass

    @abstractmethod
    def create_admin_refresh_token(self, admin_id: str) -> str:
        pass

    @abstractmethod
    def create_user_access_token(self, user_id: str) -> str:
        pass

    @abstractmethod
    def create_user_refresh_token(self, user_id: str) -> str:
        pass
=======
    pass
>>>>>>> de5c1f7c2bef64ea8c8bf84a7a103952a0bad448
