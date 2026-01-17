from __future__ import annotations

"""
Jina AI Reader API 클라이언트

Jina AI Reader API와 통신하여 웹페이지 콘텐츠를 마크다운으로 변환합니다.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from loguru import logger

from src.domain.entities import MarkdownContent
from src.domain.exceptions import (
    InvalidURLError,
    JinaReaderAPIError,
    NetworkError,
    RateLimitExceededError,
    RetryableHTTPStatusError,
)
from src.domain.exceptions import (
    TimeoutError as PKMTimeoutError,
)
from src.infrastructure.config import JinaAPIConfig
from src.infrastructure.retry import retry_with_backoff
from src.infrastructure.url_validator import validate_url


class JinaReaderClient:
    """
    Jina AI Reader API 클라이언트

    웹페이지 URL을 마크다운으로 변환하는 기능을 제공합니다.
    """

    def __init__(self, config: JinaAPIConfig) -> None:
        """
        JinaReaderClient 초기화

        Args:
            config: Jina API 설정 (API key, headers, timeout 등)
        """
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        HTTP 클라이언트 인스턴스를 가져옵니다 (느린 초기화).

        Returns:
            httpx.AsyncClient 인스턴스
        """
        if self._client is None or self._client.is_closed:
            headers = self._prepare_headers()
            timeout = httpx.Timeout(self.config.timeout)

            self._client = httpx.AsyncClient(
                timeout=timeout,
                headers=headers,
                follow_redirects=True,
            )

        return self._client

    def _prepare_headers(self) -> dict[str, str]:
        """
        API 요청에 사용할 헤더를 준비합니다.

        Returns:
            헤더 딕셔너리
        """
        headers = {}

        # config에서 정의된 헤더 복사
        for key, value in self.config.headers.items():
            if key.startswith("x-") or key in ["Accept"]:
                # 불리안/정수 타입을 문자열로 변환
                headers[key] = str(value)

        # API Key 헤더 추가 (Bearer 토큰)
        if self.config.api_key:
            api_key = self.config.api_key
            # 로그에서 마스킹을 위해 실제 설정은 별도로 관리
            headers["Authorization"] = f"Bearer {api_key}"

        return headers

    def _prepare_api_url(self, target_url: str) -> str:
        """
        Jina Reader API 요청 URL을 생성합니다.

        Args:
            target_url: 변환할 대상 URL

        Returns:
            Jina Reader API URL
        """
        # URL 인코딩 (특수 문자 처리)
        # httpx는 자동으로 인코딩하므로 별도 처리 불필요
        # 하지만 명시적으로 인코딩하여 안정성 확보
        from urllib.parse import quote

        encoded_url = quote(target_url, safe=":/?#[]@!$&'()*+,;=")
        return f"{self.config.base_url}/{encoded_url}"

    async def fetch_markdown(self, url: str) -> MarkdownContent:
        """
        URL로부터 마크다운 콘텐츠를 가져옵니다

        Args:
            url: 마크다운으로 변환할 URL

        Returns:
            MarkdownContent: 변환된 마크다운 콘텐츠

        Raises:
            InvalidURLError: 유효하지 않은 URL인 경우
            JinaReaderAPIError: Jina Reader API 호출 실패 시
            RateLimitExceededError: Rate Limit 초과 시
            NetworkError: 네트워크 오류 발생 시
        """
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info(f"[{request_id}] URL processing started: {url}")

        try:
            # URL 검증
            if not validate_url(url):
                raise InvalidURLError("URL validation failed")

            # API URL 생성
            api_url = self._prepare_api_url(url)

            # 클라이언트 가져오기
            client = await self._get_client()

            # 재시도 로직 적용하여 요청
            markdown_text = await self._fetch_with_retry(client, api_url, request_id)

            # 응답 시간 계산
            elapsed = time.time() - start_time

            # 로깅
            logger.info(
                f"[{request_id}] Content received from Jina AI Reader: "
                f"{len(markdown_text)} chars, {elapsed:.2f}s"
            )

            # MarkdownContent 생성
            return MarkdownContent(
                url=url,
                markdown=markdown_text,
                fetched_at=datetime.now(timezone.utc),
            )

        except InvalidURLError as e:
            logger.error(f"[{request_id}] Invalid URL: {e}")
            raise
        except RateLimitExceededError as e:
            logger.error(f"[{request_id}] Rate limit exceeded: {e}")
            raise
        except (httpx.TimeoutException, PKMTimeoutError) as e:
            elapsed = time.time() - start_time
            logger.error(f"[{request_id}] Request timeout after {elapsed:.2f}s")
            raise PKMTimeoutError(str(e)) from e
        except httpx.NetworkError as e:
            logger.error(f"[{request_id}] Network error: {e}")
            raise NetworkError(str(e)) from e
        except httpx.HTTPStatusError as e:
            # 4xx 에러는 재시도하지 않고 즉시 예외 발생
            if 400 <= e.response.status_code < 500:
                logger.error(f"[{request_id}] Client error ({e.response.status_code}): {e}")
                raise JinaReaderAPIError(
                    f"API request failed with status {e.response.status_code}: {e.response.text}"
                ) from e
            raise

    async def _fetch_with_retry(
        self, client: httpx.AsyncClient, api_url: str, request_id: str
    ) -> str:
        """
        재시도 로직이 적용된 HTTP 요청을 수행합니다.

        Args:
            client: HTTP 클라이언트
            api_url: 요청할 API URL
            request_id: 요청 식별자

        Returns:
            마크다운 텍스트

        Raises:
            RateLimitExceededError: 429 상태 코드 수신 시
            JinaReaderAPIError: 기타 API 오류
        """

        # 재시도 로직 설정
        # 최대 3회 재시도, 초기 1초, 배수 2.0
        @retry_with_backoff(
            max_retries=self.config.max_retries,
            initial_delay=self.config.retry_delay,
            multiplier=self.config.retry_multiplier,
            retryable_exceptions=(
                httpx.NetworkError,
                httpx.TimeoutException,
                RateLimitExceededError,
                RetryableHTTPStatusError,
            ),
        )
        async def make_request() -> str:
            response = await client.get(api_url)

            # 429 Rate Limit 처리
            if response.status_code == 429:
                retry_after = self._parse_retry_after(response.headers.get("Retry-After"))
                wait_time = retry_after if retry_after else self.config.retry_delay

                logger.warning(
                    f"[{request_id}] Rate limit hit (429). Waiting {wait_time}s before retry..."
                )

                await self._wait_for_retry(wait_time)

                # 재시도를 위해 예외 발생 (retryable로 표시)
                exc = RateLimitExceededError(f"Rate limit exceeded. Retry after {wait_time}s")
                exc._retryable = True
                raise exc

            # 기타 상태 코드 에러 처리
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # 5xx 상태 코드인 경우 재시도 가능한 예외로 변환
                if 500 <= e.response.status_code < 600:
                    logger.warning(f"[{request_id}] Server error ({e.response.status_code}): {e}")
                    server_exc = RetryableHTTPStatusError(
                        f"Server error {e.response.status_code}: {e}"
                    )
                    server_exc._retryable = True
                    raise server_exc from e
                # 4xx 상태 코드는 즉시 예외 발생
                raise

            # 빈 응답 처리
            markdown_text = response.text.strip()
            if not markdown_text:
                raise JinaReaderAPIError("Received empty response from Jina Reader API")

            return markdown_text

        return await make_request()

    def _parse_retry_after(self, header_value: str | None) -> int | None:
        """
        Retry-After 헤더 값을 파싱합니다.

        Args:
            header_value: Retry-After 헤더 값

        Returns:
            대기 시간 (초) 또는 None
        """
        if header_value is None:
            return None

        try:
            return int(header_value)
        except (ValueError, TypeError):
            return None

    async def _wait_for_retry(self, seconds: int) -> None:
        """
        지정된 시간 동안 대기합니다.

        Args:
            seconds: 대기 시간 (초)
        """
        import asyncio

        await asyncio.sleep(seconds)

    async def close(self) -> None:
        """
        HTTP 클라이언트를 종료합니다.
        """
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self) -> "JinaReaderClient":
        """
        비동기 컨텍스트 매니저 진입

        Returns:
            JinaReaderClient 인스턴스
        """
        return self

    async def __aexit__(self, *args: Any) -> None:
        """
        비동기 컨텍스트 매니저 종료

        클라이언트를 정리합니다.
        """
        await self.close()
