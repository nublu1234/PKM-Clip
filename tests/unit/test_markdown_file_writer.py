"""
MarkdownFileWriter 단위 테스트

마크다운 파일 작성을 테스트합니다.
"""

from pathlib import Path

import pytest

from src.domain.exceptions import FileExistsError
from src.infrastructure.markdown_file_writer import MarkdownFileWriter, MarkdownWriteResult


class TestMarkdownFileWriter:
    """MarkdownFileWriter 테스트"""

    def test_write_markdown_file(self, tmp_path: Path):
        """마크다운 파일 정상 저장"""
        writer = MarkdownFileWriter()
        filepath = tmp_path / "test.md"
        content = "# Test\n\nContent here..."

        writer.write_markdown_file(content, filepath)

        assert filepath.exists()
        assert filepath.read_text(encoding="utf-8") == content

    def test_write_markdown_file_creates_directory(self, tmp_path: Path):
        """존재하지 않는 디렉토리 생성"""
        writer = MarkdownFileWriter()
        filepath = tmp_path / "subdir" / "test.md"
        content = "# Test\n\nContent here..."

        writer.write_markdown_file(content, filepath)

        assert filepath.exists()
        assert filepath.parent.exists()

    def test_write_markdown_file_force_overwrite(self, tmp_path: Path):
        """force=True로 덮어쓰기"""
        writer = MarkdownFileWriter()
        filepath = tmp_path / "test.md"
        original_content = "# Original\n\nContent..."
        new_content = "# New\n\nContent..."

        # 첫 번째 저장
        writer.write_markdown_file(original_content, filepath)
        assert filepath.read_text(encoding="utf-8") == original_content

        # 덮어쓰기
        writer.write_markdown_file(new_content, filepath, force=True)
        assert filepath.read_text(encoding="utf-8") == new_content

    def test_write_markdown_file_exists_no_force(self, tmp_path: Path):
        """파일 존재 시 force=False면 예외 발생"""
        writer = MarkdownFileWriter()
        filepath = tmp_path / "test.md"
        content = "# Test\n\nContent here..."

        # 첫 번째 저장
        writer.write_markdown_file(content, filepath)

        # 두 번째 저장 시 예외 발생
        with pytest.raises(FileExistsError) as exc_info:
            writer.write_markdown_file(content, filepath, force=False)

        assert "already exists" in str(exc_info.value)

    def test_write_markdown_file_empty_content(self, tmp_path: Path):
        """빈 내용 저장"""
        writer = MarkdownFileWriter()
        filepath = tmp_path / "test.md"
        content = ""

        writer.write_markdown_file(content, filepath)

        assert filepath.exists()
        assert filepath.read_text(encoding="utf-8") == ""

    def test_write_markdown_file_unicode_content(self, tmp_path: Path):
        """유니코드 콘텐츠 저장 (한글 등)"""
        writer = MarkdownFileWriter()
        filepath = tmp_path / "test.md"
        content = "# 테스트\n\n한글 내용입니다..."

        writer.write_markdown_file(content, filepath)

        assert filepath.exists()
        assert filepath.read_text(encoding="utf-8") == content

    def test_write_markdown_file_long_content(self, tmp_path: Path):
        """긴 콘텐츠 저장"""
        writer = MarkdownFileWriter()
        filepath = tmp_path / "test.md"
        content = "# Long Content\n\n" + "Content line.\n" * 1000

        writer.write_markdown_file(content, filepath)

        assert filepath.exists()
        assert filepath.read_text(encoding="utf-8") == content

    def test_write_markdown_file_dry_run_mode(self, tmp_path: Path):
        """dry-run 모드: 파일 저장 안 됨"""
        writer = MarkdownFileWriter()
        filepath = tmp_path / "test.md"
        content = "# Test\n\nContent here..."

        result = writer.write_markdown_file(content, filepath, dry_run=True)

        assert isinstance(result, MarkdownWriteResult)
        assert not filepath.exists()
        assert result.was_saved is False
        assert result.content_size > 0

    def test_write_markdown_file_dry_run_vs_normal_mode(self, tmp_path: Path):
        """dry-run 모드와 일반 모드 비교"""
        writer = MarkdownFileWriter()
        filepath = tmp_path / "test.md"
        content = "# Test\n\nContent here..."

        dry_run_result = writer.write_markdown_file(content, filepath, dry_run=True)
        assert not filepath.exists()
        assert dry_run_result.was_saved is False

        normal_result = writer.write_markdown_file(content, filepath, dry_run=False)
        assert filepath.exists()
        assert normal_result.was_saved is True
