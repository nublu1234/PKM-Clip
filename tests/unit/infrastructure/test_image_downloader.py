"""
ImageDownloader 단위 테스트
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.domain.exceptions import ImageDownloadError, ImageSizeExceededError
from src.infrastructure.image_downloader import ImageDownloader


class TestImageDownloader:
    """ImageDownloader 단위 테스트 클래스"""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """
        임시 디렉토리 픽스처

        Returns:
            임시 디렉토리 경로
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def image_downloader(self) -> ImageDownloader:
        """
        ImageDownloader 픽스처

        Returns:
            ImageDownloader 인스턴스
        """
        return ImageDownloader()

    @pytest.mark.asyncio
    async def test_download_image_success(self, image_downloader: ImageDownloader) -> None:
        """
        정상 다운로드 테스트

        Given: 유효한 이미지 URL이 있음

        When: 이미지를 다운로드함

        Then: 이미지 데이터가 반환됨
        """
        url = "https://example.com/image.png"
        mock_content = b"fake image data"

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            # Mock HTTP 클라이언트 설정
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = mock_content
            mock_response.raise_for_status = MagicMock()

            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()

            mock_client_class.return_value = mock_client

            result = await image_downloader.download_image(url)

            assert result == mock_content
            mock_client.get.assert_called_once_with(url, follow_redirects=True)

    @pytest.mark.asyncio
    async def test_download_image_404_error(self, image_downloader: ImageDownloader) -> None:
        """
        404 에러 처리 테스트

        Given: 이미지 URL이 404 응답을 반환함

        When: 이미지 다운로드 시도

        Then: ImageDownloadError 예외가 발생함
        """
        url = "https://example.com/nonexistent.png"

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            # Mock HTTP 클라이언트 설정
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 404

            mock_error = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=mock_response
            )
            mock_error.response = mock_response

            mock_client.get = AsyncMock(side_effect=mock_error)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()

            mock_client_class.return_value = mock_client

            with pytest.raises(ImageDownloadError) as exc_info:
                await image_downloader.download_image(url)

            assert "not found (404)" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_download_image_403_error(self, image_downloader: ImageDownloader) -> None:
        """
        403 에러 처리 테스트

        Given: 이미지 URL이 403 응답을 반환함

        When: 이미지 다운로드 시도

        Then: ImageDownloadError 예외가 발생함
        """
        url = "https://example.com/forbidden.png"

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            # Mock HTTP 클라이언트 설정
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 403

            mock_error = httpx.HTTPStatusError(
                "Forbidden", request=MagicMock(), response=mock_response
            )
            mock_error.response = mock_response

            mock_client.get = AsyncMock(side_effect=mock_error)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()

            mock_client_class.return_value = mock_client

            with pytest.raises(ImageDownloadError) as exc_info:
                await image_downloader.download_image(url)

            assert "access forbidden (403)" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_download_image_timeout_retry(self, image_downloader: ImageDownloader) -> None:
        """
        타임아웃 재시도 테스트

        Given: 첫 번째 다운로드가 타임아웃으로 실패하고, 두 번째는 성공함

        When: 이미지 다운로드 시도

        Then: 재시도 후 성공함
        """
        url = "https://example.com/image.png"
        mock_content = b"fake image data"

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            # Mock HTTP 클라이언트 설정
            mock_client = AsyncMock()

            # 첫 번째 요청은 타임아웃, 두 번째 요청은 성공
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = mock_content
            mock_response.raise_for_status = MagicMock()

            mock_client.get = AsyncMock(
                side_effect=[
                    httpx.TimeoutException("Timeout"),
                    mock_response,
                ]
            )
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()

            mock_client_class.return_value = mock_client

            result = await image_downloader.download_image(url)

            assert result == mock_content
            assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_download_image_size_limit_exceeded(
        self, image_downloader: ImageDownloader
    ) -> None:
        """
        파일 크기 제한 초과 테스트

        Given: 이미지 크기가 10MB를 초과함

        When: 이미지 다운로드 시도

        Then: ImageSizeExceededError 예외가 발생함
        """
        url = "https://example.com/large.png"

        # 11MB 크기의 더미 데이터
        large_content = b"x" * (11 * 1024 * 1024)

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            # Mock HTTP 클라이언트 설정
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = large_content
            mock_response.raise_for_status = MagicMock()

            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()

            mock_client_class.return_value = mock_client

            with pytest.raises(ImageSizeExceededError):
                await image_downloader.download_image(url)

    def test_check_exists_file_exists(
        self, image_downloader: ImageDownloader, temp_dir: Path
    ) -> None:
        """
        파일 존재 확인 테스트 (True)

        Given: 파일이 존재함

        When: 파일 존재 여부를 확인함

        Then: True가 반환됨
        """
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        result = image_downloader.check_exists(str(test_file))

        assert result is True

    def test_check_exists_file_not_exists(
        self, image_downloader: ImageDownloader, temp_dir: Path
    ) -> None:
        """
        파일 존재 확인 테스트 (False)

        Given: 파일이 존재하지 않음

        When: 파일 존재 여부를 확인함

        Then: False가 반환됨
        """
        test_file = temp_dir / "nonexistent.txt"

        result = image_downloader.check_exists(str(test_file))

        assert result is False

    def test_save_to_disk(self, image_downloader: ImageDownloader, temp_dir: Path) -> None:
        """
        디스크 저장 테스트

        Given: 유효한 이미지 데이터와 파일 경로

        When: 파일을 저장함

        Then: 파일이 저장됨
        """
        test_file = temp_dir / "test.txt"
        content = b"test content"

        image_downloader.save_to_disk(content, str(test_file))

        assert test_file.exists()
        assert test_file.read_bytes() == content

    @pytest.mark.asyncio
    async def test_download_and_save_new_file(
        self, image_downloader: ImageDownloader, temp_dir: Path
    ) -> None:
        """
        새 파일 다운로드 및 저장 테스트

        Given: 파일이 존재하지 않음

        When: 이미지를 다운로드하고 저장함

        Then: 파일이 다운로드되고 저장됨
        """
        url = "https://example.com/image.png"
        filename = "test_image.png"
        mock_content = b"fake image data"

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            # Mock HTTP 클라이언트 설정
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = mock_content
            mock_response.raise_for_status = MagicMock()

            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()

            mock_client_class.return_value = mock_client

            result = await image_downloader.download_and_save(
                url=url,
                image_path=str(temp_dir),
                filename=filename,
            )

            expected_path = str(temp_dir / filename)
            assert result == expected_path
            assert Path(expected_path).exists()
            assert Path(expected_path).read_bytes() == mock_content

    @pytest.mark.asyncio
    async def test_download_and_save_existing_file_skips(
        self, image_downloader: ImageDownloader, temp_dir: Path
    ) -> None:
        """
        기존 파일 스킵 테스트

        Given: 파일이 이미 존재함

        When: 이미지 다운로드를 시도함

        Then: 다운로드를 스킵하고 기존 파일 경로를 반환함
        """
        url = "https://example.com/image.png"
        filename = "test_image.png"
        existing_content = b"existing content"

        # 기존 파일 생성
        test_file = temp_dir / filename
        test_file.write_bytes(existing_content)

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            # Mock HTTP 클라이언트 설정
            mock_client = AsyncMock()
            mock_client.get = AsyncMock()

            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()

            mock_client_class.return_value = mock_client

            result = await image_downloader.download_and_save(
                url=url,
                image_path=str(temp_dir),
                filename=filename,
            )

            # get가 호출되지 않아야 함 (스킵)
            mock_client.get.assert_not_called()

            # 기존 파일이 유지되어야 함
            assert test_file.read_bytes() == existing_content
