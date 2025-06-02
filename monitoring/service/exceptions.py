class MonitoringProjectException(Exception):
    """MonitoringProject 관련 기본 예외 클래스."""

    code = "MONITORING_PROJECT_ERROR"

    def __init__(
        self,
        message: str = "MonitoringProject 관련 오류가 발생했습니다.",
        detail: dict = {},
    ):
        super().__init__(message)
        self.detail = detail
        self.message = message


class PermissionException(MonitoringProjectException):
    """user_id 가 소유하지않은 project_id인 경우에 발생하는 예외입니다."""

    code = "NO_AUTHORIZATION"

    def __init__(
        self, message: str = "프로젝트에 대한 권한이 없습니다.", detail: dict = {}
    ):
        super().__init__(message, detail)
        self.detail = detail
        self.message = message


class NotExistException(MonitoringProjectException):
    """없는 리소스에 접근하려고 할 때 발생하는 예외입니다."""

    code = "DOES_NOT_EXIST"

    def __init__(self, message: str = "존재하지않는 리소스입니다", detail: dict = {}):
        super().__init__(message, detail)
        self.detail = detail
        self.message = message


class NotImplementedException(MonitoringProjectException):
    """구현되지않은 기능에 접근하려고 할 때 발생하는 예외입니다."""

    code = "NOT_IMPLEMENTED"

    def __init__(
        self, message: str = "아직 구현되지않은 기능입니다", detail: dict = {}
    ):
        super().__init__(message, detail)
        self.detail = detail
        self.message = message


class AlreadyExistException(MonitoringProjectException):
    """이미 존재하는 리소스에 접근하려고 할 때 발생하는 예외입니다."""

    code = "ALREADY_EXIST"

    def __init__(self, message: str = "이미 존재하는 리소스입니다", detail: dict = {}):
        super().__init__(message, detail)
        self.detail = detail
        self.message = message


# 이미 프로비저닝 중인 리소스id
class AlreadyProvisioningException(MonitoringProjectException):
    """이미 프로비저닝 중인 리소스에 접근하려고 할 때 발생하는 예외입니다."""

    code = "ALREADY_PROVISIONING"

    def __init__(
        self, message: str = "이미 프로비저닝 중인 리소스입니다", detail: dict = {}
    ):
        super().__init__(message, detail)
        self.detail = detail
        self.message = message
