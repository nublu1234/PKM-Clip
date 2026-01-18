"""
메타데이터 파서 모듈

Jina Reader API 응답(마크다운)에서 메타데이터를 추출합니다.
"""

import json
import re
from datetime import date, datetime
from typing import Any, cast
from urllib.parse import urlparse

from loguru import logger


class MetadataParser:
    """
    메타데이터 파서

    Jina Reader API 응답에서 제목, 저자, 게시일, 설명 등의 메타데이터를 추출합니다.
    """

    def parse_title(self, markdown: str | None) -> str | None:
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

    def parse_author(self, markdown: str | None) -> list[str] | None:
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

    def parse_published_date(self, markdown: str | None) -> date | None:
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

    def parse_description(self, markdown: str | None) -> str | None:
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

    def _extract_title_from_url(self, url: str | None) -> str | None:
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

    def _parse_date_string(self, date_str: str | None) -> date | None:
        """
        다양한 날짜 형식을 파싱하는 유틸리티 메서드

        지원 형식:
        - ISO 8601: 2024-09-24, 2024-09-24T14:30:00Z
        - RFC 3339: 2024-09-24T14:30:00+09:00
        - URL 경로 형식

        Args:
            date_str: 파싱할 날짜 문자열

        Returns:
            파싱된 날짜, 파싱 실패 시 None

        Examples:
            >>> _parse_date_string("2024-09-24")
            datetime.date(2024, 9, 24)
            >>> _parse_date_string("2024-09-24T14:30:00Z")
            datetime.date(2024, 9, 24)
        """
        if not date_str or not date_str.strip():
            return None

        date_str = date_str.strip()
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S.%f%z",
        ]

        for fmt in date_formats:
            try:
                parsed_datetime = datetime.strptime(date_str, fmt)
                return parsed_datetime.date()
            except ValueError:
                continue

        logger.warning(f"날짜 파싱 실패: 지원하지 않는 형식 - {date_str}")
        return None

    def _extract_jina_published_time(self, markdown: str | None) -> date | None:
        """
        jina.ai published time 추출

        마크다운 상단의 `Published: ` 라인에서 날짜를 추출합니다.

        Args:
            markdown: 마크다운 콘텐츠

        Returns:
            추출된 날짜, 실패 시 None

        Examples:
            >>> _extract_jina_published_time("Published: 2024-09-24\\n# Title")
            datetime.date(2024, 9, 24)
        """
        if not markdown or not markdown.strip():
            return None

        logger.debug("jina.ai published time 추출 시도")

        pattern = r"^Published[:：]\s*(\d{4}-\d{2}-\d{2})"
        match = re.search(pattern, markdown, re.MULTILINE)

        if match:
            date_str = match.group(1)
            parsed_date = self._parse_date_string(date_str)
            if parsed_date:
                logger.debug(f"jina.ai published time 추출 성공: {parsed_date}")
                return parsed_date

        logger.debug("jina.ai published time 추출 실패")
        return None

    def _extract_open_graph_published_time(self, markdown: str | None) -> date | None:
        """
        Open Graph published time 추출

        마크다운 메타데이터 블록에서 `article:published_time` 또는 `og:published_time`를 추출합니다.
        우선순위: article:published_time > og:published_time

        Args:
            markdown: 마크다운 콘텐츠

        Returns:
            추출된 날짜, 실패 시 None

        Examples:
            >>> _extract_open_graph_published_time("article:published_time: 2024-09-24\\n...")
            datetime.date(2024, 9, 24)
        """
        if not markdown or not markdown.strip():
            return None

        logger.debug("Open Graph published time 추출 시도")

        patterns = [
            r"^article:published_time[:：]\s*(.+)",
            r"^og:published_time[:：]\s*(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, markdown, re.MULTILINE)
            if match:
                date_str = match.group(1).strip()
                parsed_date = self._parse_date_string(date_str)
                if parsed_date:
                    logger.debug(f"Open Graph published time 추출 성공: {parsed_date}")
                    return parsed_date

        logger.debug("Open Graph published time 추출 실패")
        return None

    def _extract_schema_org_date_published(self, markdown: str | None) -> date | None:
        """
        Schema.org JSON-LD에서 datePublished 추출

        JSON-LD 형식의 Schema.org 마이크로데이터에서 `datePublished` 필드를 추출합니다.
        중첩된 구조도 지원합니다.

        Args:
            markdown: 마크다운 콘텐츠

        Returns:
            추출된 날짜, 실패 시 None

        Examples:
            >>> html = '<script type="application/ld+json">{"datePublished": "2024-09-24"}</script>'
            >>> _extract_schema_org_date_published(html)
            datetime.date(2024, 9, 24)
        """
        if not markdown or not markdown.strip():
            return None

        logger.debug("Schema.org datePublished 추출 시도")

        json_ld_pattern = r'<script\s+type="application/ld\+json">\s*({.+?})\s*</script>'
        matches = re.finditer(json_ld_pattern, markdown, re.DOTALL | re.IGNORECASE)

        for match in matches:
            json_str = match.group(1)
            try:
                json_data = json.loads(json_str)
                date_str = self._find_date_published_in_json(json_data)
                if date_str:
                    parsed_date = self._parse_date_string(date_str)
                    if parsed_date:
                        logger.debug(f"Schema.org datePublished 추출 성공: {parsed_date}")
                        return parsed_date
            except json.JSONDecodeError as e:
                logger.warning(f"JSON 파싱 실패: {e}")
                continue

        logger.debug("Schema.org datePublished 추출 실패")
        return None

    def _find_date_published_in_json(self, json_data: dict[str, Any] | list[Any]) -> str | None:
        """
        JSON 데이터에서 datePublished 필드를 재귀적으로 검색합니다.

        Args:
            json_data: JSON 데이터 (dict)

        Returns:
            datePublished 값, 찾지 못하면 None
        """
        if isinstance(json_data, dict):
            if "datePublished" in json_data:
                return cast(str, json_data["datePublished"])
            for value in json_data.values():
                result = self._find_date_published_in_json(value)
                if result:
                    return result
        elif isinstance(json_data, list):
            for item in json_data:
                result = self._find_date_published_in_json(item)
                if result:
                    return result
        return None

    def _extract_html_meta_date(self, markdown: str | None) -> date | None:
        """
        HTML meta 태그에서 date 추출

        `<meta name="date" content="...">` 형식의 HTML meta 태그에서 날짜를 추출합니다.
        다양한 속성 순서를 지원합니다.

        Args:
            markdown: 마크다운 콘텐츠

        Returns:
            추출된 날짜, 실패 시 None

        Examples:
            >>> _extract_html_meta_date('<meta name="date" content="2024-09-24" />')
            datetime.date(2024, 9, 24)
        """
        if not markdown or not markdown.strip():
            return None

        logger.debug("HTML meta 태그 date 추출 시도")

        patterns = [
            r'<meta\s+name="date"\s+content="([^"]+)"\s*/?>',
            r'<meta\s+content="([^"]+)"\s+name="date"\s*/?>',
        ]

        for pattern in patterns:
            match = re.search(pattern, markdown, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed_date = self._parse_date_string(date_str)
                if parsed_date:
                    logger.debug(f"HTML meta 태그 date 추출 성공: {parsed_date}")
                    return parsed_date

        logger.debug("HTML meta 태그 date 추출 실패")
        return None

    def _extract_date_from_url(self, url: str | None) -> date | None:
        """
        URL 경로에서 날짜 추출

        URL 경로에서 `/YYYY/MM/DD/` 패턴을 추출하여 날짜를 생성합니다.

        Args:
            url: URL 문자열

        Returns:
            추출된 날짜, 실패 시 None

        Examples:
            >>> _extract_date_from_url("https://example.com/2024/09/24/article-title")
            datetime.date(2024, 9, 24)
        """
        if not url or not url.strip():
            return None

        logger.debug(f"URL 경로 패턴에서 날짜 추출 시도: {url}")

        pattern = r"/(\d{4})/(\d{2})/(\d{2})/"
        match = re.search(pattern, url)

        if match:
            year, month, day = match.groups()
            date_str = f"{year}-{month}-{day}"
            parsed_date = self._parse_date_string(date_str)
            if parsed_date:
                logger.debug(f"URL 경로 패턴에서 날짜 추출 성공: {parsed_date}")
                return parsed_date

        logger.debug("URL 경로 패턴에서 날짜 추출 실패")
        return None

    def extract_published_date(self, markdown: str | None, url: str | None) -> date | None:
        """
        5단계 우선순위로 published 날짠를 추출합니다.

        추출 전략 (우선순위 순서):
        1. jina.ai published time
        2. Open Graph (article:published_time, og:published_time)
        3. Schema.org (datePublished)
        4. HTML meta 태그 (meta[name="date"])
        5. URL 경로 패턴 (/YYYY/MM/DD/)

        Args:
            markdown: 마크다운 콘텐츠
            url: URL (URL 경로 패턴 추출용)

        Returns:
            추출된 날짜, 모든 전략 실패 시 None

        Examples:
            >>> extract_published_date("Published: 2024-09-24\\n...", "https://example.com/article")
            datetime.date(2024, 9, 24)
        """
        if not markdown or not markdown.strip():
            logger.warning("마크다운이 비어있어 게시일을 추출할 수 없습니다.")
            return None

        strategies = [
            ("jina.ai published time", self._extract_jina_published_time, markdown),
            ("Open Graph", self._extract_open_graph_published_time, markdown),
            ("Schema.org", self._extract_schema_org_date_published, markdown),
            ("HTML meta 태그", self._extract_html_meta_date, markdown),
            ("URL 경로 패턴", self._extract_date_from_url, url),
        ]

        for strategy_name, extract_func, arg in strategies:
            logger.debug(f"{strategy_name} 전략 시도")
            extracted_date = extract_func(arg)
            if extracted_date:
                logger.info(f"게시일 추출 성공 (전략: {strategy_name}): {extracted_date}")
                return extracted_date

        logger.warning("모든 전략에서 게시일 추출 실패")
        return None
