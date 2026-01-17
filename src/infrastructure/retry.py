from __future__ import annotations

"""
재시도 로직 모듈

지수 백오프 기반 재시도 로직을 제공합니다.
"""

import asyncio
import functools
from typing import Any, Callable, Optional

from loguru import logger

from src.domain.exceptions import PKMClipError


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    multiplier: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] | None = None,
) -> Callable[..., Any]:
    """
    지수 백오프 기반 재시도 데코레이터

    재시도 가능한 예외 발생 시 지수 백오프로 대기 후 재시도합니다.

    Args:
        max_retries: 최대 재시도 횟수 (기본값: 3)
        initial_delay: 초기 대기 시간 (초, 기본값: 1.0)
        multiplier: 대기 시간 배수 (기본값: 2.0)
        retryable_exceptions: 재시도할 예외 타입 튜플

    Returns:
        비동기 함수 래퍼

    Example:
        @retry_with_backoff(max_retries=3, initial_delay=1.0)
        async def fetch_data(url: str) -> str:
            return await httpx_client.get(url)
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None
            delay = initial_delay
            retryables = retryable_exceptions or (Exception,)

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryables as e:
                    last_exception = e

                    # retryable_exceptions에 포함된 예외는 무조건 재시도 가능
                    # PKMClipError의 자식 클래스이고 _retryable이 False인 경우만 재시도하지 않음
                    if isinstance(e, PKMClipError) and not getattr(e, "_retryable", True):
                        logger.error(f"Non-retryable error occurred: {e}")
                        raise

                    # 마지막 시도 후에는 재시도하지 않음
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded")
                        raise

                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} after {delay:.1f}s. "
                        f"Reason: {type(e).__name__}: {e}"
                    )
                    await asyncio.sleep(delay)
                    delay *= multiplier
                except Exception as e:
                    # retryable_exceptions에 없는 예외는 바로 발생
                    raise

                    # 마지막 시도 후에는 재시도하지 않음
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded")
                        raise

                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} after {delay:.1f}s. "
                        f"Reason: {type(e).__name__}: {e}"
                    )
                    await asyncio.sleep(delay)
                    delay *= multiplier
                except Exception:
                    # retryable_exceptions에 없는 예외는 바로 발생
                    raise

            # 이 코드에 도달하면 안 됨 (마지막 예외를 다시 던짐)
            # last_exception이 None일 수 있으므로 검사
            if last_exception is not None:
                raise last_exception

        return async_wrapper

    return decorator
