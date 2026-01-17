"""
JinaReaderClient 통합 테스트
"""

from datetime import datetime

import httpx
import pytest
import respx

from src.domain.entities import MarkdownContent
from src.domain.exceptions import (
    InvalidURLError,
    JinaReaderAPIError,
)
from src.infrastructure.config import JinaAPIConfig
from src.infrastructure.jina_reader_client import JinaReaderClient


@pytest.fixture
def mock_config() -> JinaAPIConfig:
    """
    테스트용 JinaAPIConfig 픽스처
    """
    return JinaAPIConfig(
        api_key="test_key_12345",
        base_url="https://r.jina.ai",
        headers={
            "x-with-generated-alt": False,
            "x-no-cache": False,
            "x-cache-tolerance": 3600,
            "x-respond-with": "markdown",
            "x-timeout": 20,
            "Accept": "text/event-stream",
        },
        timeout=20,
        max_retries=3,
        retry_delay=1,
        retry_multiplier=2.0,
    )


@pytest.fixture
async def client(mock_config: JinaAPIConfig) -> JinaReaderClient:
    """
    JinaReaderClient 픽스처
    """
    jina_client = JinaReaderClient(mock_config)
    yield jina_client
    await jina_client.close()


@pytest.mark.asyncio
async def test_fetch_markdown_success(
    client: JinaReaderClient, mock_config: JinaAPIConfig
) -> None:
    """
    정상적인 마크다운 변환 테스트
    """
    test_url = "https://example.com/article"
    expected_markdown = "# Test Article\n\nThis is content."

    with respx.mock:
        respx.get(f"{mock_config.base_url}/{test_url}").mock(
            return_value=httpx.Response(200, text=expected_markdown)
        )

        result = await client.fetch_markdown(test_url)

        assert result.url == test_url
        assert result.markdown == expected_markdown
        assert isinstance(result.fetched_at, datetime)


@pytest.mark.asyncio
async def test_fetch_markdown_invalid_url(
    client: JinaReaderClient,
) -> None:
    """
    유효하지 않은 URL 예외 테스트
    """
    with pytest.raises(InvalidURLError):
        await client.fetch_markdown("javascript:alert('xss')")


@pytest.mark.asyncio
async def test_fetch_markdown_empty_url(
    client: JinaReaderClient,
) -> None:
    """
    빈 URL 예외 테스트
    """
    with pytest.raises(InvalidURLError):
        await client.fetch_markdown("")


@pytest.mark.asyncio
async def test_fetch_markdown_rate_limit_429(
    client: JinaReaderClient, mock_config: JinaAPIConfig
) -> None:
    """
    Rate Limit (429) 처리 테스트
    """
    test_url = "https://example.com/rate-limited"
    expected_markdown = "# Success"

    with respx.mock:
        # 세 번째 시도 후 성공하도록 설정
        route = respx.get(f"{mock_config.base_url}/{test_url}").mock(
            side_effect=[
                httpx.Response(429, text="Rate limit exceeded"),
                httpx.Response(429, text="Rate limit exceeded"),
                httpx.Response(200, text=expected_markdown),
            ]
        )

        result = await client.fetch_markdown(test_url)

        assert result.markdown == expected_markdown


@pytest.mark.asyncio
async def test_fetch_markdown_client_error_400(
    client: JinaReaderClient, mock_config: JinaAPIConfig
) -> None:
    """
    클라이언트 에러 (400) 즉시 예외 발생 테스트
    """
    test_url = "https://example.com/bad-request"

    with respx.mock:
        respx.get(f"{mock_config.base_url}/{test_url}").mock(
            return_value=httpx.Response(400, text="Bad Request")
        )

        with pytest.raises(JinaReaderAPIError):
            await client.fetch_markdown(test_url)


@pytest.mark.asyncio
async def test_fetch_markdown_not_found_404(
    client: JinaReaderClient, mock_config: JinaAPIConfig
) -> None:
    """
    404 Not Found 예외 테스트
    """
    test_url = "https://example.com/not-found"

    with respx.mock:
        respx.get(f"{mock_config.base_url}/{test_url}").mock(
            return_value=httpx.Response(404, text="Not Found")
        )

        with pytest.raises(JinaReaderAPIError):
            await client.fetch_markdown(test_url)


