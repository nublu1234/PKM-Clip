"""
도메인 예외 단위 테스트
"""


from src.domain.exceptions import (
    InfrastructureError,
    InvalidURLError,
    JinaReaderAPIError,
    NetworkError,
    PKMClipError,
    RateLimitExceededError,
    TimeoutError,
)


def test_pkm_clip_error_base() -> None:
    """
    PKMClipError 기본 예외 테스트
    """
    error = PKMClipError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_infrastructure_error_inheritance() -> None:
    """
    InfrastructureError 상속 테스트
    """
    error = InfrastructureError("Test")
    assert isinstance(error, PKMClipError)


def test_jina_reader_api_error_inheritance() -> None:
    """
    JinaReaderAPIError 상속 테스트
    """
    error = JinaReaderAPIError("Test error")
    assert isinstance(error, PKMClipError)
    assert str(error) == "Test error"


def test_invalid_url_error_default_message() -> None:
    """
    InvalidURLError 기본 메시지 테스트
    """
    error = InvalidURLError()
    assert "invalid" in str(error).lower()
    assert isinstance(error, JinaReaderAPIError)


def test_invalid_url_error_custom_message() -> None:
    """
    InvalidURLError 커스텀 메시지 테스트
    """
    custom_message = "Custom error message"
    error = InvalidURLError(custom_message)
    assert str(error) == custom_message


def test_rate_limit_exceeded_error_default_message() -> None:
    """
    RateLimitExceededError 기본 메시지 테스트
    """
    error = RateLimitExceededError()
    assert "rate limit" in str(error).lower()
    assert isinstance(error, JinaReaderAPIError)


def test_rate_limit_exceeded_error_custom_message() -> None:
    """
    RateLimitExceededError 커스텀 메시지 테스트
    """
    custom_message = "Custom rate limit message"
    error = RateLimitExceededError(custom_message)
    assert str(error) == custom_message


def test_timeout_error_default_message() -> None:
    """
    TimeoutError 기본 메시지 테스트
    """
    error = TimeoutError()
    assert "timeout" in str(error).lower()
    assert isinstance(error, JinaReaderAPIError)


def test_timeout_error_custom_message() -> None:
    """
    TimeoutError 커스텀 메시지 테스트
    """
    custom_message = "Custom timeout message"
    error = TimeoutError(custom_message)
    assert str(error) == custom_message


def test_network_error_default_message() -> None:
    """
    NetworkError 기본 메시지 테스트
    """
    error = NetworkError()
    assert "network" in str(error).lower()
    assert isinstance(error, JinaReaderAPIError)


def test_network_error_custom_message() -> None:
    """
    NetworkError 커스텀 메시지 테스트
    """
    custom_message = "Custom network message"
    error = NetworkError(custom_message)
    assert str(error) == custom_message


def test_exception_hierarchy() -> None:
    """
    예외 계층 구조 테스트

    PKMClipError
      └─ InfrastructureError
          └─ JinaReaderAPIError
              ├─ InvalidURLError
              ├─ RateLimitExceededError
              ├─ TimeoutError
              └─ NetworkError
    """
    invalid_url_error = InvalidURLError()
    assert isinstance(invalid_url_error, PKMClipError)

    rate_limit_error = RateLimitExceededError()
    assert isinstance(rate_limit_error, PKMClipError)

    timeout_error = TimeoutError()
    assert isinstance(timeout_error, PKMClipError)

    network_error = NetworkError()
    assert isinstance(network_error, PKMClipError)
