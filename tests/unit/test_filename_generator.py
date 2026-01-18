"""
FilenameGenerator 단위 테스트

파일명 생성 및 정규화를 테스트합니다.
"""

from src.domain.filename_generator import FilenameGenerator


class TestFilenameGenerator:
    """FilenameGenerator 테스트"""

    def test_generate_filename_from_title(self):
        """제목에서 파일명 생성"""
        generator = FilenameGenerator()

        result = generator.generate_filename("Test Article")

        assert result == "Test Article"

    def test_generate_filename_with_custom(self):
        """사용자 지정 파일명 사용"""
        generator = FilenameGenerator()

        result = generator.generate_filename("Test Article", "custom-name")

        assert result == "custom-name"

    def test_normalize_invalid_chars(self):
        """허용되지 않는 문자 정규화"""
        generator = FilenameGenerator()

        # / \ : * ? " < > | → _
        assert generator.generate_filename("Test/Article") == "Test_Article"
        assert generator.generate_filename("Test\\Article") == "Test_Article"
        assert generator.generate_filename("Test:Article") == "Test_Article"
        assert generator.generate_filename("Test*Article") == "Test_Article"
        assert generator.generate_filename("Test?Article") == "Test_Article"
        assert generator.generate_filename('Test"Article"') == "Test_Article"
        assert generator.generate_filename("Test<Article>") == "Test_Article"
        assert generator.generate_filename("Test|Article") == "Test_Article"

    def test_normalize_consecutive_underscores(self):
        """연속된 언더스코어 축소"""
        generator = FilenameGenerator()

        assert generator.generate_filename("Test__Article") == "Test_Article"
        assert generator.generate_filename("Test___Article") == "Test_Article"
        assert generator.generate_filename("Test:_*Article") == "Test_Article"

    def test_normalize_leading_trailing_underscores(self):
        """선행/후행 언더스코어 제거"""
        generator = FilenameGenerator()

        assert generator.generate_filename("_Test Article_") == "Test Article"
        assert generator.generate_filename("__Test Article__") == "Test Article"
        assert generator.generate_filename("/Test Article/") == "Test Article"

    def test_normalize_leading_trailing_spaces(self):
        """선행/후행 공백 제거"""
        generator = FilenameGenerator()

        assert generator.generate_filename("  Test Article  ") == "Test Article"
        assert generator.generate_filename("\tTest Article\n") == "Test Article"

    def test_normalize_length_limit(self):
        """파일명 길이 제한"""
        generator = FilenameGenerator()

        long_title = "A" * 250
        result = generator.generate_filename(long_title)

        assert len(result) <= 200

    def test_normalize_empty_string(self):
        """빈 문자열 처리"""
        generator = FilenameGenerator()

        result = generator.generate_filename("")

        assert result == "untitled"

    def test_normalize_only_invalid_chars(self):
        """허용되지 않는 문자만 있는 경우"""
        generator = FilenameGenerator()

        result = generator.generate_filename('/:*?"<>|')

        assert result == "untitled"

    def test_normalize_unicode_characters(self):
        """유니코드 문자 처리 (한글 등)"""
        generator = FilenameGenerator()

        assert generator.generate_filename("테스트 글") == "테스트 글"
        assert generator.generate_filename("테스트: 글") == "테스트_ 글"

    def test_normalize_mixed_content(self):
        """복합 콘텐츠 정규화"""
        generator = FilenameGenerator()

        result = generator.generate_filename("  Test: Article/Title (2024)_  ")

        assert result == "Test_ Article_Title (2024)"

    def test_normalize_custom_with_invalid_chars(self):
        """사용자 지정 파일명 정규화"""
        generator = FilenameGenerator()

        result = generator.generate_filename(
            "Original Title",
            "Custom: Name/Test",
        )

        assert result == "Custom_ Name_Test"

    def test_normalize_trailing_underscore_after_cut(self):
        """길이 제한 후 후행 언더스코어 제거"""
        generator = FilenameGenerator()

        # 긴 파일명에 불법 문자가 있는 경우
        long_title = "A" * 195 + ":/"
        result = generator.generate_filename(long_title)

        assert len(result) <= 200
        assert not result.endswith("_")
