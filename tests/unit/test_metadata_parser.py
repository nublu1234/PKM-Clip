"""
MetadataParser 단위 테스트

메타데이터 파서의 각 메서드를 테스트합니다.
"""

from datetime import date

from src.infrastructure.metadata_parser import MetadataParser


class TestParseTitle:
    """parse_title 메서드 테스트"""

    def test_h1_title_extraction(self):
        """h1 제목 추출 테스트"""
        markdown = "# Stop Drooling Over User Stories\n\nContent here..."
        parser = MetadataParser()
        assert parser.parse_title(markdown) == "Stop Drooling Over User Stories"

    def test_no_title_in_markdown(self):
        """제목이 없는 마크다운"""
        markdown = "Just some content without a title\n\nMore content..."
        parser = MetadataParser()
        assert parser.parse_title(markdown) is None

    def test_empty_markdown(self):
        """빈 마크다운"""
        parser = MetadataParser()
        assert parser.parse_title("") is None
        assert parser.parse_title(None) is None

    def test_title_with_special_chars(self):
        """특수 문자가 포함된 제목"""
        markdown = "# Hello, World! (Test) & More\n\nContent..."
        parser = MetadataParser()
        assert parser.parse_title(markdown) == "Hello, World! (Test) & More"


class TestParseAuthor:
    """parse_author 메서드 테스트"""

    def test_author_with_prefix(self):
        """Author: 접두사가 있는 저자"""
        markdown = "# Title\n\nAuthor: John Doe\n\nContent..."
        parser = MetadataParser()
        assert parser.parse_author(markdown) == ["John Doe"]

    def test_author_korean(self):
        """한국어 저자"""
        markdown = "# Title\n\n저자: 홍길동\n\nContent..."
        parser = MetadataParser()
        assert parser.parse_author(markdown) == ["홍길동"]

    def test_author_by_prefix(self):
        """By 접두사가 있는 저자"""
        markdown = "# Title\n\nBy Jane Smith\n\nContent..."
        parser = MetadataParser()
        assert parser.parse_author(markdown) == ["Jane Smith"]

    def test_multiple_authors(self):
        """여러 저자"""
        markdown = "# Title\n\nAuthor: John Doe, Jane Smith, Bob Johnson\n\nContent..."
        parser = MetadataParser()
        assert parser.parse_author(markdown) == ["John Doe", "Jane Smith", "Bob Johnson"]

    def test_no_author(self):
        """저자 정보가 없는 경우"""
        markdown = "# Title\n\nJust content without author info..."
        parser = MetadataParser()
        assert parser.parse_author(markdown) is None

    def test_empty_markdown(self):
        """빈 마크다운"""
        parser = MetadataParser()
        assert parser.parse_author("") is None
        assert parser.parse_author(None) is None


class TestParsePublishedDate:
    """parse_published_date 메서드 테스트"""

    def test_iso_date_format(self):
        """YYYY-MM-DD 형식"""
        markdown = "# Title\n\nPublished: 2024-09-24\n\nContent..."
        parser = MetadataParser()
        assert parser.parse_published_date(markdown) == date(2024, 9, 24)

    def test_slash_date_format(self):
        """YYYY/MM/DD 형식"""
        markdown = "# Title\n\nPublished: 2024/09/24\n\nContent..."
        parser = MetadataParser()
        assert parser.parse_published_date(markdown) == date(2024, 9, 24)

    def test_korean_date_format(self):
        """한국어 날짜 형식"""
        markdown = "# Title\n\n게시일: 2024년 9월 24일\n\nContent..."
        parser = MetadataParser()
        assert parser.parse_published_date(markdown) == date(2024, 9, 24)

    def test_invalid_date(self):
        """잘못된 날짜"""
        markdown = "# Title\n\nPublished: 2024-13-01\n\nContent..."
        parser = MetadataParser()
        assert parser.parse_published_date(markdown) is None

    def test_no_date(self):
        """날짜 정보가 없는 경우"""
        markdown = "# Title\n\nJust content without date..."
        parser = MetadataParser()
        assert parser.parse_published_date(markdown) is None

    def test_empty_markdown(self):
        """빈 마크다운"""
        parser = MetadataParser()
        assert parser.parse_published_date("") is None
        assert parser.parse_published_date(None) is None


