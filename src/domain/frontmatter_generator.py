"""
Frontmatter 생성기 모듈

Jina Reader API 응답에서 메타데이터를 추출하여 Frontmatter 엔티티를 생성합니다.
"""

from datetime import date

from loguru import logger

from src.application.models import FrontmatterOptions
from src.domain.entities import Frontmatter, MarkdownContent
from src.infrastructure.metadata_parser import MetadataParser


class FrontmatterGenerator:
    """
    Frontmatter 생성기

    Jina Reader API 응답에서 메타데이터를 추출하고,
    CLI 옵션과 병합하여 Frontmatter 엔티티를 생성합니다.
    """

    def __init__(self) -> None:
        """
        Frontmatter 생성기 초기화
        """
        self.parser = MetadataParser()

    def generate(
        self,
        markdown_content: MarkdownContent,
        cli_options: FrontmatterOptions | None = None,
        default_tags: list[str] | None = None,
    ) -> Frontmatter:
        """
        Frontmatter 생성

        CLI 옵션이 우선순위를 가지며, CLI 옵션이 없는 경우
        Jina Reader API 응답에서 자동으로 메타데이터를 추출합니다.

        Args:
            markdown_content: Jina Reader API 응답
            cli_options: CLI 옵션으로 지정된 메타데이터
            default_tags: 설정 파일의 기본 태그

        Returns:
            생성된 Frontmatter 엔티티
        """
        cli_options = cli_options or FrontmatterOptions()
        default_tags = default_tags or []

        # 1. CLI 옵션 우선순위로 메타데이터 결정
        title = self._get_title(markdown_content, cli_options)
        author = self._get_author(markdown_content, cli_options)
        published = self._get_published_date(markdown_content, cli_options)
        description = self._get_description(markdown_content, cli_options)
        tags = self._get_tags(cli_options, default_tags)

        # 2. Frontmatter 엔티티 생성
        frontmatter = Frontmatter(
            title=title,
            source=markdown_content.url,
            author=author,
            published=published,
            description=description,
            tags=tags,
        )

        # 3. 로깅
        logger.info(
            f"메타데이터 추출 완료 - 제목: {frontmatter.title}, "
            f"저자: {frontmatter.author}, 게시일: {frontmatter.published}, "
            f"태그: {frontmatter.tags}"
        )

        return frontmatter

    def _get_title(
        self,
        markdown_content: MarkdownContent,
        cli_options: FrontmatterOptions,
    ) -> str:
        """
        제목 가져오기 (CLI 옵션 우선)

        Args:
            markdown_content: Jina Reader API 응답
            cli_options: CLI 옵션

        Returns:
            제목
        """
        if cli_options.title:
            logger.debug(f"CLI 옵션에서 제목 사용: {cli_options.title}")
            return cli_options.title

        # 마크다운에서 추출
        title = self.parser.parse_title(markdown_content.markdown)
        if title:
            return title

        # URL에서 추출
        logger.warning("제목을 찾을 수 없습니다. URL에서 추출을 시도합니다.")
        title = self.parser._extract_title_from_url(markdown_content.url)
        if title:
            return title

        # 기본값
        logger.warning("제목을 설정하지 못했습니다. 기본값을 사용합니다.")
        return "Untitled Clipping"

    def _get_author(
        self,
        markdown_content: MarkdownContent,
        cli_options: FrontmatterOptions,
    ) -> list[str] | None:
        """
        저자 가져오기 (CLI 옵션 우선)

        Args:
            markdown_content: Jina Reader API 응답
            cli_options: CLI 옵션

        Returns:
            저자 리스트
        """
        if cli_options.author:
            author_str = cli_options.author
            # 쉼표로 구분된 여러 저자 처리
            authors = [a.strip() for a in author_str.split(",") if a.strip()]
            logger.debug(f"CLI 옵션에서 저자 사용: {authors}")
            return authors

        author = self.parser.parse_author(markdown_content.markdown)
        if author:
            logger.debug(f"마크다운에서 저자 추출: {author}")
            return author

        return None

    def _get_published_date(
        self,
        markdown_content: MarkdownContent,
        cli_options: FrontmatterOptions,
    ) -> date | None:
        """
        게시일 가져오기 (CLI 옵션 우선)

        CLI 옵션 없는 경우 5단계 우선순위 전략으로 추출합니다:
        1. jina.ai published time
        2. Open Graph (article:published_time, og:published_time)
        3. Schema.org (datePublished)
        4. HTML meta 태그 (meta[name="date"])
        5. URL 경로 패턴 (/YYYY/MM/DD/)

        Args:
            markdown_content: Jina Reader API 응답
            cli_options: CLI 옵션

        Returns:
            게시일
        """
        if cli_options.published:
            try:
                published = date.fromisoformat(cli_options.published)
                logger.debug(f"CLI 옵션에서 게시일 사용: {published}")
                return published
            except ValueError:
                # Pydantic 유효성 검증에서 이미 처리됨
                return None

        # 5단계 우선순위 추출 전략 사용
        parsed_date = self.parser.extract_published_date(
            markdown_content.markdown, markdown_content.url
        )
        if parsed_date:
            return parsed_date

        return None

    def _get_description(
        self,
        markdown_content: MarkdownContent,
        cli_options: FrontmatterOptions,
    ) -> str | None:
        """
        설명 가져오기 (CLI 옵션 우선)

        Args:
            markdown_content: Jina Reader API 응답
            cli_options: CLI 옵션

        Returns:
            설명
        """
        if cli_options.description:
            logger.debug(f"CLI 옵션에서 설명 사용: {cli_options.description}")
            return cli_options.description

        description = self.parser.parse_description(markdown_content.markdown)
        if description:
            logger.debug(f"마크다운에서 설명 추출: {description}")
            return description

        return None

    def _get_tags(
        self,
        cli_options: FrontmatterOptions,
        default_tags: list[str],
    ) -> list[str]:
        """
        태그 가져오기 (기본 태그와 CLI 태그 병합)

        Args:
            cli_options: CLI 옵션
            default_tags: 기본 태그

        Returns:
            태그 리스트
        """
        # 기본 태그 + CLI 태그 병합
        tags = default_tags.copy()
        tags.extend(cli_options.tags)

        # 중복 제거
        unique_tags = list(dict.fromkeys(tags).keys())

        logger.debug(f"적용된 태그: {unique_tags}")
        return unique_tags
