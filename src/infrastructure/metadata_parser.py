"""
메타데이터 파서 모듈

Jina Reader API 응답(마크다운)에서 메타데이터를 추출합니다.
"""

import re
from datetime import date, datetime
from urllib.parse import urlparse

from loguru import logger


class MetadataParser:
    """
    메타데이터 파서

    Jina Reader API 응답에서 제목, 저자, 게시일, 설명 등의 메타데이터를 추출합니다.
    """

    def parse_title(self, markdown: str) -> str | None:
        """
        마크다운의 첫 번째 h1 태그에서 제목을 추출합니다.

        Args:
            markdown: 마크다운 콘텐츠

        Returns:
            추출된 제목, 없을 경우 None
        """
        if not markdown or not markdown.strip():
            logger.warning("마크다운이 비어있어 제목을 추출할 수 없습니다.")
            return None

        lines = markdown.strip().split("\n")

        for line in lines:
            stripped_line = line.strip()

            # h1 제목 형식 (# Title) 찾기
            if stripped_line.startswith("# "):
                title = stripped_line[2:].strip()
                logger.debug(f"제목 추출 성공: {title}")
                return title

        logger.debug("제목(h1)을 찾을 수 없습니다.")
        return None

    def parse_author(self, markdown: str) -> list[str] | None:
        """
        마크다운에서 저자 정보를 추출합니다.

        여러 형식을 지원합니다:
        - "Author: John Doe"
        - "저자: 홍길동"
        - "By John Doe"

        Args:
            markdown: 마크다운 콘텐츠

        Returns:
            추출된 저자 리스트, 없을 경우 None
        """
        if not markdown or not markdown.strip():
            return None

        patterns = [
            r"Author[:：]\s*(.+?)(?:\n|$)",
            r"저자[:：]\s*(.+?)(?:\n|$)",
            r"By\s+(.+?)(?:\n|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, markdown, re.IGNORECASE)
            if match:
                author_str = match.group(1).strip()
                # 쉼표로 구분된 여러 저자 처리
                authors = [a.strip() for a in author_str.split(",") if a.strip()]
                if authors:
                    logger.debug(f"저자 추출 성공: {authors}")
                    return authors

        logger.debug("저자 정보를 찾을 수 없습니다.")
        return None

    def parse_published_date(self, markdown: str) -> date | None:
        """
        마크다운에서 게시일을 추출합니다.

        여러 날짜 형식을 지원합니다:
        - YYYY-MM-DD
        - Published: 2024-09-24
        - 게시일: 2024년 9월 24일

        Args:
            markdown: 마크다운 콘텐츠

        Returns:
            추출된 날짜, 파싱 실패 시 None
        """
        if not markdown or not markdown.strip():
            return None

        # 다양한 날짜 형식 패턴
        date_patterns = [
            (r"(?:Published|게시일)[:：]\s*(\d{4}-\d{2}-\d{2})", "%Y-%m-%d"),
            (r"(?:Published|게시일)[:：]\s*(\d{4}/\d{2}/\d{2})", "%Y/%m/%d"),
            (r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", "%Y%m%d"),
        ]

        for pattern, date_format in date_patterns:
            match = re.search(pattern, markdown, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                if date_format == "%Y%m%d":
                    # 연, 월, 일 그룹 처리
                    year, month, day = match.groups()
                    date_str = f"{year}{month.zfill(2)}{day.zfill(2)}"

                try:
                    parsed_date = datetime.strptime(date_str, date_format).date()
                    logger.debug(f"게시일 추출 성공: {parsed_date}")
                    return parsed_date
                except ValueError as e:
                    logger.warning(f"날짜 파싱 실패: {date_str} - {e}")
                    continue

        logger.debug("게시일을 찾을 수 없습니다.")
        return None

    def parse_description(self, markdown: str) -> str | None:
        """
        마크다운의 첫 번째 단락에서 설명을 추출합니다.

        Args:
            markdown: 마크다운 콘텐츠

        Returns:
            추출된 설명, 없을 경우 None
        """
        if not markdown or not markdown.strip():
            return None

        lines = markdown.strip().split("\n")

        # 메타데이터 패턴 (Author, Published, 게시일, 저자 등)
        metadata_patterns = [
            r"^Author[:：]",
            r"^저자[:：]",
            r"^Published[:：]",
            r"^게시일[:：]",
            r"^By\s+",
        ]

        # h1 헤더와 메타데이터 라인 건너뛰기
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line.startswith("#"):
                i += 1
                continue
            # 메타데이터 라인 건너뛰기
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in metadata_patterns):
                i += 1
                continue
            break

        # 첫 번째 비어있지 않은 단락 찾기
        while i < len(lines):
            line = lines[i].strip()
            if line:
                # 단락 끝까지 수집 (빈 라인 또는 헤더 또는 메타데이터 전까지)
                description_lines = [line]
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:
                        break
                    if next_line.startswith("#"):
                        break
                    if any(
                        re.match(pattern, next_line, re.IGNORECASE) for pattern in metadata_patterns
                    ):
                        break
                    description_lines.append(next_line)
                    i += 1

                description = " ".join(description_lines)
                # 너무 긴 설명 제한 (200자)
                if len(description) > 200:
                    description = description[:200] + "..."
                logger.debug(f"설명 추출 성공: {description}")
                return description
            i += 1

        logger.debug("설명을 찾을 수 없습니다.")
        return None

    def _extract_title_from_url(self, url: str) -> str | None:
        """
        URL 경로에서 제목을 추출합니다.

        URL의 마지막 경로 세그먼트를 사용하여 제목을 생성합니다.
        하이픈을 공백으로 변환하고, 첫 글자는 대문자로 변환합니다.

        Args:
            url: URL

        Returns:
            추출된 제목, 실패 시 None

        Examples:
            >>> _extract_title_from_url("https://example.com/2024/09/24/stop-drooling-over-user-stories")
            "Stop Drooling Over User Stories"
        """
        if not url or not url.strip():
            return None

        try:
            parsed = urlparse(url)
            path = parsed.path.strip("/")

            if not path:
                return None

            # 마지막 경로 세그먼트 추출
            segments = path.split("/")
            last_segment = segments[-1]

            if not last_segment:
                return None

            # 파일 확장자 제거
            if "." in last_segment:
                last_segment = last_segment.rsplit(".", 1)[0]

            # 하이픈을 공백으로 변환하고, 단어 첫 글자 대문자화
            title = last_segment.replace("-", " ").replace("_", " ").strip()
            title = " ".join(word.capitalize() for word in title.split())

            if title:
                logger.info(f"URL에서 제목 추출 성공: {title}")
                return title

        except Exception as e:
            logger.warning(f"URL에서 제목 추출 실패: {url} - {e}")

        return None
