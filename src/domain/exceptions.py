"""
도메인 예외 모듈

PKM-Clip의 모든 예외 타입을 정의합니다.
예외는 계층 구조로 구성하여 적절한 에러 처리를 지원합니다.
"""


class PKMClipError(Exception):
    """
    PKM-Clip의 기본 예외 클래스

    모든 커스텀 예외의 기본 클래스입니다.
    """

    _retryable: bool = True


class InfrastructureError(PKMClipError):
    """
    Infrastructure 레이어 관련 예외

    외부 API, 파일 시스템, 네트워크 등 인프라 관련 문제 발생 시 사용합니다.
    """

    pass


class JinaReaderAPIError(InfrastructureError):
    """
    Jina AI Reader API 관련 예외

    Jina Reader API 호출 실패 시 발생합니다.
    """

    pass


class InvalidURLError(JinaReaderAPIError):
    """
    유효하지 않은 URL 예외

    URL 형식이 올바르지 않거나 지원되지 않는 프로토콜인 경우 발생합니다.
    """

    def __init__(self, message: str = "Provided URL is invalid. Please check URL format.") -> None:
        super().__init__(message)


class RateLimitExceededError(JinaReaderAPIError):
    """
    Rate Limit 초과 예외

    Jina Reader API의 Rate Limit (429 상태 코드) 초과 시 발생합니다.
    """

    def __init__(
        self, message: str = "Jina Reader API rate limit exceeded. Please wait and try again later."
    ) -> None:
        super().__init__(message)


class TimeoutError(JinaReaderAPIError):
    """
    타임아웃 예외

    요청이 설정된 타임아웃 시간 내에 응답하지 않을 때 발생합니다.
    """

    def __init__(self, message: str = "Request timeout. Server took too long to respond.") -> None:
        super().__init__(message)


class NetworkError(JinaReaderAPIError):
    """
    네트워크 오류 예외

    연결 실패, DNS 오류 등 네트워크 관련 문제 발생 시 사용합니다.
    """

    def __init__(self, message: str = "Network error occurred. Check your connection.") -> None:
        super().__init__(message)


class RetryableHTTPStatusError(JinaReaderAPIError):
    """
    재시도 가능한 HTTP 상태 코드 예외

    5xx 서버 오류와 같이 재시도가 가능한 HTTP 오류 발생 시 사용합니다.
    """

    def __init__(self, message: str = "Server error occurred. Retry may succeed.") -> None:
        super().__init__(message)
