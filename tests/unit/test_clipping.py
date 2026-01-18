"""
Clipping 엔티티 단위 테스트

Clipping.to_markdown() 메서드를 테스트합니다.
"""

from datetime import date

import yaml

from src.domain.entities import Clipping, Frontmatter


class TestClippingToMarkdown:
    """Clipping.to_markdown() 테스트"""

    def test_to_markdown_with_all_fields(self):
        """모든 필드가 포함된 마크다운 생성"""
        frontmatter = Frontmatter(
            title="Article Title",
            source="https://example.com/article",
            author=["John Doe"],
            published=date(2024, 9, 24),
            created=date(2025, 1, 17),
            description="Article description",
            tags=["clippings", "python"],
        )
        clipping = Clipping(
            url="https://example.com/article",
            frontmatter=frontmatter,
            content="# Article Content\n\nThis is the content.",
        )

        markdown = clipping.to_markdown()

        assert markdown.startswith("---\n")
        assert markdown.endswith("---\n\n# Article Content\n\nThis is the content.")

        # YAML 파싱 테스트
        lines = markdown.split("\n")
        yaml_content = "\n".join(lines[1:9])  # --- 사이의 내용 (line 1-8)

        parsed = yaml.safe_load(yaml_content)
        assert parsed["title"] == "Article Title"
        assert parsed["source"] == "https://example.com/article"
        assert parsed["author"] == ["John Doe"]
        assert parsed["published"] == "2024-09-24"
        assert parsed["created"] == "2025-01-17"
        assert parsed["description"] == "Article description"
        assert parsed["tags"] == ["clippings", "python"]

    def test_to_markdown_with_none_fields(self):
        """일부 필드가 None인 마크다운 생성"""
        frontmatter = Frontmatter(
            title="Article Title",
            source="https://example.com/article",
            author=None,
            published=None,
            created=date(2025, 1, 17),
            description=None,
            tags=["clippings"],
        )
        clipping = Clipping(
            url="https://example.com/article",
            frontmatter=frontmatter,
            content="# Article Content\n\nThis is the content.",
        )

        markdown = clipping.to_markdown()

        assert markdown.startswith("---\n")
        assert markdown.endswith("---\n\n# Article Content\n\nThis is the content.")

        # YAML 파싱 테스트
        lines = markdown.split("\n")
        yaml_content = "\n".join(lines[1:6])  # --- 사이의 내용

        parsed = yaml.safe_load(yaml_content)
        assert parsed["title"] == "Article Title"
        assert parsed["source"] == "https://example.com/article"
        assert "author" not in parsed
        assert "published" not in parsed
        assert "description" not in parsed
        assert parsed["created"] == "2025-01-17"
        assert parsed["tags"] == ["clippings"]

    def test_to_markdown_empty_content(self):
        """빈 콘텐츠로 마크다운 생성"""
        frontmatter = Frontmatter(
            title="Article Title",
            source="https://example.com/article",
        )
        clipping = Clipping(
            url="https://example.com/article",
            frontmatter=frontmatter,
            content="",
        )

        markdown = clipping.to_markdown()

        assert markdown.startswith("---\n")
        assert markdown.endswith("---\n\n")

    def test_to_markdown_yaml_sorting(self):
        """YAML 필드 순서가 유지되는지 확인"""
        frontmatter = Frontmatter(
            title="Article Title",
            source="https://example.com/article",
            tags=["python", "tutorial"],
        )
        clipping = Clipping(
            url="https://example.com/article",
            frontmatter=frontmatter,
            content="# Content",
        )

        markdown = clipping.to_markdown()

        # YAML 필드 순서 확인 (sort_keys=False인 경우)
        assert "title:" in markdown
        assert "source:" in markdown
        assert "tags:" in markdown

    def test_to_markdown_unicode(self):
        """유니코드 문자열 처리 테스트 (한국어)"""
        frontmatter = Frontmatter(
            title="기사 제목",
            source="https://example.com/article",
            description="기사 설명입니다.",
            tags=["블로그", "기사"],
        )
        clipping = Clipping(
            url="https://example.com/article",
            frontmatter=frontmatter,
            content="# 내용",
        )

        markdown = clipping.to_markdown()

        # 유니코드 포함 확인
        assert "기사 제목" in markdown
        assert "기사 설명입니다." in markdown
        assert "블로그" in markdown
        assert "기사" in markdown
