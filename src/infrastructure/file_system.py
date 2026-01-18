"""
파일 시스템 유틸리티 모듈

디렉토리 생성, 파일 존재 확인 등 파일 시스템 작업을 담당합니다.
"""

from pathlib import Path

from src.domain.exceptions import DiskSpaceError
from src.infrastructure.logger import get_logger

logger = get_logger()


class FileSystem:
    """
    파일 시스템 유틸리티 클래스

    디렉토리 생성, 파일 존재 확인, 디스크 공간 확인 등의 작업을 수행합니다.
    """

    @staticmethod
    def ensure_directory(path: str | Path) -> Path:
        """
        디렉토리가 존재하지 않으면 생성합니다.

        Args:
            path: 디렉토리 경로

        Returns:
            생성된 Path 객체
        """
        dir_path = Path(path).expanduser().absolute()

        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"디렉토리 생성됨: {dir_path}")
            except OSError as e:
                logger.error(f"디렉토리 생성 실패: {dir_path} - {e}")
                raise
        else:
            logger.debug(f"디렉토리 이미 존재함: {dir_path}")

        return dir_path

    @staticmethod
    def file_exists(filepath: str | Path) -> bool:
        """
        파일이 존재하는지 확인합니다.

        Args:
            filepath: 파일 경로

        Returns:
            파일 존재 여부
        """
        file_path = Path(filepath).expanduser().absolute()
        return file_path.exists() and file_path.is_file()

    @staticmethod
    def save_file(content: bytes, filepath: str | Path) -> None:
        """
        파일을 디스크에 저장합니다.

        Args:
            content: 저장할 파일 내용 (bytes)
            filepath: 저장할 파일 경로

        Raises:
            DiskSpaceError: 디스크 공간이 부족할 때
        """
        file_path = Path(filepath).expanduser().absolute()

        # 부모 디렉토리가 존재하는지 확인
        if not file_path.parent.exists():
            FileSystem.ensure_directory(file_path.parent)

        # 디스크 공간 확인 (현재 플랫폼에서는 기본적으로 체크하고
        # 실제 쓰기 시 에러가 발생하면 예외 처리)
        try:
            with open(file_path, "wb") as f:
                f.write(content)
            logger.debug(f"파일 저장됨: {file_path} ({len(content)} bytes)")
        except OSError as e:
            logger.error(f"파일 저장 실패: {file_path} - {e}")
            raise DiskSpaceError(f"Failed to save file. Disk space may be insufficient: {e}")
