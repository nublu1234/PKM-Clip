"""
URL 검증 모듈

URL의 유효성을 검증하고 보안 문제(인젝션 등)을 방지합니다.
"""

import re
from urllib.parse import urlparse

from src.domain.exceptions import InvalidURLError

# 허용된 URL 스킴 목록 (HTTPS만 허용)
ALLOWED_SCHEMES = {"https", "http"}

# 위험한 URL 스킴 (인젝션 방지)
DANGEROUS_SCHEMES = {
    "javascript:",
    "data:",
    "vbscript:",
    "file:",
    "ftp:",
    "mailto:",
    "tel:",
}


def validate_url(url: str) -> bool:
    """
    URL이 유효한지 검증합니다.

    검증 규칙:
    1. 비어있지 않아야 함
    2. 허용된 스킴(http, https)만 사용 가능
    3. 위험한 스킴(javascript:, data: 등) 거부
    4. 유효한 형식인지 확인

    Args:
        url: 검증할 URL

    Returns:
        bool: 유효한 URL이면 True, 아니면 False

    Raises:
        InvalidURLError: 유효하지 않은 URL인 경우
    """
    if not url or not url.strip():
        raise InvalidURLError("URL cannot be empty")

    url = url.strip()

    # 위험한 스킴 체크 (인젝션 방지)
    for dangerous_scheme in DANGEROUS_SCHEMES:
        if url.lower().startswith(dangerous_scheme):
            raise InvalidURLError(f"URL contains dangerous scheme: {dangerous_scheme}")

    try:
        parsed = urlparse(url)

        # 스킴 검증
        if parsed.scheme not in ALLOWED_SCHEMES:
            raise InvalidURLError(f"URL scheme must be http or https, got: {parsed.scheme}")

        # 네트워크 위치 (netloc) 검증
        if not parsed.netloc:
            raise InvalidURLError("URL must contain a valid domain")

        # 기본적인 URL 형식 검증 (정규 표현식)
        # http:// 또는 https://로 시작하며 도메인 이름이 포함되어야 함
        url_pattern = re.compile(
            r"^https?://"  # http:// 또는 https://
            r"[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+"  # 도메인 이름 (최소 1개 점)
            r"(:[0-9]+)?"  # 옵션 포트
            r"(/.*)?$",  # 옵션 경로
            re.IGNORECASE,
        )

        if not url_pattern.match(url):
            raise InvalidURLError("URL format is invalid")

        return True

    except InvalidURLError:
        # InvalidURLError는 그대로 다시 던짐
        raise
    except Exception as e:
        # 기타 파싱 오류
        raise InvalidURLError(f"Failed to parse URL: {e}")
