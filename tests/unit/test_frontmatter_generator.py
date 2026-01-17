"""
FrontmatterGenerator 단위 테스트

Frontmatter 생성기의 각 메서드를 테스트합니다.
"""

from datetime import date

from src.application.models import FrontmatterOptions
from src.domain.entities import MarkdownContent
from src.domain.frontmatter_generator import FrontmatterGenerator


class TestFrontmatterGenerator:
    """FrontmatterGenerator 테스트"""

    def test_generate_all_metadata(self):
        """모든 메타데이터가 추출된 경우"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown=(
                "# Article Title\n\nAuthor: John Doe\n\nArticle description here.\n\nContent..."
            ),
        )
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(
            markdown_content,
            default_tags=["clippings"],
        )

        assert frontmatter.title == "Article Title"
        assert frontmatter.author == ["John Doe"]
        assert frontmatter.source == "https://example.com/article"
        assert frontmatter.published is None
        assert frontmatter.description == "Article description here."
        assert frontmatter.tags == ["clippings"]

    def test_generate_with_default_tags(self):
        """기본 태그가 있는 경우"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Article Title\n\nContent...",
        )
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(
            markdown_content,
            default_tags=["clippings", "python"],
        )

        assert frontmatter.title == "Article Title"
        assert frontmatter.tags == ["clippings", "python"]

    def test_cli_options_override_title(self):
        """CLI 옵션으로 제목 오버라이드"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Original Title\n\nContent...",
        )
        cli_options = FrontmatterOptions(title="Custom Title")
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(markdown_content, cli_options=cli_options)

        assert frontmatter.title == "Custom Title"

    def test_cli_options_override_author(self):
        """CLI 옵션으로 저자 오버라이드"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Title\n\nAuthor: Original Author\n\nContent...",
        )
        cli_options = FrontmatterOptions(author="Custom Author")
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(markdown_content, cli_options=cli_options)

        assert frontmatter.author == ["Custom Author"]

    def test_cli_options_override_published(self):
        """CLI 옵션으로 게시일 오버라이드"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Title\n\nPublished: 2024-09-24\n\nContent...",
        )
        cli_options = FrontmatterOptions(published="2024-01-01")
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(markdown_content, cli_options=cli_options)

        assert frontmatter.published == date(2024, 1, 1)

    def test_cli_options_add_tags(self):
        """CLI 옵션으로 태그 추가"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Title\n\nContent...",
        )
        cli_options = FrontmatterOptions(tags=["python", "tutorial"])
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(
            markdown_content,
            cli_options=cli_options,
            default_tags=["clippings"],
        )

        assert frontmatter.tags == ["clippings", "python", "tutorial"]

    def test_title_fallback_to_url(self):
        """제목이 없는 경우 URL에서 추출"""
        markdown_content = MarkdownContent(
            url="https://example.com/2024/09/24/article-title",
            markdown="Just content without a title...",
        )
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(markdown_content)

        assert frontmatter.title == "Article Title"

    def test_title_fallback_to_default(self):
        """제목이 없고 URL에서도 추출되지 않는 경우 기본값"""
        markdown_content = MarkdownContent(
            url="https://example.com",
            markdown="Just content without a title...",
        )
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(markdown_content)

        assert frontmatter.title == "Untitled Clipping"

    def test_missing_metadata_fields(self):
        """일부 메타데이터가 누락된 경우 (제목만 있는 경우)"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Article Title\n\n",
        )
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(
            markdown_content,
            default_tags=["clippings"],
        )

        assert frontmatter.title == "Article Title"
        assert frontmatter.author is None
        assert frontmatter.published is None
        assert frontmatter.description is None
        assert frontmatter.tags == ["clippings"]

    def test_empty_cli_options(self):
        """빈 CLI 옵션"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Article Title\n\nAuthor: John Doe\n\nPublished: 2024-09-24\n\nContent...",
        )
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(markdown_content, cli_options=None)

        assert frontmatter.title == "Article Title"
        assert frontmatter.author == ["John Doe"]
        assert frontmatter.published == date(2024, 9, 24)

    def test_multiple_authors_from_cli(self):
        """CLI 옵션에서 여러 저자"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Title\n\nContent...",
        )
        cli_options = FrontmatterOptions(author="John Doe, Jane Smith")
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(markdown_content, cli_options=cli_options)

        assert frontmatter.author == ["John Doe", "Jane Smith"]

    def test_duplicate_tags_merged(self):
        """중복 태그 병합"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Title\n\nContent...",
        )
        cli_options = FrontmatterOptions(tags=["clippings", "python"])
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(
            markdown_content,
            cli_options=cli_options,
            default_tags=["clippings", "tutorial"],
        )

        assert frontmatter.tags == ["clippings", "tutorial", "python"]

    def test_created_date_always_today(self):
        """생성일은 항상 오늘 날짜"""
        markdown_content = MarkdownContent(
            url="https://example.com/article",
            markdown="# Title\n\nContent...",
        )
        generator = FrontmatterGenerator()

        frontmatter = generator.generate(markdown_content)

        assert frontmatter.created == date.today()