@pytest.mark.asyncio
async def test_fetch_markdown_server_error_500_with_retry(
    client: JinaReaderClient, mock_config: JinaAPIConfig
) -> None:
    """
    서버 에러 (500) 재시도 후 성공 테스트
    """
    test_url = "https://example.com/server-error"
    expected_markdown = "# Recovered"

    with respx.mock:
        respx.get(f"{mock_config.base_url}/{test_url}").mock(
            side_effect=[
                httpx.Response(500, text="Internal Server Error"),
                httpx.Response(500, text="Internal Server Error"),
                httpx.Response(200, text=expected_markdown),
            ]
        )

        result = await client.fetch_markdown(test_url)

        assert result.markdown == expected_markdown


@pytest.mark.asyncio
async def test_fetch_markdown_empty_response(
    client: JinaReaderClient, mock_config: JinaAPIConfig
) -> None:
    """
    빈 응답 예외 테스트
    """
    test_url = "https://example.com/empty"

    with respx.mock:
        respx.get(f"{mock_config.base_url}/{test_url}").mock(
            return_value=httpx.Response(200, text="   ")
        )

        with pytest.raises(JinaReaderAPIError):
            await client.fetch_markdown(test_url)


@pytest.mark.asyncio
async def test_fetch_markdown_timeout(
    client: JinaReaderClient, mock_config: JinaAPIConfig
) -> None:
    """
    타임아웃 예외 테스트
    """
    test_url = "https://example.com/timeout"

    # respx는 타임아웃을 직접 모킹하기 어려우므로
    # 이 테스트에서는 타임아웃 로직이 작동하는지 확인만 함
    # 실제 타임아웃 테스트는 별도의 방법이 필요함
    # 여기서는 408 Request Timeout으로 대체

    with respx.mock:
        respx.get(f"{mock_config.base_url}/{test_url}").mock(
            return_value=httpx.Response(408, text="Request Timeout")
        )

        with pytest.raises(JinaReaderAPIError):
            await client.fetch_markdown(test_url)


@pytest.mark.asyncio
async def test_prepare_api_url_encoding(
    client: JinaReaderClient,
) -> None:
    """
    API URL 인코딩 테스트
    """
    test_url = "https://example.com/path?param=value&other=hello world"
    api_url = client._prepare_api_url(test_url)

    # 공백이 인코딩되어야 함
    assert "hello%20world" in api_url or "hello+world" in api_url
    assert api_url.startswith("https://r.jina.ai/")


@pytest.mark.asyncio
async def test_prepare_api_url_simple(
    client: JinaReaderClient,
) -> None:
    """
    간단한 API URL 생성 테스트
    """
    test_url = "https://example.com/article"
    api_url = client._prepare_api_url(test_url)

    assert api_url == "https://r.jina.ai/https://example.com/article"


@pytest.mark.asyncio
async def test_client_context_manager(
    mock_config: JinaAPIConfig,
) -> None:
    """
    비동기 컨텍스트 매니저 테스트
    """
    async with JinaReaderClient(mock_config) as ctx_client:
        assert ctx_client is not None


@pytest.mark.asyncio
async def test_parse_retry_after_header(
    client: JinaReaderClient,
) -> None:
    """
    Retry-After 헤더 파싱 테스트
    """
    assert client._parse_retry_after("30") == 30
    assert client._parse_retry_after("5") == 5
    assert client._parse_retry_after(None) is None
    assert client._parse_retry_after("") is None
    assert client._parse_retry_after("invalid") is None


@pytest.mark.asyncio
async def test_prepare_headers_includes_auth(
    mock_config: JinaAPIConfig,
) -> None:
    """
    Authorization 헤더 포함 테스트
    """
    client = JinaReaderClient(mock_config)
    headers = client._prepare_headers()

    assert "Authorization" in headers
    assert headers["Authorization"] == f"Bearer {mock_config.api_key}"

    await client.close()


@pytest.mark.asyncio
async def test_markdown_content_validation(
    client: JinaReaderClient,
) -> None:
    """
    MarkdownContent 유효성 검증 테스트
    """
    url = "https://example.com/article"
    markdown = "# Test\n\nContent"

    content = MarkdownContent(url=url, markdown=markdown)

    assert content.url == url
    assert content.markdown == markdown
    assert content.fetched_at is not None
