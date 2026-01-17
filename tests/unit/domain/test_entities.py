"""
MarkdownContent 모델 단위 테스트
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.domain.entities import MarkdownContent


def test_markdown_content_creation() -> None:
    """
    정상적인 MarkdownContent 생성 테스트
    """
    url = "https://example.com/article"
    markdown = "# Test Article\n\nContent goes here."
    now = datetime.now(timezone.utc)

    content = MarkdownContent(url=url, markdown=markdown, fetched_at=now)

    assert content.url == url
    assert content.markdown == markdown
    assert content.fetched_at == now


def test_markdown_content_default_fetched_at() -> None:
    """
    fetched_at 기본값 테스트
    """
    url = "https://example.com/article"
    markdown = "# Test"

    content = MarkdownContent(url=url, markdown=markdown)

    assert content.fetched_at is not None
    assert isinstance(content.fetched_at, datetime)


def test_markdown_content_empty_url_validation() -> None:
    """
    빈 URL 유효성 검증 테스트
    """
    with pytest.raises(ValidationError) as exc_info:
        MarkdownContent(url="", markdown="# Test")

    assert "cannot be empty" in str(exc_info.value).lower()


def test_markdown_content_whitespace_url_validation() -> None:
    """
    공백만 있는 URL 유효성 검증 테스트
    """
    with pytest.raises(ValidationError) as exc_info:
        MarkdownContent(url="   ", markdown="# Test")

    assert "cannot be empty" in str(exc_info.value).lower()


def test_markdown_content_url_trimming() -> None:
    """
    URL 앞뒤 공백 제거 테스트
    """
    url_with_spaces = "  https://example.com/article  "
    markdown = "# Test"

    content = MarkdownContent(url=url_with_spaces, markdown=markdown)

    assert content.url == "https://example.com/article"


def test_markdown_content_empty_markdown() -> None:
    """
    빈 마크다운 콘텐츠 테스트
    """
    url = "https://example.com/article"
    markdown = ""

    content = MarkdownContent(url=url, markdown=markdown)

    assert content.markdown == markdown


def test_markdown_content_required_fields() -> None:
    """
    필드 필수성 테스트
    """
    with pytest.raises(ValidationError) as exc_info:
        MarkdownContent()

    assert exc_info.value.error_count() >= 1
