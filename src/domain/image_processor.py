"""
이미지 처리 도메인 모듈

마크다운 내 이미지 URL 추출, 파일명 생성, Obsidian 참조 변환을 담당합니다.
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict


class ImageProcessor:
    """
    이미지 처리 클래스

    마크다운 내 이미지 URL 추출, 파일명 생성, Obsidian 참조 변환을 수행합니다.
    """

    # 표준 마크다운 이미지 문법: ![alt](url)
    MARKDOWN_IMAGE_PATTERN = r"!\[.*?\]\((https?://[^\s)]+)\)"

    # HTML img 태그: <img src="url" ...> 전체 태그 매칭
    HTML_IMAGE_PATTERN = r'<img[^>]+src=["\'](https?://[^"\']+)["\'][^>]*>'

    # 파일 크기 제한 (10MB)
    MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

    def __init__(self, max_image_size_bytes: int = MAX_IMAGE_SIZE_BYTES) -> None:
        """
        이미지 처리 초기화

        Args:
            max_image_size_bytes: 최대 이미지 크기 (기본값: 10MB)
        """
        self.max_image_size_bytes = max_image_size_bytes

    def extract_image_urls(self, markdown: str) -> list[str]:
        """
        마크다운 콘텐츠에서 모든 이미지 URL을 추출합니다.

        표준 마크다운 이미지 문법과 HTML img 태그 모두 지원합니다.

        Args:
            markdown: 마크다운 콘텐츠

        Returns:
            추출된 이미지 URL 목록 (중복 제거됨)
        """
        # 표준 마크다운 이미지 문법 추출
        markdown_urls = re.findall(self.MARKDOWN_IMAGE_PATTERN, markdown)

        # HTML img 태그 추출
        html_urls = re.findall(self.HTML_IMAGE_PATTERN, markdown)

        # 중복 제거 (set 사용)
        all_urls = list(set(markdown_urls + html_urls))

        return all_urls

    def generate_filename(self, url: str) -> str:
        """
        이미지 URL에서 유일한 파일명을 생성합니다.

        형식: YYYYMMDD_HHMMSS_{hash}.{extension}

        Args:
            url: 이미지 URL

        Returns:
            생성된 파일명
        """
        # 현재 시간으로 timestamp 생성 (YYYYMMDD_HHMMSS)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # URL에서 SHA-256 해시 생성 (첫 8자)
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:8]

        # URL에서 확장자 추출
        extension = self._extract_extension(url)

        # 파일명 조합: timestamp_hash.extension
        filename = f"{timestamp}_{url_hash}.{extension}"

        return filename

    def _extract_extension(self, url: str) -> str:
        """
        URL에서 파일 확장자를 추출합니다.

        Args:
            url: 이미지 URL

        Returns:
            파일 확장자 (예: png, jpg)
        """
        # URL에서 경로 부분 추출
        parsed_url = Path(url)
        # 확장자 추출 (앞의 점 제거)
        extension = parsed_url.suffix.lstrip(".")

        # 확장자가 없거나 비표준인 경우 기본값으로 png 설정
        if not extension or len(extension) > 5:
            extension = "png"

        # 소문자로 변환
        return extension.lower()

    def replace_with_obsidian_reference(
        self, markdown: str, url_to_filename: Dict[str, str]
    ) -> str:
        """
        마크다운 내 이미지 참조를 Obsidian 방식으로 변환합니다.

        표준 마크다운: ![alt](url) → Obsidian: ![[filename]]
        HTML img 태그: <img src="url"> → ![[filename]]

        Args:
            markdown: 마크다운 콘텐츠
            url_to_filename: URL에서 파일명으로의 매핑 딕셔너리

        Returns:
            변환된 마크다운 콘텐츠
        """

        # 표준 마크다운 이미지 문법 변환
        def replace_markdown_image(match: re.Match) -> str:
            url = match.group(1)
            if url in url_to_filename:
                return f"![[{url_to_filename[url]}]]"
            return match.group(0)

        result = re.sub(self.MARKDOWN_IMAGE_PATTERN, replace_markdown_image, markdown)

        # HTML img 태그 변환
        def replace_html_image(match: re.Match) -> str:
            url = match.group(1)
            if url in url_to_filename:
                return f"![[{url_to_filename[url]}]]"
            return match.group(0)

        result = re.sub(self.HTML_IMAGE_PATTERN, replace_html_image, result)

        return result

    def validate_image_size(self, size: int) -> None:
        """
        이미지 크기가 제한을 초과하는지 검증합니다.

        Args:
            size: 이미지 크기 (bytes)

        Raises:
            ImageSizeExceededError: 이미지 크기가 제한을 초과할 때
        """
        if size > self.max_image_size_bytes:
            from src.domain.exceptions import ImageSizeExceededError

            raise ImageSizeExceededError(
                f"Image size ({size} bytes) exceeds the maximum limit ({self.max_image_size_bytes} bytes)"
            )
