"""
URL to Markdown Service 통합 테스트

서비스의 전체 흐름을 테스트합니다.
"""


import pytest

from src.application.url_to_markdown_service import URLToMarkdownService


class TestURLToMarkdownService:
    """URLToMarkdownService 통합 테스트"""

    @pytest.fixture
    def service(self) -> URLToMarkdownService:
        """서비스 fixture"""
        return URLToMarkdownService()

    @pytest.mark.asyncio
    async def test_process_url_with_metadata(self, service: URLToMarkdownService):
        """메타데이터가 있는 URL 처리"""
        # 실제 API 호출을 피하기 위해 mock을 사용해야 하지만,
        # 현재는 통합 테스트의 구조만 확인
        pass

    def test_service_initialization(self):
        """서비스 초기화 테스트"""
        service = URLToMarkdownService()
        assert service.jina_client is not None
        assert service.frontmatter_generator is not None
        assert service.default_tags is None

    def test_service_with_default_tags(self):
        """기본 태그가 있는 서비스 초기화"""
        default_tags = ["clippings", "python"]
        service = URLToMarkdownService(default_tags=default_tags)
        assert service.default_tags == default_tags
