from monitoring.domain.i_repo.i_visualization_platform_repo.i_folder_permission_repo import (
    IFolderPermissionRepo,
)
from monitoring.domain.visualization_platform.folder import FolderPermission
from monitoring.infra.models.visualization_platform_model import FolderPermissionModel


class FolderPermissionRepo(IFolderPermissionRepo):
    def save(self, permission: FolderPermission) -> None:
        FolderPermissionModel.objects.update_or_create(
            service_account_id=permission.service_account_id,
            folder_uid=permission.folder_uid,
            defaults=permission.to_dict(),
        )
