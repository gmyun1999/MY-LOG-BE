from django.core.management.base import BaseCommand
import boto3
from requests_aws4auth import AWS4Auth
import requests

class Command(BaseCommand):
    help = "오픈소스 검색 api에 연결 테스트"

    def add_arguments(self, parser):
        parser.add_argument(
            "--endpoint",
            required=True,
            help="OpenSearch 엔드포인트 (호스트만, https:// 제외)"
        )
        parser.add_argument(
            "--region",
            default="ap-northeast-2",
            help="AWS 리전"
        )

    def handle(self, *args, **options):
        endpoint = options["endpoint"]
        region = options["region"]
        service = "es"

        # Boto3 세션에서 자격증명 획득 :contentReference[oaicite:0]{index=0}
        session = boto3.Session()
        creds = session.get_credentials().get_frozen_credentials()

        # SigV4 서명 객체 생성 :contentReference[oaicite:1]{index=1}
        awsauth = AWS4Auth(
            creds.access_key,
            creds.secret_key,
            region,
            service,
            session_token=creds.token
        )

        url = f"https://{endpoint}/"
        self.stdout.write(f"→ {url} 에 요청 중…")
        resp = requests.get(url, auth=awsauth)
        self.stdout.write(f"Status Code: {resp.status_code}")
        self.stdout.write(resp.text)
