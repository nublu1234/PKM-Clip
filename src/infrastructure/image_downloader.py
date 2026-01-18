"""
이미지 다운로더 모듈

이미지 URL에서 이미지를 다운로드하고 로컬에 저장합니다.
"""

import asyncio
from pathlib import Path

import httpx

from src.domain.exceptions import (
    ImageDownloadError,
    ImageSizeExceededError,
)
from src.domain.image_processor import ImageProcessor
from src.infrastructure.file_system import FileSystem
from src.infrastructure.logger import get_logger

logger = get_logger()


class ImageDownloader:
    """
    이미지 다운로더 클래스

    이미지 URL에서 이미지를 다운로드하고 로컬에 저장합니다.
    재시도 로직, 타임아웃 설정 등을 포함합니다.
    """

    # 타임아웃 설정 (초)
    DEFAULT_TIMEOUT = 30

    # 최대 재시도 횟수
    MAX_RETRIES = 2

    # 재시도 대기 시간 (초)
    RETRY_DELAYS = [2, 4]

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        retry_delays: list[int] | None = None,
        image_processor: ImageProcessor | None = None,
    ) -> None:
        """
        이미지 다운로더 초기화

        Args:
            timeout: 타임아웃 시간 (초)
            max_retries: 최대 재시도 횟수
            retry_delays: 재시도 대기 시간 목록 (초)
            image_processor: 이미지 프로세서 (기본값: 새 인스턴스)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delays = retry_delays or self.RETRY_DELAYS
        self.image_processor = image_processor or ImageProcessor()
        self.file_system = FileSystem()

    async def download_image(self, url: str) -> bytes:
        """
        이미지를 다운로드합니다.

        재시도 로직과 타임아웃이 적용됩니다.

        Args:
            url: 이미지 URL

        Returns:
            다운로드된 이미지 데이터 (bytes)

        Raises:
            ImageDownloadError: 다운로드 실패 시
        """
        logger.debug(f"이미지 다운로드 시작: {url}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries + 1):
                try:
                    response = await client.get(url, follow_redirects=True)
                    response.raise_for_status()

                    # 콘텐츠 크기 검증
                    content_size = len(response.content)
                    self.image_processor.validate_image_size(content_size)

                    logger.debug(f"이미지 다운로드 성공: {url} ({content_size} bytes)")
                    return response.content

                except httpx.HTTPStatusError as e:
                    # 4xx 에러는 재시도하지 않음
                    if 400 <= e.response.status_code < 500:
                        error_msg = self._get_http_error_message(e.response.status_code, url)
                        logger.warning(error_msg)
                        raise ImageDownloadError(error_msg) from e

                    # 5xx 에러는 재시도
                    if attempt < self.max_retries:
                        delay = self.retry_delays[attempt]
                        logger.warning(
                            f"이미지 다운로드 실패 (재시도 {attempt + 1}/{self.max_retries}): {url} - {e}"
                        )
                        await asyncio.sleep(delay)
                        continue

                    raise ImageDownloadError(f"Image download failed: {url} - {e}") from e

                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    # 타임아웃/네트워크 에러는 재시도
                    if attempt < self.max_retries:
                        delay = self.retry_delays[attempt]
                        logger.warning(
                            f"이미지 다운로드 실패 (재시도 {attempt + 1}/{self.max_retries}): {url} - {e}"
                        )
                        await asyncio.sleep(delay)
                        continue

                    raise ImageDownloadError(f"Image download timeout: {url}") from e

                except ImageSizeExceededError:
                    # 이미지 크기 초과는 재시료하지 않음
                    raise

            # 모든 재시도 실패
            raise ImageDownloadError(
                f"Image download failed after {self.max_retries} retries: {url}"
            )

    def _get_http_error_message(self, status_code: int, url: str) -> str:
        """
        HTTP 상태 코드에 따른 에러 메시지를 반환합니다.

        Args:
            status_code: HTTP 상태 코드
            url: 이미지 URL

        Returns:
            에러 메시지
        """
        error_messages = {
            400: f"Bad request: {url}",
            401: f"Unauthorized: {url}",
            403: f"Image access forbidden (403): {url}",
            404: f"Image not found (404): {url}",
            429: f"Too many requests (429): {url}",
        }
        return error_messages.get(status_code, f"HTTP error {status_code}: {url}")

    def check_exists(self, filepath: str) -> bool:
        """
        파일이 존재하는지 확인합니다.

        Args:
            filepath: 파일 경로

        Returns:
            파일 존재 여부
        """
        exists = self.file_system.file_exists(filepath)
        if exists:
            logger.debug(f"이미지 이미 존재함: {filepath}")
        return exists

    def save_to_disk(self, content: bytes, filepath: str) -> None:
        """
        이미지를 디스크에 저장합니다.

        Args:
            content: 이미지 데이터
            filepath: 저장할 파일 경로
        """
        self.file_system.save_file(content, filepath)
        logger.info(f"이미지 저장됨: {filepath} ({len(content)} bytes)")

    async def download_and_save(self, url: str, image_path: str, filename: str) -> str:
        """
        이미지를 다운로드하고 디스크에 저장합니다.

        이미 존재하는 파일이면 다운로드를 건너뜁니다.

        Args:
            url: 이미지 URL
            image_path: 이미지 저장 디렉토리
            filename: 저장할 파일명

        Returns:
            저장된 파일의 전체 경로

        Raises:
            ImageDownloadError: 다운로드 실패 시
        """
        # 디렉토리 생성
        self.file_system.ensure_directory(image_path)

        # 파일 경로 생성
        filepath = str(Path(image_path).expanduser() / filename)

        # 파일 존재 확인
        if self.check_exists(filepath):
            logger.info(f"이미지 이미 존재함, 다운로드 스킵: {filepath}")
            return filepath

        # 이미지 다운로드
        content = await self.download_image(url)

        # 파일 저장
        self.save_to_disk(content, filepath)

        return filepath
