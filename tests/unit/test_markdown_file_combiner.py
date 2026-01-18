"""
MarkdownFileCombiner 단위 테스트

frontmatter와 마크다운 콘텐츠 결합을 테스트합니다.
"""

from src.domain.markdown_file_combiner import MarkdownFileCombiner


class TestMarkdownFileCombiner:
    """MarkdownFileCombiner 테스트"""

    def test_combine_frontmatter_and_markdown(self):
        """기본적인 frontmatter와 마크다운 결합"""
        frontmatter = {
            "title": "Test Article",
            "source": "https://example.com",
            "tags": ["python", "tutorial"],
        }
        markdown = "# Test Article\n\nContent here..."
        combiner = MarkdownFileCombiner()

        result = combiner.combine_frontmatter_and_markdown(frontmatter, markdown)

        assert result.startswith("---")
        assert "---" in result
        assert "# Test Article" in result
        assert "Content here..." in result
        assert "title: Test Article" in result
        assert "source: https://example.com" in result

    def test_combine_empty_frontmatter(self):
        """빈 frontmatter 처리"""
        frontmatter = {}
        markdown = "# Test Article\n\nContent here..."
        combiner = MarkdownFileCombiner()

        result = combiner.combine_frontmatter_and_markdown(frontmatter, markdown)

        assert result == markdown
        assert not result.startswith("---")

    def test_combine_empty_markdown(self):
        """빈 markdown 처리"""
        frontmatter = {"title": "Test"}
        markdown = ""
        combiner = MarkdownFileCombiner()

        result = combiner.combine_frontmatter_and_markdown(frontmatter, markdown)

        assert result.startswith("---")
        assert "---\n" in result
        assert result.endswith("\n")

    def test_combine_both_empty(self):
        """둘 다 빈 경우"""
        frontmatter = {}
        markdown = ""
        combiner = MarkdownFileCombiner()

        result = combiner.combine_frontmatter_and_markdown(frontmatter, markdown)

        assert result == ""

    def test_combine_unicode_characters(self):
        """유니코드 문자 처리 (한글 등)"""
        frontmatter = {"title": "테스트 글", "author": "홍길동"}
        markdown = "# 테스트 글\n\n이것은 테스트입니다."
        combiner = MarkdownFileCombiner()

        result = combiner.combine_frontmatter_and_markdown(frontmatter, markdown)

        assert "테스트 글" in result
        assert "홍길동" in result
        assert "이것은 테스트입니다." in result

    def test_combine_complex_frontmatter(self):
        """복잡한 frontmatter 구조 처리"""
        frontmatter = {
            "title": "Complex Article",
            "tags": ["python", "cli", "tool"],
            "published": "2024-01-15",
            "author": ["John Doe", "Jane Smith"],
            "custom": {
                "nested": "value",
                "list": [1, 2, 3],
            },
        }
        markdown = "# Complex Article\n\nContent..."
        combiner = MarkdownFileCombiner()

        result = combiner.combine_frontmatter_and_markdown(frontmatter, markdown)

        assert "title: Complex Article" in result
        assert "python" in result
        assert "nested: value" in result
        assert "# Complex Article" in result

    def test_combine_multiline_markdown(self):
        """여러 줄의 마크다운 처리"""
        frontmatter = {"title": "Test"}
        markdown = """# Test Article

## Section 1

Content here...

## Section 2

More content...

### Subsection

Details...
"""
        combiner = MarkdownFileCombiner()

        result = combiner.combine_frontmatter_and_markdown(frontmatter, markdown)

        assert "# Test Article" in result
        assert "## Section 1" in result
        assert "## Section 2" in result
        assert "### Subsection" in result
        assert "Details..." in result
