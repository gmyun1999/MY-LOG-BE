from django.forms.models import model_to_dict

from monitoring.domain.i_repo.i_visualization_platform_repo.i_folder_repo import (
    IFolderRepo,
)
from monitoring.domain.visualization_platform.folder import UserFolder
from monitoring.infra.models.visualization_platform_model import UserFolderModel


class FolderRepo(IFolderRepo):
    def save(self, folder: UserFolder) -> None:
        UserFolderModel.objects.update_or_create(
            uid=folder.uid, defaults=folder.to_dict()
        )

    def find_by_uid(self, uid: str) -> UserFolder | None:
        try:
            model = UserFolderModel.objects.get(uid=uid)
            return UserFolder(
                id=model.id,
                uid=model.uid,
                user_id=model.user_id,
                name=model.name,
                org_id=model.org_id,
                created_by_task=model.created_by_task,
            )
        except UserFolderModel.DoesNotExist:
            return None

    def find_by_user_id(self, user_id: str) -> UserFolder | None:
        try:
            model = UserFolderModel.objects.get(user_id=user_id)
            return UserFolder(
                id=model.id,
                uid=model.uid,
                user_id=model.user_id,
                name=model.name,
                org_id=model.org_id,
                created_by_task=model.created_by_task,
            )
        except UserFolderModel.DoesNotExist:
            return None