class TestParseDescription:
    """parse_description 메서드 테스트"""

    def test_first_paragraph(self):
        """첫 번째 단락 추출"""
        markdown = "# Title\n\nThis is the description.\n\nMore content..."
        parser = MetadataParser()
        assert parser.parse_description(markdown) == "This is the description."

    def test_multiline_paragraph(self):
        """여러 줄로 된 첫 번째 단락"""
        markdown = (
            "# Title\n\nThis is the description\nthat spans multiple lines.\n\nMore content..."
        )
        parser = MetadataParser()
        assert (
            parser.parse_description(markdown)
            == "This is the description that spans multiple lines."
        )

    def test_long_description_truncated(self):
        """긴 설명 제한 (200자)"""
        long_text = (
            "This is a very long description that exceeds 200 character limit "
            "and should be truncated properly to maintain reasonable length "
            "for the description field in the frontmatter metadata section of the document "
            "that is being processed."
        )
        markdown = f"# Title\n\n{long_text}\n\nMore content..."
        parser = MetadataParser()
        description = parser.parse_description(markdown)
        assert description is not None
        assert len(description) == 203  # 200 chars + "..."
        assert description.endswith("...")

    def test_no_description(self):
        """설명이 없는 경우 (빈 단락만 있는 경우)"""
        markdown = "# Title\n\n\n"
        parser = MetadataParser()
        assert parser.parse_description(markdown) is None

    def test_empty_markdown(self):
        """빈 마크다운"""
        parser = MetadataParser()
        assert parser.parse_description("") is None
        assert parser.parse_description(None) is None

    def test_description_after_metadata(self):
        """메타데이터 뒤의 설명"""
        markdown = "# Title\n\nAuthor: John Doe\n\nThis is the description.\n\nMore content..."
        parser = MetadataParser()
        assert parser.parse_description(markdown) == "This is the description."


class TestExtractTitleFromUrl:
    """_extract_title_from_url 메서드 테스트"""

    def test_simple_url(self):
        """간단한 URL"""
        parser = MetadataParser()
        assert (
            parser._extract_title_from_url("https://example.com/stop-drooling-over-user-stories")
            == "Stop Drooling Over User Stories"
        )

    def test_url_with_path(self):
        """경로가 포함된 URL"""
        parser = MetadataParser()
        assert (
            parser._extract_title_from_url("https://example.com/2024/09/24/article-title")
            == "Article Title"
        )

    def test_url_with_extension(self):
        """파일 확장자가 포함된 URL"""
        parser = MetadataParser()
        assert parser._extract_title_from_url("https://example.com/page.html") == "Page"

    def test_url_with_underscores(self):
        """언더스코어가 포함된 URL"""
        parser = MetadataParser()
        assert (
            parser._extract_title_from_url("https://example.com/my_article_title")
            == "My Article Title"
        )

    def test_url_without_path(self):
        """경로가 없는 URL"""
        parser = MetadataParser()
        assert parser._extract_title_from_url("https://example.com/") is None

    def test_empty_url(self):
        """빈 URL"""
        parser = MetadataParser()
        assert parser._extract_title_from_url("") is None
        assert parser._extract_title_from_url(None) is None


class TestParseDateString:
    """_parse_date_string 메서드 테스트"""

    def test_iso_date_format(self):
        """ISO 8601 형식 (YYYY-MM-DD)"""
        parser = MetadataParser()
        assert parser._parse_date_string("2024-09-24") == date(2024, 9, 24)

    def test_slash_date_format(self):
        """슬래시 형식 (YYYY/MM/DD)"""
        parser = MetadataParser()
        assert parser._parse_date_string("2024/09/24") == date(2024, 9, 24)

    def test_iso_with_time(self):
        """ISO 8601 형식 + 시간 (YYYY-MM-DDTHH:MM:SSZ)"""
        parser = MetadataParser()
        assert parser._parse_date_string("2024-09-24T14:30:00Z") == date(2024, 9, 24)

    def test_iso_with_timezone(self):
        """ISO 8601 형식 + 타임존 (YYYY-MM-DDTHH:MM:SS+09:00)"""
        parser = MetadataParser()
        assert parser._parse_date_string("2024-09-24T14:30:00+09:00") == date(2024, 9, 24)

    def test_iso_with_microseconds(self):
        """ISO 8601 형식 + 마이크로초"""
        parser = MetadataParser()
        assert parser._parse_date_string("2024-09-24T14:30:00.123Z") == date(2024, 9, 24)

    def test_invalid_date(self):
        """잘못된 날짜"""
        parser = MetadataParser()
        assert parser._parse_date_string("2024-13-01") is None
        assert parser._parse_date_string("not-a-date") is None

    def test_empty_string(self):
        """빈 문자열"""
        parser = MetadataParser()
        assert parser._parse_date_string("") is None
        assert parser._parse_date_string(None) is None


