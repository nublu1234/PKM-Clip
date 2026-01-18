"""
이미지 다운로드 통합 테스트 (E2E)

전체 이미지 다운로드 흐름을 테스트합니다.
"""

import tempfile
from pathlib import Path

import pytest

from src.application.image_download_service import ImageDownloadService


class TestImageDownloadE2E:
    """이미지 다운로드 통합 테스트 클래스"""

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
    def image_download_service(self) -> ImageDownloadService:
        """
        ImageDownloadService 픽스처

        Returns:
            ImageDownloadService 인스턴스
        """
        return ImageDownloadService()

    @pytest.mark.asyncio
    async def test_no_images_flag_skips_processing(
        self, image_download_service: ImageDownloadService, temp_dir: Path
    ) -> None:
        """
        --no-images 플래그 테스트

        Given: 마크다운 콘텐츠에 이미지 URL이 있음

        And: --no-images 플래그가 설정됨

        When: 마크다운 처리 수행

        Then: 이미지 다운로드가 스킵됨

        And: 원본 콘텐츠 유지
        """
        markdown = "![image](https://example.com/image.png)"
        image_path = str(temp_dir)

        result = await image_download_service.process_markdown_images(
            markdown=markdown,
            image_path=image_path,
            no_images=True,
        )

        # 원본 콘텐츠 유지
        assert result == markdown

        # 파일이 다운로드되지 않았는지 확인
        downloaded_files = list(temp_dir.glob("*"))
        assert len(downloaded_files) == 0

    @pytest.mark.asyncio
    async def test_no_images_in_markdown(
        self, image_download_service: ImageDownloadService, temp_dir: Path
    ) -> None:
        """
        이미지가 없는 마크다운 테스트

        Given: 마크다운 콘텐츠에 이미지가 없음

        When: 마크다운 처리 수행

        Then: 원본 콘텐츠 유지
        """
        markdown = "텍스트만 있는 콘텐츠입니다."
        image_path = str(temp_dir)

        result = await image_download_service.process_markdown_images(
            markdown=markdown,
            image_path=image_path,
            no_images=False,
        )

        # 원본 콘텐츠 유지
        assert result == markdown

        # 파일이 다운로드되지 않았는지 확인
        downloaded_files = list(temp_dir.glob("*"))
        assert len(downloaded_files) == 0

    @pytest.mark.asyncio
    async def test_empty_markdown(
        self, image_download_service: ImageDownloadService, temp_dir: Path
    ) -> None:
        """
        빈 마크다운 테스트

        Given: 마크다운 콘텐츠가 비어있음

        When: 마크다운 처리 수행

        Then: 원본 콘텐츠 유지
        """
        markdown = ""
        image_path = str(temp_dir)

        result = await image_download_service.process_markdown_images(
            markdown=markdown,
            image_path=image_path,
            no_images=False,
        )

        # 원본 콘텐츠 유지
        assert result == markdown

        # 파일이 다운로드되지 않았는지 확인
        downloaded_files = list(temp_dir.glob("*"))
        assert len(downloaded_files) == 0
