"""
FrontmatterOptions 단위 테스트

CLI 옵션 모델의 유효성을 테스트합니다.
"""

import pytest
from pydantic import ValidationError

from src.application.models import FrontmatterOptions


class TestFrontmatterOptionsValidation:
    """FrontmatterOptions 유효성 검증 테스트"""

    def test_empty_options(self):
        """빈 옵션"""
        options = FrontmatterOptions()
        assert options.title is None
        assert options.author is None
        assert options.published is None
        assert options.description is None
        assert options.tags == []

    def test_valid_date_format(self):
        """유효한 날짜 형식 (YYYY-MM-DD)"""
        options = FrontmatterOptions(published="2024-09-24")
        assert options.published == "2024-09-24"

    def test_invalid_date_format(self):
        """잘못된 날짜 형식"""
        with pytest.raises(ValidationError) as exc_info:
            FrontmatterOptions(published="September 24, 2024")

        error_messages = [error["msg"] for error in exc_info.value.errors()]
        assert any("날짜 형식이 올바르지 않습니다" in msg for msg in error_messages)

    def test_invalid_date_value(self):
        """잘못된 날짜 값"""
        with pytest.raises(ValidationError) as exc_info:
            FrontmatterOptions(published="2024-13-01")

        error_messages = [error["msg"] for error in exc_info.value.errors()]
        assert any("날짜 형식이 올바르지 않습니다" in msg for msg in error_messages)

    def test_none_date(self):
        """날짜가 None인 경우"""
        options = FrontmatterOptions(published=None)
        assert options.published is None

    def test_tags_empty_list(self):
        """빈 태그 리스트"""
        options = FrontmatterOptions()
        assert options.tags == []

    def test_tags_with_values(self):
        """태그 값이 있는 경우"""
        options = FrontmatterOptions(tags=["python", "tutorial"])
        assert options.tags == ["python", "tutorial"]

    def test_title_with_value(self):
        """제목 값이 있는 경우"""
        options = FrontmatterOptions(title="Custom Title")
        assert options.title == "Custom Title"

    def test_author_with_value(self):
        """저자 값이 있는 경우"""
        options = FrontmatterOptions(author="John Doe")
        assert options.author == "John Doe"

    def test_description_with_value(self):
        """설명 값이 있는 경우"""
        options = FrontmatterOptions(description="Article description")
        assert options.description == "Article description"

    def test_all_fields_populated(self):
        """모든 필드가 채워진 경우"""
        options = FrontmatterOptions(
            title="Article Title",
            author="John Doe",
            published="2024-09-24",
            description="Article description",
            tags=["python", "tutorial"],
        )
        assert options.title == "Article Title"
        assert options.author == "John Doe"
        assert options.published == "2024-09-24"
        assert options.description == "Article description"
        assert options.tags == ["python", "tutorial"]
