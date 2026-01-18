"""
ImageDownloadService 단위 테스트
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.application.image_download_service import ImageDownloadService
from src.domain.exceptions import ImageDownloadError
from src.domain.image_processor import ImageProcessor
from src.infrastructure.image_downloader import ImageDownloader


class TestImageDownloadService:
    """ImageDownloadService 단위 테스트 클래스"""

    @pytest.fixture
    def image_processor(self) -> ImageProcessor:
        """
        ImageProcessor 픽스처

        Returns:
            ImageProcessor 인스턴스
        """
        return ImageProcessor()

    @pytest.fixture
    def image_downloader(self) -> ImageDownloader:
        """
        ImageDownloader 픽스처

        Returns:
            ImageDownloader 인스턴스
        """
        return ImageDownloader()

    @pytest.fixture
    def image_download_service(
        self, image_processor: ImageProcessor, image_downloader: ImageDownloader
    ) -> ImageDownloadService:
        """
        ImageDownloadService 픽스처

        Returns:
            ImageDownloadService 인스턴스
        """
        return ImageDownloadService(
            image_processor=image_processor,
            image_downloader=image_downloader,
        )

    @pytest.mark.asyncio
    async def test_process_markdown_images_no_images_flag(
        self, image_download_service: ImageDownloadService
    ) -> None:
        """
        --no-images 플래그 테스트

        Given: --no-images 플래그가 설정됨

        When: 마크다운 처리 수행

        Then: 이미지 URL 추출을 수행하지 않음

        And: 원본 이미지 참조 유지
        """
        markdown = "![alt](https://example.com/image.png)"
        image_path = "./Attachments"
        no_images = True

        result, image_count = await image_download_service.process_markdown_images(
            markdown=markdown,
            image_path=image_path,
            no_images=no_images,
        )

        # 원본 콘텐츠 유지
        assert result == markdown
        assert image_count == 0

    @pytest.mark.asyncio
    async def test_process_markdown_images_normal_case(
        self, image_download_service: ImageDownloadService, image_downloader: ImageDownloader
    ) -> None:
        """
        정상적인 이미지 처리 테스트

        Given: 마크다운 콘텐츠에 이미지 URL이 있음

        And: 이미지 다운로드 성공

        When: 마크다운 처리 수행

        Then: 이미지가 다운로드되고 Obsidian 참조로 변환됨
        """
        markdown = "![alt](https://example.com/image.png)"
        image_path = "./Attachments"
        no_images = False

        # Mock 다운로드
        with patch.object(
            image_downloader, "download_and_save", new_callable=AsyncMock
        ) as mock_download:
            mock_download.return_value = "/path/to/image.png"

            result, image_count = await image_download_service.process_markdown_images(
                markdown=markdown,
                image_path=image_path,
                no_images=no_images,
            )

            # Obsidian 참조 형식으로 변환됨
            assert "![[202" in result  # 타임스탬프 포함

            # 다운로드가 호출되었는지 확인
            mock_download.assert_called_once()
            # 이미지 개수 확인
            assert image_count == 1

    @pytest.mark.asyncio
    async def test_process_markdown_images_download_failure(
        self, image_download_service: ImageDownloadService, image_downloader: ImageDownloader
    ) -> None:
        """
        다운로드 실패 시 원본 URL 유지 테스트

        Given: 마크다운 콘텐츠에 이미지 URL이 있음

        And: 이미지 다운로드 실패

        When: 마크다운 처리 수행

        Then: 원본 URL 유지
        """
        markdown = "![alt](https://example.com/image.png)"
        image_path = "./Attachments"
        no_images = False

        # Mock 다운로드 실패
        with patch.object(
            image_downloader, "download_and_save", new_callable=AsyncMock
        ) as mock_download:
            mock_download.side_effect = ImageDownloadError("Download failed")

            result, image_count = await image_download_service.process_markdown_images(
                markdown=markdown,
                image_path=image_path,
                no_images=no_images,
            )

            # 원본 URL 유지
            assert result == markdown
            assert image_count == 0

    @pytest.mark.asyncio
    async def test_process_markdown_images_multiple_images(
        self, image_download_service: ImageDownloadService, image_downloader: ImageDownloader
    ) -> None:
        """
        여러 이미지 처리 테스트

        Given: 마크다운 콘텐츠에 여러 이미지 URL이 있음

        And: 모든 다운로드 성공

        When: 마크다운 처리 수행

        Then: 모든 이미지가 변환됨
        """
        markdown = "![img1](https://example.com/img1.png)\n![img2](https://example.com/img2.jpg)"
        image_path = "./Attachments"
        no_images = False

        # Mock 다운로드
        with patch.object(
            image_downloader, "download_and_save", new_callable=AsyncMock
        ) as mock_download:
            mock_download.return_value = "/path/to/image.png"

            result, image_count = await image_download_service.process_markdown_images(
                markdown=markdown,
                image_path=image_path,
                no_images=no_images,
            )

            # 모든 이미지가 Obsidian 참조로 변환됨
            assert markdown.count("!") == result.count("!")  # 이미지 개수 동일
            assert "https://example.com/" not in result  # 원본 URL 제거

            # 두 번 다운로드가 호출되었는지 확인
            assert mock_download.call_count == 2
            # 이미지 개수 확인
            assert image_count == 2

    @pytest.mark.asyncio
    async def test_process_markdown_images_no_images_in_content(
        self, image_download_service: ImageDownloadService, image_downloader: ImageDownloader
    ) -> None:
        """
        이미지가 없는 경우 테스트

        Given: 마크다운 콘텐츠에 이미지가 없음

        When: 마크다운 처리 수행

        Then: 원본 콘텐츠 유지
        """
        markdown = "텍스트만 있는 콘텐츠입니다."
        image_path = "./Attachments"
        no_images = False

        with patch.object(
            image_downloader, "download_and_save", new_callable=AsyncMock
        ) as mock_download:
            result, image_count = await image_download_service.process_markdown_images(
                markdown=markdown,
                image_path=image_path,
                no_images=no_images,
            )

            # 원본 콘텐츠 유지
            assert result == markdown
            # 다운로드가 호출되지 않았는지 확인
            mock_download.assert_not_called()
            # 이미지 개수 확인
            assert image_count == 0

    @pytest.mark.asyncio
    async def test_process_markdown_images_partial_failure(
        self, image_download_service: ImageDownloadService, image_downloader: ImageDownloader
    ) -> None:
        """
        부분적 다운로드 실패 테스트

        Given: 마크다운 콘텐츠에 여러 이미지가 있음

        And: 일부 다운로드 실패

        When: 마크다운 처리 수행

        Then: 성공한 이미지는 변환되고, 실패한 이미지는 원본 유지
        """
        markdown = "![img1](https://example.com/img1.png)\n![img2](https://example.com/img2.jpg)"
        image_path = "./Attachments"
        no_images = False

        # Mock 다운로드 (첫 번째 성공, 두 번째 실패)
        with patch.object(
            image_downloader, "download_and_save", new_callable=AsyncMock
        ) as mock_download:
            mock_download.side_effect = [
                "/path/to/img1.png",
                ImageDownloadError("Download failed"),
            ]

            result, image_count = await image_download_service.process_markdown_images(
                markdown=markdown,
                image_path=image_path,
                no_images=no_images,
            )

            # 첫 번째 이미지는 변환됨
            assert "![[202" in result
            # 두 번째 이미지는 원본 유지
            assert "https://example.com/img2.jpg" in result
            # 이미지 개수 확인 (1개만 성공)
            assert image_count == 1

    @pytest.mark.asyncio
    async def test_process_markdown_images_html_img_tag(
        self, image_download_service: ImageDownloadService, image_downloader: ImageDownloader
    ) -> None:
        """
        HTML img 태그 처리 테스트

        Given: 마크다운 콘텐츠에 HTML img 태그가 있음

        When: 마크다운 처리 수행

        Then: HTML img 태그도 Obsidian 참조로 변환됨
        """
        markdown = '<img src="https://example.com/image.png" alt="alt text">'
        image_path = "./Attachments"
        no_images = False

        # Mock 다운로드
        with patch.object(
            image_downloader, "download_and_save", new_callable=AsyncMock
        ) as mock_download:
            mock_download.return_value = "/path/to/image.png"

            result, image_count = await image_download_service.process_markdown_images(
                markdown=markdown,
                image_path=image_path,
                no_images=no_images,
            )

            # HTML 태그가 Obsidian 참조로 변환됨
            assert "![[202" in result
            assert "<img" not in result  # HTML 태그 제거
            # 이미지 개수 확인
            assert image_count == 1

    @pytest.mark.asyncio
    async def test_process_markdown_images_dry_run_mode(
        self, image_download_service: ImageDownloadService, image_downloader: ImageDownloader
    ) -> None:
        """
        dry-run 모드 테스트

        Given: dry_run=True로 설정됨

        When: 마크다운 처리 수행

        Then: 이미지 다운로드가 수행되지 않음

        And: 이미지 개수만 반환됨
        """
        markdown = "![alt](https://example.com/image.png)\n![img2](https://example.com/img2.jpg)"
        image_path = "./Attachments"

        with patch.object(
            image_downloader, "download_and_save", new_callable=AsyncMock
        ) as mock_download:
            result, image_count = await image_download_service.process_markdown_images(
                markdown=markdown,
                image_path=image_path,
                no_images=False,
                dry_run=True,
            )

            # 원본 콘텐츠 유지
            assert result == markdown

            # 다운로드가 호출되지 않았는지 확인
            mock_download.assert_not_called()

            # 이미지 개수만 반환됨
            assert image_count == 2

    @pytest.mark.asyncio
    async def test_process_markdown_images_dry_run_no_images(
        self, image_download_service: ImageDownloadService
    ) -> None:
        """
        dry-run 모드 + 이미지 없는 경우 테스트

        Given: dry_run=True로 설정됨

        And: 마크다운 콘텐츠에 이미지가 없음

        When: 마크다운 처리 수행

        Then: 원본 콘텐츠 유지

        And: 이미지 개수는 0
        """
        markdown = "텍스트만 있는 콘텐츠입니다."
        image_path = "./Attachments"

        result, image_count = await image_download_service.process_markdown_images(
            markdown=markdown,
            image_path=image_path,
            no_images=False,
            dry_run=True,
        )

        # 원본 콘텐츠 유지
        assert result == markdown

        # 이미지 개수는 0
        assert image_count == 0
