"""
URL to Markdown 서비스 모듈

URL에서 마크다운 콘텐츠를 가져오고 Frontmatter를 생성하여 Clipping을 반환합니다.
"""

from dotenv import load_dotenv

from src.application.models import FrontmatterOptions
from src.domain.entities import Clipping
from src.domain.frontmatter_generator import FrontmatterGenerator
from src.infrastructure.config import JinaAPIConfig
from src.infrastructure.jina_reader_client import JinaReaderClient
from src.infrastructure.logger import get_logger

logger = get_logger()

# 환경 변수 로드 (JINA_API_KEY 등)
load_dotenv()


class URLToMarkdownService:
    """
    URL to Markdown 서비스

    URL에서 마크다운 콘텐츠를 가져오고 Frontmatter를 생성하여 Clipping을 반환합니다.
    """

    def __init__(
        self,
        jina_client: JinaReaderClient | None = None,
        frontmatter_generator: FrontmatterGenerator | None = None,
        default_tags: list[str] | None = None,
        config: JinaAPIConfig | None = None,
    ) -> None:
        """
        서비스 초기화

        Args:
            jina_client: Jina Reader API 클라이언트 (기본값: 새 인스턴스)
            frontmatter_generator: Frontmatter 생성기 (기본값: 새 인스턴스)
            default_tags: 기본 태그
            config: Jina API 설정 (기본값: None)
        """
        if jina_client is None:
            # config가 있는 경우 config을 전달, 없는 경우 빈 config 생성
            if config is None:
                config = JinaAPIConfig()
            self.jina_client = JinaReaderClient(config=config)
        else:
            self.jina_client = jina_client

        self.frontmatter_generator = frontmatter_generator or FrontmatterGenerator()
        self.default_tags = default_tags

    async def process_url(
        self,
        url: str,
        options: FrontmatterOptions | None = None,
    ) -> Clipping:
        """
        URL을 처리하여 Clipping을 반환합니다.

        Args:
            url: 처리할 URL
            options: CLI 옵션으로 지정된 메타데이터

        Returns:
            생성된 Clipping 엔티티
        """
        # 1. Jina Reader API로 마크다운 콘텐츠 가져오기
        logger.info(f"URL 처리 시작: {url}")
        markdown_content = await self.jina_client.fetch_markdown(url)

        # 2. Frontmatter 생성
        frontmatter = self.frontmatter_generator.generate(
            markdown_content=markdown_content,
            cli_options=options,
            default_tags=self.default_tags,
        )

        # 3. Clipping 엔티티 생성
        clipping = Clipping(
            url=url,
            frontmatter=frontmatter,
            content=markdown_content.markdown,
        )

        logger.info(f"Clipping 생성 완료: {frontmatter.title}")
        return clipping
