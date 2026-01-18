"""
파일명 생성기 모듈

제목에서 파일명을 생성하고 정규화합니다.
"""

import re
from typing import Final

from src.infrastructure.logger import get_logger

logger = get_logger()

# 파일 시스템에서 허용되지 않는 문자들
INVALID_CHARS: Final = r'[\\/:"*?"<>|]'
# 최대 파일명 길이 (OS 제약 고려)
MAX_FILENAME_LENGTH: Final = 200
# 빈 파일명의 기본값
DEFAULT_FILENAME: Final = "untitled"


class FilenameGenerator:
    """
    파일명 생성기 클래스

    제목에서 파일명을 생성하고 정규화합니다.
    """

    def generate_filename(
        self,
        title: str,
        custom_filename: str | None = None,
    ) -> str:
        """
        제목 또는 사용자 지정 파일명에서 파일명을 생성합니다.

        Args:
            title: 문서 제목
            custom_filename: 사용자 지정 파일명 (선택)

        Returns:
            정규화된 파일명 (.md 확장자 제외)

        Example:
            >>> generator = FilenameGenerator()
            >>> generator.generate_filename("Hello: World!")
            'Hello_ World'
            >>> generator.generate_filename("Test", "custom-name")
            'custom-name'
        """
        # 사용자 지정 파일명이 우선
        if custom_filename:
            filename = custom_filename
            logger.debug(f"사용자 지정 파일명 사용: {custom_filename}")
        else:
            filename = title
            logger.debug(f"제목에서 파일명 생성: {title}")

        # 파일명 정규화
        normalized = self._normalize_filename(filename)

        logger.debug(f"파일명 생성 완료: {normalized}")

        return normalized

    def _normalize_filename(self, filename: str) -> str:
        r"""
        파일명을 정규화합니다.

        정규화 규칙:
        1. 파일 시스템에서 허용되지 않는 문자 치환: / \ : * ? " < > | → _
        2. 연속된 언더스코어 축소: __ → _
        3. 선행/후행 언더스코어 및 공백 제거
        4. 길이 제한: 최대 200자
        5. 빈 문자열 처리: "untitled" 기본값

        Args:
            filename: 원본 파일명

        Returns:
            정규화된 파일명
        """
        if not filename:
            logger.debug("빈 파일명, 기본값 사용")
            return DEFAULT_FILENAME

        # 1. 허용되지 않는 문자 치환
        normalized = re.sub(INVALID_CHARS, "_", filename)

        # 2. 연속된 언더스코어 축소
        normalized = re.sub(r"__+", "_", normalized)

        # 3. 선행/후행 언더스코어 및 공백 제거
        normalized = normalized.strip("_ \t\n\r")

        # 4. 길이 제한
        if len(normalized) > MAX_FILENAME_LENGTH:
            original_length = len(normalized)
            normalized = normalized[:MAX_FILENAME_LENGTH].strip("_ ")
            logger.debug(f"파일명 길이 제한: {original_length} → {len(normalized)} 자")

        # 5. 빈 문자열 처리
        if not normalized:
            logger.debug("정규화 후 빈 문자열, 기본값 사용")
            normalized = DEFAULT_FILENAME

        return normalized
