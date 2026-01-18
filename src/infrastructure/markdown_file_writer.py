"""
마크다운 파일 작성기 모듈

마크다운 파일을 파일 시스템에 저장합니다.
"""

from pathlib import Path

from pydantic import BaseModel

from src.domain.exceptions import FileExistsError
from src.infrastructure.file_system import FileSystem
from src.infrastructure.logger import get_logger

logger = get_logger()


class MarkdownWriteResult(BaseModel):
    """
    마크다운 파일 저장 결과
    """

    filepath: Path
    was_saved: bool
    content_size: int


class MarkdownFileWriter:
    """
    마크다운 파일 작성기 클래스

    마크다운 파일을 파일 시스템에 저장합니다.
    """

    def __init__(self) -> None:
        """MarkdownFileWriter 초기화"""
        self.file_system = FileSystem()

    def write_markdown_file(
        self,
        content: str,
        filepath: Path,
        force: bool = False,
        dry_run: bool = False,
    ) -> MarkdownWriteResult:
        """
        마크다운 파일을 저장합니다.

        Args:
            content: 저장할 마크다운 콘텐츠
            filepath: 저장할 파일 경로
            force: 파일이 존재할 때 덮어쓸지 여부 (기본값: False)
            dry_run: 실제 저장하지 않고 결과만 반환 (기본값: False)

        Returns:
            MarkdownWriteResult: 저장 결과 정보

        Raises:
            FileExistsError: 파일이 존재하고 force=False일 때
            DiskSpaceError: 디스크 공간이 부족할 때
            PermissionError: 쓰기 권한이 없을 때
        """
        # 콘텐츠 크기 계산
        content_size = len(content.encode("utf-8"))

        # dry-run 모드인 경우 파일 저장 없이 결과 반환
        if dry_run:
            logger.info(f"DRY-RUN 모드: 파일 저장 건너뜀: {filepath}")
            return MarkdownWriteResult(
                filepath=filepath,
                was_saved=False,
                content_size=content_size,
            )

        # 디렉토리가 존재하는지 확인하고 없으면 생성
        self.file_system.ensure_directory(filepath.parent)

        # 파일 존재 확인
        if self.file_system.file_exists(filepath) and not force:
            logger.warning(f"파일 이미 존재함: {filepath}")
            raise FileExistsError(
                f"File already exists: {filepath}. Use --force option to overwrite."
            )

        # 문자열을 bytes로 변환하여 저장
        content_bytes = content.encode("utf-8")

        try:
            self.file_system.save_file(content_bytes, filepath)
            logger.info(f"마크다운 파일 저장 완료: {filepath}")
            return MarkdownWriteResult(
                filepath=filepath,
                was_saved=True,
                content_size=content_size,
            )
        except Exception as e:
            logger.error(f"마크다운 파일 저장 실패: {filepath} - {e}")
            raise