class TestExtractJinaPublishedTime:
    """_extract_jina_published_time 메서드 테스트"""

    def test_published_line(self):
        """Published: 라인"""
        markdown = "Published: 2024-09-24\n\n# Title\n\nContent..."
        parser = MetadataParser()
        assert parser._extract_jina_published_time(markdown) == date(2024, 9, 24)

    def test_published_korean_colon(self):
        """한국어 콜론 사용"""
        markdown = "Published：2024-09-24\n\n# Title\n\nContent..."
        parser = MetadataParser()
        assert parser._extract_jina_published_time(markdown) == date(2024, 9, 24)

    def test_no_published_line(self):
        """Published: 라인이 없는 경우"""
        markdown = "# Title\n\nContent..."
        parser = MetadataParser()
        assert parser._extract_jina_published_time(markdown) is None

    def test_empty_markdown(self):
        """빈 마크다운"""
        parser = MetadataParser()
        assert parser._extract_jina_published_time("") is None
        assert parser._extract_jina_published_time(None) is None


class TestExtractOpenGraphPublishedTime:
    """_extract_open_graph_published_time 메서드 테스트"""

    def test_article_published_time(self):
        """article:published_time 우선순위"""
        markdown = (
            "article:published_time: 2024-09-24T14:30:00Z\n"
            "og:published_time: 2024-01-01\n"
            "\n# Title\n\nContent..."
        )
        parser = MetadataParser()
        assert parser._extract_open_graph_published_time(markdown) == date(2024, 9, 24)

    def test_og_published_time(self):
        """og:published_time 대체"""
        markdown = "og:published_time: 2024-09-24T14:30:00Z\n\n# Title\n\nContent..."
        parser = MetadataParser()
        assert parser._extract_open_graph_published_time(markdown) == date(2024, 9, 24)

    def test_og_published_time_simple_date(self):
        """og:published_time 간단한 날짜"""
        markdown = "og:published_time: 2024-09-24\n\n# Title\n\nContent..."
        parser = MetadataParser()
        assert parser._extract_open_graph_published_time(markdown) == date(2024, 9, 24)

    def test_no_open_graph_metadata(self):
        """Open Graph 메타데이터가 없는 경우"""
        markdown = "# Title\n\nContent..."
        parser = MetadataParser()
        assert parser._extract_open_graph_published_time(markdown) is None

    def test_empty_markdown(self):
        """빈 마크다운"""
        parser = MetadataParser()
        assert parser._extract_open_graph_published_time("") is None
        assert parser._extract_open_graph_published_time(None) is None


class TestExtractSchemaOrgDatePublished:
    """_extract_schema_org_date_published 메서드 테스트"""

    def test_simple_json_ld(self):
        """간단한 JSON-LD 블록"""
        markdown = (
            '<script type="application/ld+json">\n'
            "{\n"
            '  "@context": "https://schema.org",\n'
            '  "@type": "Article",\n'
            '  "datePublished": "2024-09-24"\n'
            "}\n"
            "</script>\n\n"
            "# Title\n\nContent..."
        )
        parser = MetadataParser()
        assert parser._extract_schema_org_date_published(markdown) == date(2024, 9, 24)

    def test_nested_json_ld(self):
        """중첩된 JSON-LD 구조"""
        markdown = (
            '<script type="application/ld+json">\n'
            "{\n"
            '  "@context": "https://schema.org",\n'
            '  "@type": "Blog",\n'
            '  "blogPost": {\n'
            '    "@type": "Article",\n'
            '    "datePublished": "2024-09-24"\n'
            "  }\n"
            "}\n"
            "</script>\n\n"
            "# Title\n\nContent..."
        )
        parser = MetadataParser()
        assert parser._extract_schema_org_date_published(markdown) == date(2024, 9, 24)

    def test_json_ld_with_time(self):
        """시간이 포함된 JSON-LD"""
        markdown = (
            '<script type="application/ld+json">\n'
            "{\n"
            '  "@context": "https://schema.org",\n'
            '  "@type": "Article",\n'
            '  "datePublished": "2024-09-24T14:30:00Z"\n'
            "}\n"
            "</script>\n\n"
            "# Title\n\nContent..."
        )
        parser = MetadataParser()
        assert parser._extract_schema_org_date_published(markdown) == date(2024, 9, 24)

    def test_invalid_json(self):
        """잘못된 JSON"""
        markdown = (
            '<script type="application/ld+json">\n'
            "{\n"
            '  "datePublished": "2024-09-24"\n'
            "</script>\n\n"
            "# Title\n\nContent..."
        )
        parser = MetadataParser()
        assert parser._extract_schema_org_date_published(markdown) is None

    def test_no_json_ld(self):
        """JSON-LD 블록이 없는 경우"""
        markdown = "# Title\n\nContent..."
        parser = MetadataParser()
        assert parser._extract_schema_org_date_published(markdown) is None

    def test_empty_markdown(self):
        """빈 마크다운"""
        parser = MetadataParser()
        assert parser._extract_schema_org_date_published("") is None
        assert parser._extract_schema_org_date_published(None) is None


