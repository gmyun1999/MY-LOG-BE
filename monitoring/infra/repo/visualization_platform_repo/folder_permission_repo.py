from monitoring.domain.i_repo.i_visualization_platform_repo.i_folder_permission_repo import (
    IFolderPermissionRepo,
)
from monitoring.domain.visualization_platform.folder import (
    FolderPermission,
    FolderPermissionLevel,
)
from monitoring.infra.models.visualization_platform_model import FolderPermissionModel


class FolderPermissionRepo(IFolderPermissionRepo):
    def save(self, permission: FolderPermission) -> None:
        FolderPermissionModel.objects.update_or_create(
            service_account_id=permission.service_account_id,
            folder_uid=permission.folder_uid,
            defaults=permission.to_dict(),
        )

    def find_by_service_account_id(
        self, service_account_id: str
    ) -> FolderPermission | None:
        try:
            perm_model = FolderPermissionModel.objects.get(
                service_account_id=service_account_id
            )
            return FolderPermission(
                id=perm_model.id,
                service_account_id=perm_model.service_account_id,
                folder_uid=perm_model.folder_uid,
                permission=FolderPermissionLevel(perm_model.permission),
            )
        except FolderPermissionModel.DoesNotExist:
            return None
