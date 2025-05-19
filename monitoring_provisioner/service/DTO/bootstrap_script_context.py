from dataclasses import dataclass


@dataclass
class BootstrapScriptContext:
    """
    부트스트랩 스크립트(bootstrap.sh.j2 등)를 렌더링할 때
    필요한 모든 파라미터를 모아놓은 DTO.
    """
    base_zip_url: str                 # Filebeat 패키지 ZIP URL
    collector_config_url: str         # 방금 업로드된 collector.yml URL
    router_config_url: str            # 방금 업로드된 router.yml URL
    filebeat_dir: str = "filebeat"    # 풀고 실행할 디렉터리명
    script_name: str = "bootstrap.sh" # 생성될 스크립트 파일명
    aws_region: str | None= None            # (필요시) AWS CLI region
    timestamp: int | None= None             # (선택) 버전 관리용 타임스탬프