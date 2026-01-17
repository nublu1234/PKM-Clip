"""
URL 검증 로직 단위 테스트
"""

import pytest

from src.domain.exceptions import InvalidURLError
from src.infrastructure.url_validator import validate_url


def test_valid_https_url() -> None:
    """
    유효한 HTTPS URL 검증 테스트
    """
    url = "https://example.com/article"
    result = validate_url(url)
    assert result is True


def test_valid_http_url() -> None:
    """
    유효한 HTTP URL 검증 테스트
    """
    url = "http://example.com/article"
    result = validate_url(url)
    assert result is True


def test_valid_url_with_path() -> None:
    """
    경로가 포함된 URL 검증 테스트
    """
    url = "https://example.com/path/to/article"
    result = validate_url(url)
    assert result is True


def test_valid_url_with_query_params() -> None:
    """
    쿼리 파라미터가 포함된 URL 검증 테스트
    """
    url = "https://example.com/article?param=value&other=123"
    result = validate_url(url)
    assert result is True


def test_valid_url_with_fragment() -> None:
    """
    프래그먼트가 포함된 URL 검증 테스트
    """
    url = "https://example.com/article#section"
    result = validate_url(url)
    assert result is True


def test_valid_url_with_port() -> None:
    """
    포트가 포함된 URL 검증 테스트
    """
    url = "https://example.com:8080/article"
    result = validate_url(url)
    assert result is True


def test_empty_url() -> None:
    """
    빈 URL 예외 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("")

    assert "empty" in str(exc_info.value).lower()


def test_whitespace_only_url() -> None:
    """
    공백만 있는 URL 예외 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("   ")

    assert "empty" in str(exc_info.value).lower()


def test_javascript_injection() -> None:
    """
    자바스크립트 인젝션 방지 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("javascript:alert('xss')")

    assert "dangerous" in str(exc_info.value).lower()


def test_data_url_injection() -> None:
    """
    data URL 인젝션 방지 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("data:text/html,<script>alert('xss')</script>")

    assert "dangerous" in str(exc_info.value).lower()


def test_file_scheme_url() -> None:
    """
    file 스킴 URL 거부 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("file:///path/to/file")

    assert "dangerous" in str(exc_info.value).lower() or "scheme" in str(exc_info.value).lower()


def test_ftp_scheme_url() -> None:
    """
    FTP 스킴 URL 거부 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("ftp://example.com/file")

    assert "scheme" in str(exc_info.value).lower()


def test_mailto_scheme_url() -> None:
    """
    mailto 스킴 URL 거부 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("mailto:test@example.com")

    assert "scheme" in str(exc_info.value).lower()


def test_tel_scheme_url() -> None:
    """
    tel 스킴 URL 거부 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("tel:+1234567890")

    assert "scheme" in str(exc_info.value).lower()


def test_vbscript_injection() -> None:
    """
    VBScript 인젝션 방지 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("vbscript:msgbox('xss')")

    assert "dangerous" in str(exc_info.value).lower()


def test_url_without_domain() -> None:
    """
    도메인이 없는 URL 예외 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("https:///path")

    assert "domain" in str(exc_info.value).lower()


def test_invalid_url_format() -> None:
    """
    잘못된 URL 형식 예외 테스트
    """
    with pytest.raises(InvalidURLError) as exc_info:
        validate_url("not a url")

    assert "scheme" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


def test_url_trimming() -> None:
    """
    URL 앞뒤 공백 처리 테스트
    """
    url_with_spaces = "  https://example.com/article  "
    result = validate_url(url_with_spaces)
    assert result is True


def test_mixed_case_scheme() -> None:
    """
    대소문자가 섞인 스킴 테스트
    """
    url = "HtTpS://example.com/article"
    result = validate_url(url)
    assert result is True


def test_subdomain_url() -> None:
    """
    서브도메인이 포함된 URL 테스트
    """
    url = "https://blog.example.com/article"
    result = validate_url(url)
    assert result is True


def test_url_with_special_characters_in_path() -> None:
    """
    경로에 특수 문자가 포함된 URL 테스트
    """
    url = "https://example.com/article/hello_world-test"
    result = validate_url(url)
    assert result is True


def test_idn_domain() -> None:
    """
    국제화 도메인 이름 테스트
    """
    url = "https://example.com/article"
    result = validate_url(url)
    assert result is True