class TestExtractHtmlMetaDate:
    """_extract_html_meta_date 메서드 테스트"""

    def test_meta_date_tag(self):
        """meta name="date" 태그"""
        markdown = '<meta name="date" content="2024-09-24" />\n\n# Title\n\nContent...'
        parser = MetadataParser()
        assert parser._extract_html_meta_date(markdown) == date(2024, 9, 24)

    def test_meta_date_reversed_order(self):
        """속성 순서가 반대인 경우"""
        markdown = '<meta content="2024-09-24" name="date" />\n\n# Title\n\nContent...'
        parser = MetadataParser()
        assert parser._extract_html_meta_date(markdown) == date(2024, 9, 24)

    def test_meta_date_with_time(self):
        """시간이 포함된 meta 태그"""
        markdown = '<meta name="date" content="2024-09-24T14:30:00Z" />\n\n# Title\n\nContent...'
        parser = MetadataParser()
        assert parser._extract_html_meta_date(markdown) == date(2024, 9, 24)

    def test_no_meta_date_tag(self):
        """meta date 태그가 없는 경우"""
        markdown = "# Title\n\nContent..."
        parser = MetadataParser()
        assert parser._extract_html_meta_date(markdown) is None

    def test_empty_markdown(self):
        """빈 마크다운"""
        parser = MetadataParser()
        assert parser._extract_html_meta_date("") is None
        assert parser._extract_html_meta_date(None) is None


class TestExtractDateFromUrl:
    """_extract_date_from_url 메서드 테스트"""

    def test_url_date_pattern(self):
        """URL 경로에 날짜 패턴이 있는 경우"""
        parser = MetadataParser()
        assert parser._extract_date_from_url(
            "https://example.com/2024/09/24/article-title"
        ) == date(2024, 9, 24)

    def test_url_date_pattern_with_subdirs(self):
        """하위 디렉토리가 있는 URL"""
        parser = MetadataParser()
        assert parser._extract_date_from_url(
            "https://example.com/archives/2024/09/24/article-title"
        ) == date(2024, 9, 24)

    def test_url_no_date_pattern(self):
        """날짜 패턴이 없는 URL"""
        parser = MetadataParser()
        assert parser._extract_date_from_url("https://example.com/article-title") is None

    def test_url_invalid_date(self):
        """잘못된 날짜가 있는 URL"""
        parser = MetadataParser()
        assert parser._extract_date_from_url("https://example.com/2024/13/01/article-title") is None

    def test_empty_url(self):
        """빈 URL"""
        parser = MetadataParser()
        assert parser._extract_date_from_url("") is None
        assert parser._extract_date_from_url(None) is None


class TestExtractPublishedDate:
    """extract_published_date 메서드 테스트 (전체 파이프라인)"""

    def test_priority_jina_first(self):
        """jina.ai published time 우선순위"""
        markdown = "Published: 2024-09-24\nog:published_time: 2024-01-01\n\n# Title\n\nContent..."
        parser = MetadataParser()
        assert parser.extract_published_date(markdown, "https://example.com/article") == date(
            2024, 9, 24
        )

    def test_priority_og_second(self):
        """Open Graph 두 번째 우선순위"""
        markdown = "og:published_time: 2024-09-24\n\n# Title\n\nContent..."
        parser = MetadataParser()
        assert parser.extract_published_date(markdown, "https://example.com/article") == date(
            2024, 9, 24
        )

    def test_priority_schema_third(self):
        """Schema.org 세 번째 우선순위"""
        markdown = (
            '<script type="application/ld+json">\n'
            "{\n"
            '  "datePublished": "2024-09-24"\n'
            "}\n"
            "</script>\n\n"
            "# Title\n\nContent..."
        )
        parser = MetadataParser()
        assert parser.extract_published_date(markdown, "https://example.com/article") == date(
            2024, 9, 24
        )

    def test_priority_html_meta_fourth(self):
        """HTML meta 태그 네 번째 우선순위"""
        markdown = '<meta name="date" content="2024-09-24" />\n\n# Title\n\nContent...'
        parser = MetadataParser()
        assert parser.extract_published_date(markdown, "https://example.com/article") == date(
            2024, 9, 24
        )

    def test_priority_url_fifth(self):
        """URL 경로 패턴 다섯 번째 우선순위"""
        markdown = "# Title\n\nContent..."
        url = "https://example.com/2024/09/24/article-title"
        parser = MetadataParser()
        assert parser.extract_published_date(markdown, url) == date(2024, 9, 24)

    def test_all_strategies_fail(self):
        """모든 전략 실패"""
        markdown = "# Title\n\nContent..."
        url = "https://example.com/article"
        parser = MetadataParser()
        assert parser.extract_published_date(markdown, url) is None

    def test_empty_inputs(self):
        """빈 입력"""
        parser = MetadataParser()
        assert parser.extract_published_date("", "") is None
        assert parser.extract_published_date(None, None) is None
        assert parser.extract_published_date("# Title", "") is None
        assert parser.extract_published_date("# Title", None) is None
