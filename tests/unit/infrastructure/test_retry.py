"""
재시도 로직 단위 테스트
"""

import asyncio

import pytest

from src.domain.exceptions import PKMClipError
from src.infrastructure.retry import retry_with_backoff


class RetryableError(Exception):
    """재시도 가능한 테스트 예외"""

    pass


class NonRetryableError(Exception):
    """재시도 불가능한 테스트 예외"""

    pass


class RetryablePKMClipError(PKMClipError):
    """재시도 가능한 PKMClipError 예외"""

    _retryable = True


@pytest.mark.asyncio
async def test_retry_with_backoff_success_on_first_try() -> None:
    """
    첫 시도에서 성공하는 경우 테스트
    """
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=0.1)
    async def always_succeed() -> str:
        nonlocal call_count
        call_count += 1
        return "success"

    result = await always_succeed()
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_with_backoff_success_on_second_try() -> None:
    """
    두 번째 시도에서 성공하는 경우 테스트
    """
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=0.1)
    async def fail_once_then_succeed() -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RetryableError("First attempt failed")
        return "success"

    result = await fail_once_then_succeed()
    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_with_backoff_max_retries_exceeded() -> None:
    """
    최대 재시도 횟수 초과 시 예외 발생 테스트
    """
    call_count = 0

    @retry_with_backoff(max_retries=2, initial_delay=0.01)
    async def always_fail() -> str:
        nonlocal call_count
        call_count += 1
        raise RetryableError("Always fails")

    with pytest.raises(RetryableError):
        await always_fail()

    assert call_count == 3  # 초기 1회 + 재시도 2회


@pytest.mark.asyncio
async def test_retry_with_backoff_exponential_delay() -> None:
    """
    지수 백오프 대기 시간 테스트
    """
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=0.1, multiplier=2.0)
    async def fail_twice_with_delay() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RetryableError("Fail")
        return "success"

    start_time = asyncio.get_event_loop().time()
    await fail_twice_with_delay()
    elapsed = asyncio.get_event_loop().time() - start_time

    # 초기 0.1 + 두 번째 0.2 + 세 번째 0.4 = 최소 0.7초
    assert elapsed >= 0.3


@pytest.mark.asyncio
async def test_retry_with_backoff_custom_retryable_exceptions() -> None:
    """
    커스텀 재시도 가능 예외 테스트
    """
    call_count = 0

    @retry_with_backoff(
        max_retries=2, initial_delay=0.01, retryable_exceptions=(RetryableError,)
    )
    async def fail_with_retryable() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise RetryableError("Fail")
        return "success"

    result = await fail_with_retryable()
    assert result == "success"


@pytest.mark.asyncio
async def test_retry_with_backoff_non_retryable_exception() -> None:
    """
    재시도 불가능한 예외 즉시 발생 테스트
    """
    call_count = 0

    @retry_with_backoff(
        max_retries=3, initial_delay=0.01, retryable_exceptions=(RetryableError,)
    )
    async def fail_with_non_retryable() -> str:
        nonlocal call_count
        call_count += 1
        raise NonRetryableError("Non-retryable error")

    with pytest.raises(NonRetryableError):
        await fail_with_non_retryable()

    assert call_count == 1  # 재시도 없이 즉시 실패


@pytest.mark.asyncio
async def test_retry_with_backoff_pkm_clip_error_non_retryable() -> None:
    """
    PKMClipError 자식 클래스가 _retryable=False 인 경우 재시도 안 함 테스트
    """
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=0.01)
    async def fail_with_pkm_clip_error() -> str:
        nonlocal call_count
        call_count += 1
        raise NonRetryablePKMClipError("Non-retryable PKM error")

    with pytest.raises(NonRetryablePKMClipError):
        await fail_with_pkm_clip_error()

    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_with_backoff_pkm_clip_error_retryable() -> None:
    """
    PKMClipError 자식 클래스가 _retryable=True 인 경우 재시도 테스트
    """
    call_count = 0

    @retry_with_backoff(max_retries=2, initial_delay=0.01)
    async def fail_then_succeed_with_pkm_error() -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RetryablePKMClipError("Retryable PKM error")
        return "success"

    result = await fail_then_succeed_with_pkm_error()
    assert result == "success"
    assert call_count == 2


class NonRetryablePKMClipError(PKMClipError):
    """재시도 불가능한 PKMClipError 예외 (기본값)"""

    _retryable = False

    pass


@pytest.mark.asyncio
async def test_retry_with_backoff_preserves_exception() -> None:
    """
    원본 예외 보존 테스트
    """
    original_error = RetryableError("Original error")

    @retry_with_backoff(max_retries=0, initial_delay=0.01)
    async def raise_original_error() -> str:
        raise original_error

    with pytest.raises(RetryableError) as exc_info:
        await raise_original_error()

    assert exc_info.value is original_error


@pytest.mark.asyncio
async def test_retry_with_backoff_zero_retries() -> None:
    """
    재시도 횟수 0 설정 테스트 (초기 시도만)
    """
    call_count = 0

    @retry_with_backoff(max_retries=0, initial_delay=0.01)
    async def succeed_immediately() -> str:
        nonlocal call_count
        call_count += 1
        return "success"

    result = await succeed_immediately()
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_with_backoff_delay_multiplier_one() -> None:
    """
    배수 1.0 설정 시 일정 지연 테스트
    """
    call_count = 0

    @retry_with_backoff(max_retries=2, initial_delay=0.1, multiplier=1.0)
    async def fail_twice() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RetryableError("Fail")
        return "success"

    start_time = asyncio.get_event_loop().time()
    await fail_twice()
    elapsed = asyncio.get_event_loop().time() - start_time

    # 0.1 + 0.1 + 0.1 = 최소 0.3초
    assert elapsed >= 0.2
