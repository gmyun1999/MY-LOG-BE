from typing_extensions import override

from monitoring.domain.i_repo.i_visualization_platform_repo.i_service_account_repo import (
    IServiceAccountRepo,
)
from monitoring.domain.visualization_platform.service_account import ServiceAccount
from monitoring.infra.models.visualization_platform_model import ServiceAccountModel


class ServiceAccountRepo(IServiceAccountRepo):

    @override
    def save(self, account: ServiceAccount) -> None:
        ServiceAccountModel.objects.update_or_create(
            account_id=account.account_id, defaults=account.to_dict()
        )

    @override
    def find_by_account_id(self, account_id: int) -> ServiceAccount | None:
        try:
            model = ServiceAccountModel.objects.get(account_id=account_id)
            return ServiceAccount(
                id=model.id,
                account_id=model.account_id,
                user_id=model.user_id,
                name=model.name,
                is_disabled=model.is_disabled,
                role=model.role,
                token=model.token,
            )
        except ServiceAccountModel.DoesNotExist:
            return None

    @override
    def find_by_user_id(self, user_id: str) -> ServiceAccount | None:
        try:
            model = ServiceAccountModel.objects.get(user_id=user_id)
            return ServiceAccount(
                id=model.id,
                account_id=model.account_id,
                user_id=model.user_id,
                name=model.name,
                is_disabled=model.is_disabled,
                role=model.role,
                token=model.token,
            )
        except ServiceAccountModel.DoesNotExist:
            return None

    @override
    def update_token(self, account_id: int, token: str) -> None:
        ServiceAccountModel.objects.filter(account_id=account_id).update(token=token)
