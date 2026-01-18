"""
SaveMarkdownFileService 단위 테스트

마크다운 파일 저장 서비스를 테스트합니다.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.models import FrontmatterOptions
from src.application.save_markdown_file_service import SaveMarkdownFileService
from src.domain.entities import Clipping


class TestSaveMarkdownFileService:
    """SaveMarkdownFileService 테스트"""

    @pytest.fixture
    def mock_url_to_markdown_service(self):
        """URLToMarkdownService 모의"""
        mock = MagicMock()
        mock.process_url = AsyncMock()
        return mock

    @pytest.fixture
    def mock_filename_generator(self):
        """FilenameGenerator 모의"""
        mock = MagicMock()
        mock.generate_filename = MagicMock(return_value="Test Article")
        return mock

    @pytest.fixture
    def mock_markdown_file_combiner(self):
        """MarkdownFileCombiner 모의"""
        mock = MagicMock()
        mock.combine_frontmatter_and_markdown = MagicMock(return_value="# Combined")
        return mock

    @pytest.fixture
    def mock_markdown_file_writer(self):
        """MarkdownFileWriter 모의"""
        mock = MagicMock()
        mock.write_markdown_file = MagicMock()
        return mock

    @pytest.fixture
    def service(
        self,
        mock_url_to_markdown_service,
        mock_filename_generator,
        mock_markdown_file_combiner,
        mock_markdown_file_writer,
    ):
        """테스트용 서비스 인스턴스"""
        return SaveMarkdownFileService(
            url_to_markdown_service=mock_url_to_markdown_service,
            filename_generator=mock_filename_generator,
            markdown_file_combiner=mock_markdown_file_combiner,
            markdown_file_writer=mock_markdown_file_writer,
        )

    @pytest.fixture
    def sample_clipping(self):
        """샘플 Clipping"""
        from datetime import date

        from src.domain.entities import Frontmatter

        return Clipping(
            url="https://example.com/article",
            frontmatter=Frontmatter(
                title="Test Article",
                author=["John Doe"],
                source="https://example.com/article",
                published=date(2024, 1, 15),
                created=date.today(),
            ),
            content="# Test Article\n\nContent here...",
        )

    async def test_save_markdown_file_basic(
        self,
        service,
        mock_url_to_markdown_service,
        sample_clipping,
        tmp_path,
    ):
        """기본 파일 저장"""
        mock_url_to_markdown_service.process_url.return_value = sample_clipping

        result = await service.save_markdown_file(
            url="https://example.com/article",
            output_dir=str(tmp_path),
        )

        assert result.endswith("Test Article.md")
        mock_url_to_markdown_service.process_url.assert_called_once()
        mock_url_to_markdown_service.process_url.call_args.kwargs[
            "url"
        ] == "https://example.com/article"

    async def test_save_markdown_file_with_custom_filename(
        self,
        service,
        mock_filename_generator,
        mock_url_to_markdown_service,
        sample_clipping,
        tmp_path,
    ):
        """사용자 지정 파일명"""
        mock_url_to_markdown_service.process_url.return_value = sample_clipping

        await service.save_markdown_file(
            url="https://example.com/article",
            output_dir=str(tmp_path),
            filename="custom-name",
        )

        # custom_filename이 전달되었는지 확인
        mock_filename_generator.generate_filename.assert_called_once_with(
            title="Test Article",
            custom_filename="custom-name",
        )

    async def test_save_markdown_file_with_frontmatter_options(
        self,
        service,
        mock_url_to_markdown_service,
        sample_clipping,
        tmp_path,
    ):
        """Frontmatter 옵션 전달"""
        mock_url_to_markdown_service.process_url.return_value = sample_clipping

        options = FrontmatterOptions(title="Custom Title", tags=["python"])
        await service.save_markdown_file(
            url="https://example.com/article",
            output_dir=str(tmp_path),
            frontmatter_options=options,
        )

        mock_url_to_markdown_service.process_url.assert_called_once()
        call_kwargs = mock_url_to_markdown_service.process_url.call_args.kwargs
        assert call_kwargs["options"] == options

    async def test_save_markdown_file_with_force(
        self,
        service,
        mock_url_to_markdown_service,
        mock_markdown_file_writer,
        sample_clipping,
        tmp_path,
    ):
        """force 옵션"""
        mock_url_to_markdown_service.process_url.return_value = sample_clipping

        await service.save_markdown_file(
            url="https://example.com/article",
            output_dir=str(tmp_path),
            force=True,
        )

        mock_markdown_file_writer.write_markdown_file.assert_called_once()
        call_kwargs = mock_markdown_file_writer.write_markdown_file.call_args.kwargs
        assert call_kwargs["force"] is True

    async def test_save_markdown_file_no_images(
        self,
        service,
        mock_url_to_markdown_service,
        sample_clipping,
        tmp_path,
    ):
        """이미지 다운로드 스킵"""
        mock_url_to_markdown_service.process_url.return_value = sample_clipping

        await service.save_markdown_file(
            url="https://example.com/article",
            output_dir=str(tmp_path),
            no_images=True,
        )

        mock_url_to_markdown_service.process_url.assert_called_once()
        call_kwargs = mock_url_to_markdown_service.process_url.call_args.kwargs
        assert call_kwargs["no_images"] is True

    async def test_save_markdown_file_default_output_dir(
        self,
        service,
        mock_url_to_markdown_service,
        sample_clipping,
    ):
        """기본 출력 디렉토리 사용"""
        from pathlib import Path

        mock_url_to_markdown_service.process_url.return_value = sample_clipping

        result = await service.save_markdown_file(
            url="https://example.com/article",
        )

        # ~가 확장된 경로인지 확인
        default_dir = str(Path("~/Clippings").expanduser())
        assert default_dir in result
        assert result.endswith("Test Article.md")

    async def test_handle_duplicate_filename_no_force(
        self,
        service,
        mock_markdown_file_writer,
        mock_url_to_markdown_service,
        sample_clipping,
        tmp_path,
    ):
        """파일명 중복 처리 (force=False)"""
        mock_url_to_markdown_service.process_url.return_value = sample_clipping

        # 파일이 존재한다고 가정
        (tmp_path / "Test Article.md").touch()

        await service.save_markdown_file(
            url="https://example.com/article",
            output_dir=str(tmp_path),
            force=False,
        )

        # 파일명이 "Test Article 1"로 변경되었는지 확인
        mock_markdown_file_writer.write_markdown_file.assert_called_once()
        filepath = mock_markdown_file_writer.write_markdown_file.call_args.kwargs["filepath"]
        assert "Test Article 1.md" in str(filepath)

    async def test_handle_duplicate_filename_with_force(
        self,
        service,
        mock_markdown_file_writer,
        mock_url_to_markdown_service,
        sample_clipping,
        tmp_path,
    ):
        """파일명 중복 시 force=True"""
        mock_url_to_markdown_service.process_url.return_value = sample_clipping

        await service.save_markdown_file(
            url="https://example.com/article",
            output_dir=str(tmp_path),
            force=True,
        )

        # 기본 파일명 유지
        mock_markdown_file_writer.write_markdown_file.assert_called_once()
        filepath = mock_markdown_file_writer.write_markdown_file.call_args.kwargs["filepath"]
        assert "Test Article.md" in str(filepath)

    async def test_frontmatter_and_markdown_combined(
        self,
        service,
        mock_markdown_file_combiner,
        mock_url_to_markdown_service,
        sample_clipping,
        tmp_path,
    ):
        """Frontmatter와 Markdown 결합 확인"""
        mock_url_to_markdown_service.process_url.return_value = sample_clipping

        await service.save_markdown_file(
            url="https://example.com/article",
            output_dir=str(tmp_path),
        )

        mock_markdown_file_combiner.combine_frontmatter_and_markdown.assert_called_once()
        call_args = mock_markdown_file_combiner.combine_frontmatter_and_markdown.call_args
        assert call_args.kwargs["frontmatter"]["title"] == "Test Article"
        assert call_args.kwargs["markdown"] == "# Test Article\n\nContent here..."
