"""
애플리케이션 모델 모듈

CLI 옵션 및 애플리케이션에서 사용하는 모델을 정의합니다.
"""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class FrontmatterOptions(BaseModel):
    """
    Frontmatter 옵션 모델

    CLI 옵션으로 지정된 메타데이터를 모델링합니다.
    """

    title: str | None = Field(default=None, description="제목 직접 지정")
    author: str | None = Field(default=None, description="저자 직접 지정 (쉼표로 구분)")
    published: str | None = Field(default=None, description="게시일 직접 지정 (YYYY-MM-DD 형식)")
    description: str | None = Field(default=None, description="설명 직접 지정")
    tags: list[str] = Field(default_factory=list, description="추가할 태그 목록")

    @field_validator("published")
    @classmethod
    def validate_published_date(cls, v: str | None) -> str | None:
        """
        게시일 형식을 검증합니다.

        Args:
            v: 검증할 날짜 문자열

        Returns:
            유효한 날짜 문자열

        Raises:
            ValueError: 날짜 형식이 올바르지 않은 경우
        """
        if v is None:
            return None

        try:
            date.fromisoformat(v)
        except ValueError as e:
            raise ValueError("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.") from e

        return v
