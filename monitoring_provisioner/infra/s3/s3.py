from typing_extensions import override
import boto3
from botocore.exceptions import ClientError
from config import settings
from monitoring_provisioner.service.i_storage.i_storage_provider import IStorageProvider

class S3StorageProvider(IStorageProvider):
    def __init__(self):
      
        self.bucket = settings.S3_BUCKET_NAME
        self.client = boto3.client('s3', region_name=settings.S3_AWS_REGION)
        
    @override
    def upload(
        self,
        data: bytes,
        key: str,
        content_type: str = 'application/octet-stream'
    ) -> str:
        """
        바이트 데이터를 S3에 업로드하고 public-read ACL을 부여한 뒤,
        https://{bucket}.s3.amazonaws.com/{key} 형태의 URL을 반환

        :param data: 업로드할 바이트 데이터
        :param key: 버킷 내 저장 경로
        :param content_type: 객체의 MIME 타입
        :return: 업로드된 객체의 public URL
        """
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                ACL='public-read'
            )
        except ClientError as e:
            raise RuntimeError(f"S3 upload failed: {e}")

        return f"https://{self.bucket}.s3.amazonaws.com/{key}"