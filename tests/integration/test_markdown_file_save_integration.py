"""
마크다운 파일 저장 통합 테스트

마크다운 파일 저장 전체 워크플로우를 통합적으로 테스트합니다.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx

from src.application.models import FrontmatterOptions
from src.application.save_markdown_file_service import SaveMarkdownFileService


class TestMarkdownFileSaveIntegration:
    """마크다운 파일 저장 통합 테스트"""

    @pytest.fixture
    def service(self):
        """테스트용 서비스 인스턴스"""
        return SaveMarkdownFileService()

    @pytest.fixture
    def mock_config(self):
        """테스트용 API 설정"""
        from src.infrastructure.config import JinaAPIConfig

        return JinaAPIConfig()

    @pytest.mark.asyncio
    async def test_full_workflow_save_file(self, service, tmp_path, mock_config):
        """전체 워크플로우 테스트: URL → 파일 저장"""
        mock_markdown = """# Test Article

Author: John Doe

This is a test article content."""

        with respx.mock:
            respx.get(f"{mock_config.base_url}/https://example.com/article").mock(
                return_value=httpx.Response(200, text=mock_markdown)
            )

            # 파일 저장
            filepath = await service.save_markdown_file(
                url="https://example.com/article",
                output_dir=str(tmp_path),
                no_images=True,
            )

            # 파일 존재 확인
            assert Path(filepath).exists()

            # 파일 내용 확인
            content = Path(filepath).read_text(encoding="utf-8")
            assert "---" in content
            assert "title: Test Article" in content
            assert "# Test Article" in content

    @pytest.mark.asyncio
    async def test_full_workflow_with_custom_filename(self, service, tmp_path, mock_config):
        """사용자 지정 파일명으로 저장"""
        mock_markdown = "# Custom Title\n\nContent..."

        with respx.mock:
            respx.get(f"{mock_config.base_url}/https://example.com/article").mock(
                return_value=httpx.Response(200, text=mock_markdown)
            )

            filepath = await service.save_markdown_file(
                url="https://example.com/article",
                output_dir=str(tmp_path),
                filename="custom-file",
                no_images=True,
            )

            assert "custom-file.md" in filepath
            assert Path(filepath).exists()

    @pytest.mark.asyncio
    async def test_full_workflow_duplicate_handling(self, service, tmp_path, mock_config):
        """파일명 중복 처리 테스트"""
        mock_markdown = "# Test Article\n\nContent..."

        with respx.mock:
            respx.get(f"{mock_config.base_url}/https://example.com/article").mock(
                return_value=httpx.Response(200, text=mock_markdown)
            )

            # 첫 번째 파일 저장
            filepath1 = await service.save_markdown_file(
                url="https://example.com/article",
                output_dir=str(tmp_path),
                no_images=True,
            )
            assert "Test Article.md" in filepath1

            # 두 번째 파일 저장 (중복 처리)
            filepath2 = await service.save_markdown_file(
                url="https://example.com/article",
                output_dir=str(tmp_path),
                no_images=True,
            )
            assert "Test Article 1.md" in filepath2
            assert Path(filepath2).exists()

    @pytest.mark.asyncio
    async def test_full_workflow_force_overwrite(self, service, tmp_path, mock_config):
        """force 옵션 테스트: 덮어쓰기"""
        mock_markdown1 = "# Original\n\nContent 1..."
        mock_markdown2 = "# Original\n\nContent 2..."

        with respx.mock:
            route = respx.get(f"{mock_config.base_url}/https://example.com/article")

            # 첫 번째 저장
            route.mock(return_value=httpx.Response(200, text=mock_markdown1))
            filepath1 = await service.save_markdown_file(
                url="https://example.com/article",
                output_dir=str(tmp_path),
                force=False,
                no_images=True,
            )
            content1 = Path(filepath1).read_text(encoding="utf-8")
            assert "Content 1..." in content1

            # 두 번째 저장 (force=True로 덮어쓰기)
            route.mock(return_value=httpx.Response(200, text=mock_markdown2))
            filepath2 = await service.save_markdown_file(
                url="https://example.com/article",
                output_dir=str(tmp_path),
                force=True,
                no_images=True,
            )
            content2 = Path(filepath2).read_text(encoding="utf-8")
            assert "Content 2..." in content2
            assert filepath1 == filepath2

    @pytest.mark.asyncio
    async def test_full_workflow_with_frontmatter_options(self, service, tmp_path, mock_config):
        """Frontmatter 옵션 테스트"""
        mock_markdown = "# Original Title\n\nContent..."

        with respx.mock:
            respx.get(f"{mock_config.base_url}/https://example.com/article").mock(
                return_value=httpx.Response(200, text=mock_markdown)
            )

            # Frontmatter 옵션 지정
            options = FrontmatterOptions(
                title="Custom Title",
                author="Jane Smith",
                tags=["python", "test"],
            )

            filepath = await service.save_markdown_file(
                url="https://example.com/article",
                output_dir=str(tmp_path),
                frontmatter_options=options,
                no_images=True,
            )

            content = Path(filepath).read_text(encoding="utf-8")
            assert "title: Custom Title" in content
            assert "- Jane Smith" in content
            assert "python" in content
            assert "test" in content

    @pytest.mark.asyncio
    async def test_full_workflow_no_images(self, service, tmp_path, mock_config):
        """이미지 다운로드 스킵 테스트"""
        mock_markdown = "# Test\n\nContent with image: ![Image](https://example.com/image.png)"

        with respx.mock:
            respx.get(f"{mock_config.base_url}/https://example.com/article").mock(
                return_value=httpx.Response(200, text=mock_markdown)
            )

            filepath = await service.save_markdown_file(
                url="https://example.com/article",
                output_dir=str(tmp_path),
                no_images=True,
            )

            content = Path(filepath).read_text(encoding="utf-8")
            assert "Content with image:" in content
            # 이미지가 다운로드되지 않음 (로컬 경로 변환 없음)

    @pytest.mark.asyncio
    async def test_full_workflow_error_handling(self, service, tmp_path, mock_config):
        """에러 처리 테스트"""
        with respx.mock:
            respx.get(f"{mock_config.base_url}/https://example.com/not-found").mock(
                return_value=httpx.Response(404, text="Not Found")
            )

            with pytest.raises(Exception):
                await service.save_markdown_file(
                    url="https://example.com/not-found",
                    output_dir=str(tmp_path),
                    no_images=True,
                )
