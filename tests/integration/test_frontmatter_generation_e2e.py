"""
E2E 통합 테스트

전체 URL 처리 및 Frontmatter 생성 흐름을 테스트합니다.
"""

import pytest

from src.application.models import FrontmatterOptions
from src.application.url_to_markdown_service import URLToMarkdownService
from src.domain.entities import Clipping


class TestFrontmatterGenerationE2E:
    """Frontmatter 생성 E2E 테스트"""

    @pytest.fixture
    def service(self) -> URLToMarkdownService:
        """서비스 fixture"""
        return URLToMarkdownService()

    def test_service_initialization(self, service: URLToMarkdownService):
        """서비스 초기화 테스트"""
        assert service.jina_client is not None
        assert service.frontmatter_generator is not None

    def test_service_with_default_tags(self):
        """기본 태그가 있는 서비스 초기화"""
        default_tags = ["clippings", "python"]
        service = URLToMarkdownService(default_tags=default_tags)
        assert service.default_tags == default_tags

    # 참고: 실제 API 호출은 비동기이므로 E2E 테스트에서는 mock 필요
    # 여기서는 서비스 초기화 및 기본 구조만 테스트
    # 전체 흐름 테스트는 향후 실제 API 통합 완료 후 추가 가능

    def test_service_components_exist(self, service: URLToMarkdownService):
        """서비스 구성 요소 존재 확인"""
        assert hasattr(service, "jina_client")
        assert hasattr(service, "frontmatter_generator")
        assert hasattr(service, "default_tags")

    def test_service_has_process_url_method(self, service: URLToMarkdownService):
        """process_url 메서드 존재 확인"""
        assert hasattr(service, "process_url")
        assert callable(service.process_url)
