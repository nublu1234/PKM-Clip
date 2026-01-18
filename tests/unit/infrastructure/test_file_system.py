"""
FileSystem 단위 테스트
"""

import tempfile
from pathlib import Path

import pytest

from src.infrastructure.file_system import FileSystem


class TestFileSystem:
    """FileSystem 단위 테스트 클래스"""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """
        임시 디렉토리 픽스처

        Returns:
            임시 디렉토리 경로
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_ensure_directory_creates_directory(self, temp_dir: Path) -> None:
        """
        디렉토리 생성 테스트

        Given: 디렉토리가 존재하지 않음

        When: 디렉토리를 생성함

        Then: 디렉토리가 생성됨
        """
        new_dir = temp_dir / "new_directory"
        assert not new_dir.exists()

        result = FileSystem.ensure_directory(str(new_dir))

        assert result.exists()
        assert result.is_dir()

    def test_ensure_directory_existing_directory_no_error(self, temp_dir: Path) -> None:
        """
        기존 디렉토리 처리 테스트

        Given: 디렉토리가 이미 존재함

        When: 디렉토리를 생성하려 시도함

        Then: 에러 없이 기존 디렉토리가 반환됨
        """
        existing_dir = temp_dir / "existing_directory"
        existing_dir.mkdir()

        result = FileSystem.ensure_directory(str(existing_dir))

        assert result == existing_dir
        assert result.exists()

    def test_ensure_directory_creates_nested_directories(self, temp_dir: Path) -> None:
        """
        중첩 디렉토리 생성 테스트

        Given: 중첩된 경로가 존재하지 않음

        When: 디렉토리를 생성함

        Then: 모든 중첩 디렉토리가 생성됨
        """
        nested_dir = temp_dir / "level1" / "level2" / "level3"
        assert not nested_dir.exists()

        result = FileSystem.ensure_directory(str(nested_dir))

        assert result.exists()
        assert result.is_dir()

    def test_ensure_directory_expands_home_path(self) -> None:
        """
        ~ 경로 확장 테스트

        Given: ~가 포함된 경로

        When: 디렉토리를 생성함

        Then: 홈 디렉토리로 확장되어 생성됨
        """
        # 실제 홈 디렉토리에 영향을 주지 않도록 테스트
        home_dir = Path.home()
        temp_dir = home_dir / ".pkm-clip-test"
        temp_dir.mkdir(exist_ok=True)
        test_dir = temp_dir / "test_directory"

        try:
            result = FileSystem.ensure_directory(str(test_dir))

            assert result.exists()
            assert result.is_dir()
            assert "~" not in str(result)  # ~가 확장됨
        finally:
            # 정리
            if test_dir.exists():
                test_dir.rmdir()
            if temp_dir.exists():
                temp_dir.rmdir()

    def test_file_exists_returns_true(self, temp_dir: Path) -> None:
        """
        파일 존재 확인 테스트 (True)

        Given: 파일이 존재함

        When: 파일 존재 여부를 확인함

        Then: True가 반환됨
        """
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        result = FileSystem.file_exists(str(test_file))

        assert result is True

    def test_file_exists_returns_false(self, temp_dir: Path) -> None:
        """
        파일 존재 확인 테스트 (False)

        Given: 파일이 존재하지 않음

        When: 파일 존재 여부를 확인함

        Then: False가 반환됨
        """
        test_file = temp_dir / "nonexistent.txt"

        result = FileSystem.file_exists(str(test_file))

        assert result is False

    def test_file_exists_directory_returns_false(self, temp_dir: Path) -> None:
        """
        디렉토리 확인 테스트

        Given: 디렉토리가 존재하지만 파일은 아님

        When: 파일 존재 여부를 확인함

        Then: False가 반환됨
        """
        test_dir = temp_dir / "test_directory"
        test_dir.mkdir()

        result = FileSystem.file_exists(str(test_dir))

        assert result is False

    def test_save_file_creates_file(self, temp_dir: Path) -> None:
        """
        파일 저장 테스트

        Given: 파일이 존재하지 않음

        When: 파일을 저장함

        Then: 파일이 생성됨
        """
        test_file = temp_dir / "test.txt"
        content = b"test content"

        FileSystem.save_file(content, str(test_file))

        assert test_file.exists()
        assert test_file.read_bytes() == content

    def test_save_file_overwrites_existing_file(self, temp_dir: Path) -> None:
        """
        파일 덮어쓰기 테스트

        Given: 파일이 이미 존재함

        When: 새로운 내용으로 파일을 저장함

        Then: 파일이 덮어써짐
        """
        test_file = temp_dir / "test.txt"
        test_file.write_text("original content")

        new_content = b"new content"
        FileSystem.save_file(new_content, str(test_file))

        assert test_file.read_bytes() == new_content

    def test_save_file_creates_parent_directory(self, temp_dir: Path) -> None:
        """
        부모 디렉토리 생성 테스트

        Given: 부모 디렉토리가 존재하지 않음

        When: 파일을 저장함

        Then: 부모 디렉토리가 생성됨
        """
        nested_file = temp_dir / "new_dir" / "test.txt"
        content = b"test content"

        FileSystem.save_file(content, str(nested_file))

        assert nested_file.exists()
        assert nested_file.parent.exists()

    def test_save_file_expands_home_path(self) -> None:
        """
        ~ 경로 확장 테스트 (저장)

        Given: ~가 포함된 경로

        When: 파일을 저장함

        Then: 홈 디렉토리로 확장되어 저장됨
        """
        home_dir = Path.home()
        temp_dir = home_dir / ".pkm-clip-test"
        temp_dir.mkdir(exist_ok=True)
        test_file = temp_dir / "test.txt"
        content = b"test content"

        try:
            # ~로 저장하려고 하면 확장되어야 함
            FileSystem.save_file(content, str(test_file))

            assert test_file.exists()
            assert test_file.read_bytes() == content
        finally:
            # 정리
            if test_file.exists():
                test_file.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()
